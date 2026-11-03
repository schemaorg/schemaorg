#!/usr/bin/env python3
"""Validate JSON-LD examples against the generated SHACL schema."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import concurrent.futures
import logging
import os
from pathlib import Path
import sys
from typing import NamedTuple

import owlrl
import pyshacl
import rdflib
from rdflib.namespace import RDF, SH

from schemaorg.layout import Releases
import SchemaExamples.schemaexamples as schemaexamples
import util.paths as paths
import util.schema as schema

log: logging.Logger = logging.getLogger(__name__)


def load_examples() -> list[schemaexamples.Example]:
    """Find and load all JSON-LD examples."""
    loaded = schemaexamples.SchemaExamples.from_default()
    log.info("Loaded %d examples, processing JSON-LD variants", len(loaded))
    return [ex for ex in loaded.allExamples() if ex.hasJsonld()]


class ExampleResult(NamedTuple):
    """Outcome of validating one example."""

    example: schemaexamples.Example
    #: A shape targeted a declared type. Untargeted means uninspected, not valid.
    targeted: bool
    conforms: bool
    #: SHACL report, failures only.
    report: str | None
    #: Not validatable at all, e.g. bad JSON. Distinct from conforms=False.
    error: str | None

    @property
    def name(self) -> str:
        return self.example.getKey()


class ExampleValidator:
    """Validates examples against one fixed set of SHACL shapes."""

    def __init__(self, shacl_graph: rdflib.Graph, ont_graph: rdflib.Graph) -> None:
        """Prepare the graphs once.

        Args:
            shacl_graph: generated shapes.
            ont_graph: subclass ontology. RDFS-closed in place.

        Raises:
            ValueError: if the shapes declare no sh:targetClass.
        """
        self.shacl_graph = shacl_graph
        self.ont_graph = ont_graph

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

    def validate(self, example: schemaexamples.Example) -> ExampleResult:
        """Validate one example's JSON-LD against the shapes.

        Never raises: parse and validation failures are reported in the
        result's `error` field.
        """
        try:
            data_graph = rdflib.Graph()
            data_graph.parse(data=example.getJsonldRaw(), format="json-ld")

            declared_types = {str(t) for t in data_graph.objects(None, RDF.type)}
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
                report=None if conforms else report,
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


class ValidationStats:
    """Counts validation outcomes and logs them as they arrive."""

    def __init__(self, total: int, invalid_only: bool, source_output: bool) -> None:
        self.total = total
        self.invalid_only = invalid_only
        self.source_output = source_output
        self.count: int = 0
        self.error_count: int = 0
        self.targeted_count: int = 0
        log.info("Validating %d examples", self.total)

    def add(self, result: ExampleResult) -> None:
        """Record one result and log whatever it warrants."""
        self.count += 1
        if not self.invalid_only:
            log.info("Validating example %s", result.name)

        if result.targeted:
            self.targeted_count += 1

        failed = result.error is not None or not result.conforms
        if result.error is not None:
            self.error_count += 1
            log.error("Invalid JSON example %s: %s", result.name, result.error)
        elif not result.conforms:
            self.error_count += 1
            log.error(
                "Validation failed for example %s:\n%s",
                result.name,
                result.report,
            )

        if self.source_output and failed:
            source = "\n".join(
                f"{i:4d}: {line.rstrip()}"
                for i, line in enumerate(
                    result.example.getJsonldRaw().splitlines(), start=1
                )
            )
            log.info("Source:\n%s", source)

    def done(self) -> None:
        log.info(
            "Done: Processed %d examples, %d of which matched at least one shape",
            self.count,
            self.targeted_count,
        )


def validate_examples(
    examples: Sequence[schemaexamples.Example],
    invalid_only: bool,
    source_output: bool,
) -> None:
    """Validate the provided examples against the generated SHACL shapes."""
    if not examples:
        log.error("No JSON-LD examples found to validate.")
        sys.exit(os.EX_CONFIG)

    releases = Releases(paths.DefaultOutputLayout(), schema.VERSION)
    shacl_file = releases.file(protocol="", scope="shapes", extension=".shacl")
    subclass_file = releases.file(
        protocol="", scope="subclasses", extension=".shacl"
    )

    if not shacl_file.exists() or not subclass_file.exists():
        log.error(
            "SHACL files not found at %s or %s – check site build",
            shacl_file,
            subclass_file,
        )
        sys.exit(os.EX_CONFIG)

    log.info("Loading SHACL shapes and subclass graphs...")
    shacl_graph = rdflib.Graph()
    shacl_graph.parse(shacl_file, format="turtle")

    ont_graph = rdflib.Graph()
    ont_graph.parse(subclass_file, format="turtle")

    # The constructor RDFS-closes ont_graph in place.
    before = len(ont_graph)
    try:
        engine = ExampleValidator(shacl_graph=shacl_graph, ont_graph=ont_graph)
    except ValueError as exception:
        log.error("SHACL gate is dead: %s", exception)
        sys.exit(os.EX_CONFIG)

    log.info("Subclass ontology RDFS-closed: %d -> %d triples", before, len(ont_graph))
    log.info("Shapes declare %d target classes", len(engine.target_classes))

    stats = ValidationStats(
        total=len(examples), invalid_only=invalid_only, source_output=source_output
    )

    with concurrent.futures.ProcessPoolExecutor() as pool:
        # chunksize: the engine is pickled per chunk, not per example.
        for result in pool.map(engine.validate, examples, chunksize=16):
            stats.add(result)
    stats.done()

    if stats.error_count:
        log.error("Found %d invalid examples", stats.error_count)
        sys.exit(1)

    if not stats.targeted_count:
        log.error(
            "SHACL gate inspected none of the %d examples: no example "
            "declares a type that any shape targets.",
            stats.count,
        )
        sys.exit(os.EX_CONFIG)

    log.info("All examples validated successfully.")


def main(argv: Sequence[str] | None = None) -> None:
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-i",
        "--invalidonly",
        action="store_true",
        help="Only report invalid examples",
    )
    parser.add_argument(
        "-s",
        "--sourceoutput",
        action="store_true",
        help="Output invalid example source",
    )
    parser.add_argument("-o", "--output", help="Output site directory")
    args = parser.parse_args(argv)

    if args.output:
        schema.config.OUTPUTDIR = args.output

    examples = load_examples()
    validate_examples(
        examples=examples,
        invalid_only=args.invalidonly,
        source_output=args.sourceoutput,
    )


if __name__ == "__main__":
    main()
