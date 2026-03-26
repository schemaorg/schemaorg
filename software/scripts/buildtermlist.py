#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import standard python libraries

import argparse
import logging
import os
import sys
import typing
from typing import Any, Dict, List, Optional, Tuple, Union, Iterable, Sequence, Set, Callable, Generator

# Import schema.org libraries
if os.getcwd() not in sys.path:
    sys.path.insert(1, os.getcwd())


import software.SchemaTerms.sdotermsource as sdotermsource
import software.SchemaTerms.sdoterm as sdoterm
import software.util.pretty_logger as pretty_logger


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


if __name__ == "__main__":
    parser: argparse.ArgumentParser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--tagtype",
        default=False,
        action="store_true",
        help="Add a termtype to name",
    )
    parser.add_argument("-o", "--output", required=True, help="output file")
    args_parsed: argparse.Namespace = parser.parse_args()
    filename: str = args_parsed.output
    with pretty_logger.BlockLog(
        logger=log, message=f"Writing term list to file {filename}"
    ):
        with open(filename, "w", encoding="utf-8") as handle:
            for term_line in generateTerms(tags=args_parsed.tagtype):
                handle.write(term_line)
