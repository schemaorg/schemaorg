#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Import standard python libraries

import argparse
import io
import logging
import os
import sys

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software

import software.SchemaTerms.sdotermsource as sdotermsource
import software.SchemaTerms.sdoterm as sdoterm

log = logging.getLogger(__name__)


def generateTerms(tags=False):
    for term in sdotermsource.SdoTermSource.getAllTerms(expanded=True):
        label = ""
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
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-t",
        "--tagtype",
        default=False,
        action="store_true",
        help="Add a termtype to name",
    )
    parser.add_argument("-o", "--output", required=True, help="output file")
    args = parser.parse_args()
    filename = args.output
    log.info("Writing term list to file %s", filename)
    with open(filename, "w", encoding="utf-8") as handle:
        for term in generateTerms(tags=args.tagtype):
            handle.write(term)
    log.info("Done")
