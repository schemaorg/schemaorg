#!/usr/bin/env python3
"""Compare vocabulary terms and triples between two schema.org releases or sources."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import logging
import sys

from schemaorg import constants
from schemaorg.layout import InputLayout
from schemaorg.progress import LogProgressReporter
from schemaorg.tasks.compare_vocabulary import CompareVocabularyTask

log: logging.Logger = logging.getLogger(__name__)


def _parse_bool_arg(value: str | bool) -> bool:
    if isinstance(value, bool):
        return value
    lowered = value.strip().lower()
    if lowered in ("yes", "true", "1", "y"):
        return True
    if lowered in ("no", "false", "0", "n"):
        return False
    raise argparse.ArgumentTypeError(f"Expected Yes or No, got {value!r}")


def main(argv: Sequence[str] | None = None) -> None:
    logging.basicConfig(level=logging.INFO)
    # Historical releases predate HTTPS; suppress per-URI upgrade chatter.
    logging.getLogger("schemaorg.sdo_uri").setLevel(logging.ERROR)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-p",
        "--previous",
        help="Previous release version or path (default: previous release in versions.json)",
    )
    parser.add_argument(
        "-c",
        "--current",
        help="Current release version, 'source', or path (default: working-tree source TTLs)",
    )
    parser.add_argument(
        "-e",
        "--exclude",
        default=[],
        action="extend",
        nargs="*",
        help="Exclude layer(s) [core|extensions|pending|attic|meta|auto|bib|...] (repeatable)",
    )
    parser.add_argument(
        "-i",
        "--include",
        default=[],
        action="extend",
        nargs="*",
        help="Include layer(s), overriding --exclude (repeatable)",
    )
    parser.add_argument(
        "-t",
        "--triples",
        nargs="?",
        const=True,
        default=False,
        type=_parse_bool_arg,
        help="Show triple differences (Yes/No or flag)",
    )
    parser.add_argument(
        "-n",
        "--names",
        nargs="?",
        const=True,
        default=False,
        type=_parse_bool_arg,
        help="List added, dropped, and changed term names (Yes/No or flag)",
    )
    args = parser.parse_args(argv)

    report = CompareVocabularyTask(
        input_layout=InputLayout(constants.PROJECT_ROOT),
        previous_spec=args.previous,
        current_spec=args.current,
        exclude_layers=args.exclude,
        include_layers=args.include,
        show_names=args.names,
        show_triples=args.triples,
        progress=LogProgressReporter(logger=log, log_steps=False),
    ).run()
    sys.stdout.write(report.formatted_report)


if __name__ == "__main__":
    main()
