#!/usr/bin/env python3
"""Validate JSON-LD examples against the generated SHACL schema."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import logging
import os
from pathlib import Path
import sys

from schemaorg import constants
from schemaorg.layout import (
    Domain,
    InputLayout,
    NEXT_VERSION,
    OutputLayout,
    Releases,
)
from schemaorg.layout.releases import VersionRef
from schemaorg.progress import LogProgressReporter
from schemaorg.tasks.validate_examples import (
    ShaclConfigError,
    ValidatableExample,
    ValidateExamplesTask,
)
from schemaorg.version import Version
import SchemaExamples.schemaexamples as schemaexamples

log: logging.Logger = logging.getLogger(__name__)


def load_examples(input_layout: InputLayout) -> list[schemaexamples.Example]:
    """Find and load all JSON-LD examples."""
    loaded = schemaexamples.SchemaExamples.from_layout(input_layout)
    log.info("Loaded %d examples, processing JSON-LD variants", len(loaded))
    return [ex for ex in loaded.allExamples() if ex.hasJsonld()]


def validate_examples(
    examples: Sequence[ValidatableExample],
    invalid_only: bool,
    source_output: bool,
    releases: Releases | None = None,
    version: VersionRef = NEXT_VERSION,
) -> None:
    """Validate examples via ValidateExamplesTask and map failures to exit codes."""
    if releases is None:
        input_layout = InputLayout(constants.PROJECT_ROOT)
        version_registry = Version(
            input_layout.file(Domain.ROOT, constants.VERSIONS_FILE)
        )
        rel = Releases(input_layout, version_registry)
    else:
        rel = releases
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

    input_layout = InputLayout(constants.PROJECT_ROOT)
    version_registry = Version(
        input_layout.file(Domain.ROOT, constants.VERSIONS_FILE)
    )
    releases_layout: InputLayout | OutputLayout = (
        OutputLayout(Path(args.output)) if args.output else input_layout
    )
    validate_examples(
        examples=load_examples(input_layout),
        invalid_only=args.invalidonly,
        source_output=args.sourceoutput,
        releases=Releases(releases_layout, version_registry),
        version=args.version,
    )


if __name__ == "__main__":
    main()
