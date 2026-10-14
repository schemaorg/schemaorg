#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
from pathlib import Path
from typing import Dict, Generator, Optional, Sequence

import SchemaTerms.sdoterm as sdoterm
import SchemaTerms.sdotermsource as sdotermsource
import util.pretty_logger as pretty_logger

log: logging.Logger = logging.getLogger(__name__)

TERM_TAGS: Dict[sdoterm.SdoTermType, str] = {
    sdoterm.SdoTermType.PROPERTY: " p",
    sdoterm.SdoTermType.TYPE: " t",
    sdoterm.SdoTermType.DATATYPE: " d",
    sdoterm.SdoTermType.ENUMERATION: " e",
    sdoterm.SdoTermType.ENUMERATIONVALUE: " v",
}


def generateTerms(tags: bool = False) -> Generator[str, None, None]:
    for term in sdotermsource.SdoTermSource.getAllTerms(expanded=True):
        if not isinstance(term, sdoterm.SdoTerm):
            continue
        label: str = TERM_TAGS.get(term.termType, "") if tags else ""
        yield f"{term.id}{label}\n"


def main(argv: Optional[Sequence[str]] = None) -> None:
    parser = argparse.ArgumentParser(description="Build list of schema.org terms.")
    parser.add_argument(
        "-t",
        "--tagtype",
        default=False,
        action="store_true",
        help="Add a termtype to name",
    )
    parser.add_argument("-o", "--output", required=True, help="output file")
    args_parsed = parser.parse_args(argv)
    filename: Path = Path(args_parsed.output)
    with pretty_logger.BlockLog(
        logger=log, message=f"Writing term list to file {filename}"
    ):
        filename.write_text(
            "".join(generateTerms(tags=args_parsed.tagtype)), encoding="utf-8"
        )


if __name__ == "__main__":
    main()
