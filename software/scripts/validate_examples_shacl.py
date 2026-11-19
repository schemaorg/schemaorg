#!/usr/bin/env python3
"""Validate JSON-LD examples against the generated SHACL schema."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import logging
import os
from pathlib import Path
import sys

from schemaorg.layout import NEXT_VERSION, OutputLayout, Releases
from schemaorg.layout.releases import VersionRef
from schemaorg.progress import LogProgressReporter
from schemaorg.tasks.validate_examples import (
    ExampleResult,
    ExampleValidator,
    ShaclConfigError,
    ValidatableExample,
    ValidateExamplesTask,
    format_numbered_source,
)
import SchemaExamples.schemaexamples as schemaexamples
import util.paths as paths
import util.schema as schema

log: logging.Logger = logging.getLogger(__name__)


def load_examples() -> list[schemaexamples.Example]:
    """Find and load all JSON-LD examples."""
    loaded = schemaexamples.SchemaExamples.from_layout(
        paths.DefaultInputLayout()
    )
    log.info("Loaded %d examples, processing JSON-LD variants", len(loaded))
    return [ex for ex in loaded.allExamples() if ex.hasJsonld()]


class ValidationStats:
    """Compatibility accumulator logging example validation outcomes."""

    def __init__(
        self, total: int, invalid_only: bool, source_output: bool
    ) -> None:
        self.total = total
        self.invalid_only = invalid_only
        self.source_output = source_output
        self.count: int = 0
        self.error_count: int = 0
        self.targeted_count: int = 0
        log.info("Validating %d examples", self.total)

    def add(self, result: ExampleResult) -> None:
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
            log.info(
                "Source:\n%s",
                format_numbered_source(result.example.getJsonldRaw()),
            )


def validate_examples(
    examples: Sequence[ValidatableExample],
    invalid_only: bool,
    source_output: bool,
    releases: Releases | None = None,
    version: VersionRef = NEXT_VERSION,
) -> None:
    """Validate examples via ValidateExamplesTask and map failures to exit codes."""
    rel = releases or Releases(paths.DefaultInputLayout(), schema.VERSION)
    resolved = rel.resolve(version)
    reporter = LogProgressReporter(logger=log, log_steps=not invalid_only)
    try:
        summary = ValidateExamplesTask(
            releases=rel,
            version=resolved,
            examples=examples,
            invalid_only=invalid_only,
            source_output=source_output,
            progress=reporter,
        ).run()
    except ShaclConfigError as exc:
        log.error("%s", exc)
        sys.exit(os.EX_CONFIG)

    if summary.error_count:
        log.error("Found %d invalid examples", summary.error_count)
        sys.exit(1)
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
    parser.add_argument(
        "-o",
        "--output",
        help="Optional output root containing releases/ (defaults to checked-in data/releases/)",
    )
    parser.add_argument(
        "--version",
        default=NEXT_VERSION,
        help="Release version whose shapes to validate against (default: 'next')",
    )
    args = parser.parse_args(argv)

    layout = (
        OutputLayout(Path(args.output))
        if args.output
        else paths.DefaultInputLayout()
    )
    validate_examples(
        examples=load_examples(),
        invalid_only=args.invalidonly,
        source_output=args.sourceoutput,
        releases=Releases(layout, schema.VERSION),
        version=args.version,
    )


if __name__ == "__main__":
    main()
