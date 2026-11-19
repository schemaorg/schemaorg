#!/usr/bin/env python3
"""Tool to reformat, merge, and annotate schema.org Turtle files."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import logging
from pathlib import Path
import sys

from schemaorg.progress import LogProgressReporter
from schemaorg.tasks.turtle_tasks import (
    AnnotateTurtleTask,
    LintTurtleTask,
    MergeTurtleTask,
    VALID_PARTS,
)

log: logging.Logger = logging.getLogger(__name__)


def main(argv: Sequence[str] | None = None) -> None:
    """Parse CLI arguments and dispatch to the selected subcommand."""
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Re-organize Turtle files")
    subparsers = parser.add_subparsers(dest="command", required=True)

    lint_parser = subparsers.add_parser("lint", help="Reformat files (aka linting)")
    lint_parser.add_argument("-o", "--output", help="Output file (default: overwrites)")
    lint_parser.add_argument("files", nargs="+")

    merge_parser = subparsers.add_parser("merge", help="Merging several files")
    merge_parser.add_argument("-o", "--output", required=True, help="Output file")
    merge_parser.add_argument("files", nargs="+")

    annotate_parser = subparsers.add_parser(
        "annotate", help="Add annotations to types and properties."
    )
    annotate_parser.add_argument("-o", "--output", help="Output file")
    annotate_parser.add_argument(
        "--ispartof",
        required=True,
        choices=VALID_PARTS,
        help="Target state in schema.org (pending, attic, meta, or GA)",
    )
    annotate_parser.add_argument("files", nargs="+")

    args = parser.parse_args(argv)
    if (
        args.command in ("lint", "annotate")
        and args.output is not None
        and len(args.files) > 1
    ):
        parser.error("Cannot use --output with multiple files!")

    progress = LogProgressReporter(logger=log, log_steps=True)
    input_files = [Path(f) for f in args.files]

    try:
        if args.command == "lint":
            output = Path(args.output) if args.output is not None else None
            LintTurtleTask(
                files=input_files,
                output=output,
                progress=progress,
            ).run()
        elif args.command == "merge":
            MergeTurtleTask(
                files=input_files,
                output=Path(args.output),
                progress=progress,
            ).run()
        elif args.command == "annotate":
            output = Path(args.output) if args.output is not None else None
            AnnotateTurtleTask(
                files=input_files,
                output=output,
                part_of=args.ispartof,
                progress=progress,
            ).run()
    except ValueError as exc:
        log.error("%s", exc)
        sys.exit(1)


if __name__ == "__main__":
    main()
