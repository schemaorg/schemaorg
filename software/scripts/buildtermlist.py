#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import standard python libraries

import argparse
import logging
import os
import sys
import typing
from typing import Any, Callable, Dict, Generator, Iterable, List, Optional, Sequence, Set, Tuple, Union

import SchemaTerms.sdoterm as sdoterm
import SchemaTerms.sdotermsource as sdotermsource
import util.pretty_logger as pretty_logger


# Import schema.org libraries




log: logging.Logger = logging.getLogger(__name__)


def generateTerms(tags: bool = False) -> Generator[str, None, None]:
    for term in sdotermsource.SdoTermSource.getAllTerms(expanded=True):
        if not isinstance(term, sdoterm.SdoTerm):
            continue
        label: str = ""
        if tags:
            if term.termType == sdoterm.SdoTermType.PROPERTY:
                label = " p"
            elif term.termType == sdoterm.SdoTermType.TYPE:
                label = " t"
            elif term.termType == sdoterm.SdoTermType.DATATYPE:
                label = " d"
            elif term.termType == sdoterm.SdoTermType.ENUMERATION:
                label = " e"
            elif term.termType == sdoterm.SdoTermType.ENUMERATIONVALUE:
                label = " v"
        yield term.id + label + "\n"


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
    filename: str = args_parsed.output
    with pretty_logger.BlockLog(
        logger=log, message=f"Writing term list to file {filename}"
    ):
        with open(filename, "w") as handle:
            for term_line in generateTerms(tags=args_parsed.tagtype):
                handle.write(term_line)


if __name__ == "__main__":
    main()
