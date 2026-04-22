#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Tool that validates the JSON-LD in the examples against the generated SHACL schema.
This replaces the legacy Ruby validation tests.
"""

import argparse
import logging
import os
import sys
from pathlib import Path
import rdflib
import pyshacl

if str(Path.cwd()) not in sys.path:
    sys.path.insert(1, str(Path.cwd()))

import software.SchemaExamples.schemaexamples as schemaexamples
import software.util.schemaversion as schemaversion

log: logging.Logger = logging.getLogger(__name__)

def load_examples() -> list:
    """Finds and loads all examples."""
    schemaexamples.SchemaExamples.loadExamplesFiles("default")
    log.info(f"Loaded {schemaexamples.SchemaExamples.count()} examples, processing JSON-LD variants")

    examples = [ex for ex in schemaexamples.SchemaExamples.allExamples(sort=True) if ex.hasJsonld()]
    return examples


def validate_examples(examples: list, invalid_only: bool, source_output: bool) -> None:
    """Validates the provided examples against the generated SHACL shapes."""
    version: str = schemaversion.getVersion()
    shacl_file: Path = Path.cwd() / "software" / "site" / "releases" / version / "schemaorg-shapes.shacl"
    subclass_file: Path = Path.cwd() / "software" / "site" / "releases" / version / "schemaorg-subclasses.shacl"

    if not shacl_file.exists() or not subclass_file.exists():
        log.error(f"SHACL files not found at {shacl_file} or {subclass_file} – check site build")
        sys.exit(os.EX_CONFIG)

    log.info("Loading SHACL shapes and subclass graphs...")
    shacl_graph: rdflib.Graph = rdflib.Graph()
    shacl_graph.parse(source=str(shacl_file), format="turtle")

    ont_graph: rdflib.Graph = rdflib.Graph()
    ont_graph.parse(source=str(subclass_file), format="turtle")

    count: int = 0
    error_count: int = 0

    for ex in examples:
        count += 1
        name = ex.getKey()

        if not invalid_only:
            log.info(f"Validating example {name}")

        try:
            data_graph: rdflib.Graph = rdflib.Graph()
            data_graph.parse(data=ex.getJsonldRaw(), format="json-ld")

            conforms, results_graph, results_text = pyshacl.validate(
                data_graph,
                shacl_graph=shacl_graph,
                ont_graph=ont_graph,
                inference="rdfs",
                abort_on_first=False,
                max_validation_depth=200
            )

            if not conforms:
                error_count += 1
                log.error(f"Validation failed for example {name}:\n{results_text}")
                if source_output:
                    source = "\n".join([f"{i:4d}: {x.rstrip()}" for i, x in enumerate(ex.getJsonldRaw().splitlines(), start=1)])
                    log.info(f"Source:\n{source}")
        except Exception as exception:
            error_count += 1
            log.error(f"Invalid JSON example {name}: {exception}")
            if source_output:
                source = "\n".join([f"{i:4d}: {x.rstrip()}" for i, x in enumerate(ex.getJsonldRaw().splitlines(), start=1)])
                log.info(f"Source:\n{source}")

    log.info(f"Done: Processed {count} examples")
    if error_count:
        log.error(f"Found {error_count} invalid examples")
        sys.exit(1)
    else:
        log.info("All examples validated successfully.")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-i", "--invalidonly", default=False, action="store_true", help="Only report invalid examples")
    parser.add_argument("-s", "--sourceoutput", default=False, action="store_true", help="Output invalid example source")
    args = parser.parse_args()

    examples = load_examples()
    validate_examples(examples=examples, invalid_only=args.invalidonly, source_output=args.sourceoutput)
