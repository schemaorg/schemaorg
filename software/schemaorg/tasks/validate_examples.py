"""Floating task that validates JSON-LD examples against generated SHACL shapes."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
import logging
from typing import NamedTuple, Protocol

import owlrl  # type: ignore[import-untyped]
import pyshacl
import rdflib
from rdflib.namespace import RDF, SH

from schemaorg.layout import Domain, OutputLayout, Releases
from schemaorg.progress import ProgressReporter
from schemaorg.version import VersionItem


class ValidatableExample(Protocol):
    """Structural interface needed to validate one JSON-LD example."""

    def getKey(self) -> str: ...

    def getJsonldRaw(self) -> str: ...


class ShaclConfigError(ValueError):
    """Raised when SHACL inputs or gates are missing or degenerate."""


class ExampleResult(NamedTuple):
    """Outcome of validating one example."""

    example: ValidatableExample
    targeted: bool
    conforms: bool
    report: str | None
    error: str | None

    @property
    def name(self) -> str:
        return self.example.getKey()


@dataclass(frozen=True)
class ValidationSummary:
    """Structured result returned by ValidateExamplesTask."""

    total_count: int
    targeted_count: int
    error_count: int
    failures: tuple[ExampleResult, ...]


class ExampleValidator:
    """Validates examples against one fixed set of SHACL shapes."""

    def __init__(
        self, shacl_graph: rdflib.Graph, ont_graph: rdflib.Graph
    ) -> None:
        self.shacl_graph: rdflib.Graph = shacl_graph
        self.ont_graph: rdflib.Graph = ont_graph

        # Closed once so validate() can run with inference="none".
        owlrl.DeductiveClosure(owlrl.RDFS_Semantics).expand(self.ont_graph)

        self.target_classes: frozenset[str] = frozenset(
            str(t) for t in self.shacl_graph.objects(None, SH.targetClass)
        )
        if not self.target_classes:
            raise ValueError(
                "the shapes declare no sh:targetClass, so they can never "
                "select a focus node. Regenerate the shapes."
            )

    def validate(self, example: ValidatableExample) -> ExampleResult:
        """Validate one example's JSON-LD against the shapes without raising."""
        try:
            data_graph = rdflib.Graph()
            data_graph.parse(data=example.getJsonldRaw(), format="json-ld")

            declared_types = {
                str(t) for t in data_graph.objects(None, RDF.type)
            }
            targeted = bool(declared_types & self.target_classes)

            conforms, _, report = pyshacl.validate(
                data_graph,
                shacl_graph=self.shacl_graph,
                ont_graph=self.ont_graph,
                inference="none",
                abort_on_first=False,
                max_validation_depth=200,
            )

            return ExampleResult(
                example=example,
                targeted=targeted,
                conforms=bool(conforms),
                report=None if conforms else str(report),
                error=None,
            )
        except Exception as exception:  # noqa: BLE001 - reported, not swallowed
            return ExampleResult(
                example=example,
                targeted=False,
                conforms=False,
                report=None,
                error=str(exception),
            )


def format_numbered_source(raw_jsonld: str) -> str:
    return "\n".join(
        f"{i:4d}: {line.rstrip()}"
        for i, line in enumerate(raw_jsonld.splitlines(), start=1)
    )


@dataclass(frozen=True)
class ValidateExamplesTask:
    """Validates JSON-LD examples against release SHACL shapes via ProgressReporter."""

    releases: Releases
    version: VersionItem
    examples: Sequence[ValidatableExample]
    invalid_only: bool
    source_output: bool
    progress: ProgressReporter

    def run(self) -> ValidationSummary:
        if not self.examples:
            raise ShaclConfigError("No JSON-LD examples found to validate.")

        version = self.releases.resolve(self.version)
        if isinstance(self.releases.layout, OutputLayout):
            release_dir = (
                self.releases.layout.output_dir
                / Domain.RELEASE.value
                / version.number()
            )
            if not release_dir.is_dir():
                raise ShaclConfigError(
                    f"SHACL files not found in {release_dir} – check site build"
                )

        shacl_file = self.releases.file(
            version, protocol="", scope="shapes", extension=".shacl"
        )
        subclass_file = self.releases.file(
            version, protocol="", scope="subclasses", extension=".shacl"
        )
        if not shacl_file.is_file() or not subclass_file.is_file():
            raise ShaclConfigError(
                f"SHACL files not found at {shacl_file} or {subclass_file} – check site build"
            )

        with self.progress.task(
            f"Validating {len(self.examples)} JSON-LD examples",
            total=len(self.examples),
            unit="examples",
        ) as p:
            p.step("loading SHACL shapes")
            shacl_graph = rdflib.Graph()
            shacl_graph.parse(shacl_file, format="turtle")

            ont_graph = rdflib.Graph()
            ont_graph.parse(subclass_file, format="turtle")

            try:
                engine = ExampleValidator(
                    shacl_graph=shacl_graph, ont_graph=ont_graph
                )
            except ValueError as exc:
                raise ShaclConfigError(f"SHACL gate is dead: {exc}") from exc

            targeted_count = 0
            failures: list[ExampleResult] = []

            for example in self.examples:
                if not self.invalid_only:
                    p.step(example.getKey())
                result = engine.validate(example)
                if result.targeted:
                    targeted_count += 1

                failed = result.error is not None or not result.conforms
                if result.error is not None:
                    failures.append(result)
                    p.log(
                        f"Invalid JSON example {result.name}: {result.error}",
                        logging.ERROR,
                    )
                elif not result.conforms:
                    failures.append(result)
                    p.log(
                        f"Validation failed for example {result.name}:\n{result.report}",
                        logging.ERROR,
                    )
                if self.source_output and failed:
                    p.log(
                        f"Source:\n{format_numbered_source(result.example.getJsonldRaw())}",
                        logging.INFO,
                    )
                p.advance(1)

        if not targeted_count and not failures:
            raise ShaclConfigError(
                f"SHACL gate inspected none of the {len(self.examples)} examples: "
                "no example declares a type that any shape targets."
            )

        return ValidationSummary(
            total_count=len(self.examples),
            targeted_count=targeted_count,
            error_count=len(failures),
            failures=tuple(failures),
        )
