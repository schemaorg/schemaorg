#!/usr/bin/env python3
"""Generate a flat list of schema.org term IDs."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import logging
from pathlib import Path

from util.buildocspages import generate_terms
import util.pretty_logger as pretty_logger

log: logging.Logger = logging.getLogger(__name__)

generateTerms = generate_terms


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Build list of schema.org terms.")
    parser.add_argument(
        "-t",
        "--tagtype",
        action="store_true",
        help="Add a termtype to name",
    )
    parser.add_argument("-o", "--output", required=True, help="output file")
    args_parsed = parser.parse_args(argv)
    filename = Path(args_parsed.output)
    with pretty_logger.BlockLog(
        logger=log, message=f"Writing term list to file {filename}"
    ):
        filename.write_text(
            "".join(generate_terms(tags=args_parsed.tagtype)), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
