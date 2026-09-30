#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tool that validates the JSON-LD in the examples against the generated SHACL schema.
This replaces the legacy Ruby validation tests.
"""

import argparse
import concurrent.futures
import logging
import os
from pathlib import Path
import sys
from typing import FrozenSet, List, NamedTuple, Optional

import owlrl
import pyshacl
import rdflib
from rdflib.namespace import RDF, SH

import SchemaExamples.schemaexamples as schemaexamples
import util.paths as paths
import util.schema as schema


log: logging.Logger = logging.getLogger(__name__)


def load_examples() -> list:
    """Finds and loads all examples."""
    schemaexamples.SchemaExamples.loadExamplesFiles("default")
    log.info(f"Loaded {schemaexamples.SchemaExamples.count()} examples, processing JSON-LD variants")

    examples = [ex for ex in schemaexamples.SchemaExamples.allExamples(sort=True) if ex.hasJsonld()]
    return examples


class ExampleResult(NamedTuple):
    """Outcome of validating one example."""

    example: schemaexamples.Example
    #: A shape targeted a declared type. Untargeted means uninspected, not valid.
    targeted: bool
    conforms: bool
    #: SHACL report, failures only.
    report: Optional[str]
    #: Not validatable at all, e.g. bad JSON. Distinct from conforms=False.
    error: Optional[str]

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

        self.target_classes: FrozenSet[str] = frozenset(
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
        log.info(f"Validating {self.total} examples")

    def add(self, result: ExampleResult) -> None:
        """Record one result and log whatever it warrants."""
        self.count += 1
        if not self.invalid_only:
            log.info(f"Validating example {result.name}")

        if result.targeted:
            self.targeted_count += 1

        if result.error is not None:
            self.error_count += 1
            log.error(f"Invalid JSON example {result.name}: {result.error}")
        elif not result.conforms:
            self.error_count += 1
            log.error(
                f"Validation failed for example {result.name}:\n{result.report}"
            )

        if self.source_output:
            source = "\n".join(
                f"{i:4d}: {line.rstrip()}"
                for i, line in enumerate(
                    result.example.getJsonldRaw().splitlines(), start=1
                )
            )
            log.info(f"Source:\n{source}")

    def done(self) -> None:
        log.info(
            f"Done: Processed {self.count} examples, "
            f"{self.targeted_count} of which matched at least one shape"
        )


def validate_examples(examples: list, invalid_only: bool, source_output: bool) -> None:
    """Validates the provided examples against the generated SHACL shapes."""
    version: str = schema.getVersion()

    shacl_file: Path = paths.DefaultOutputLayout().domain_file(paths.Domain.RELEASE, "schemaorg-shapes.shacl")
    subclass_file: Path = paths.DefaultOutputLayout().domain_file(paths.Domain.RELEASE, "schemaorg-subclasses.shacl")

    if not shacl_file.exists() or not subclass_file.exists():
        log.error(f"SHACL files not found at {shacl_file} or {subclass_file} – check site build")
        sys.exit(os.EX_CONFIG)

    log.info("Loading SHACL shapes and subclass graphs...")
    shacl_graph: rdflib.Graph = rdflib.Graph()
    shacl_graph.parse(source=str(shacl_file), format="turtle")

    ont_graph: rdflib.Graph = rdflib.Graph()
    ont_graph.parse(source=str(subclass_file), format="turtle")

    # The constructor RDFS-closes ont_graph in place.
    before: int = len(ont_graph)
    try:
        engine = ExampleValidator(shacl_graph=shacl_graph, ont_graph=ont_graph)
    except ValueError as exception:
        log.error(f"SHACL gate is dead: {exception}")
        sys.exit(os.EX_CONFIG)

    log.info(f"Subclass ontology RDFS-closed: {before} -> {len(ont_graph)} triples")
    log.info(f"Shapes declare {len(engine.target_classes)} target classes")

    stats = ValidationStats(
        total=len(examples), invalid_only=invalid_only, source_output=source_output
    )

    with concurrent.futures.ProcessPoolExecutor() as pool:
        # chunksize: the engine is pickled per chunk, not per example.
        for result in pool.map(engine.validate, examples, chunksize=16):
            stats.add(result)
    stats.done()

    if stats.error_count:
        log.error(f"Found {stats.error_count} invalid examples")
        sys.exit(1)

    if stats.count and not stats.targeted_count:
        log.error(
            f"SHACL gate inspected none of the {stats.count} examples: no example "
            "declares a type that any shape targets."
        )
        sys.exit(os.EX_CONFIG)

    log.info("All examples validated successfully.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-i", "--invalidonly", default=False, action="store_true", help="Only report invalid examples")
    parser.add_argument("-s", "--sourceoutput", default=False, action="store_true", help="Output invalid example source")
    parser.add_argument("-o", "--output", help="Output site directory")
    args = parser.parse_args()

    if args.output:
        schema.config.OUTPUTDIR = args.output

    examples = load_examples()
    validate_examples(
        examples=examples,
        invalid_only=args.invalidonly,
        source_output=args.sourceoutput,
    )
