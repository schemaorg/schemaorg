#!/usr/bin/env python3
"""Print or record a schema.org release version."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from datetime import date

from util.schema import VERSION


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--add",
        metavar="X.Y",
        help="Add a new numbered release to versions.json.",
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Release date in YYYY-MM-DD format (defaults to today when --add is set).",
    )
    args = parser.parse_args(argv)
    if args.add:
        release_date = args.date or date.today().isoformat()
        VERSION.add_version(args.add, release_date)
    print(VERSION.current().number())


if __name__ == "__main__":
    main()
