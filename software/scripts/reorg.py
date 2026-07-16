#!/usr/bin/env python3
# -*- coding: utf-8; python-indent-offset: 4 -*-
"""A Tool to help maintain the set of ttl files in schema.org.

This helps reformatting, merging and splitting ttl files along
semantic axis.
"""

import argparse
import itertools
import logging
import os
from pathlib import Path
import sys
import typing
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Set, Tuple, Union

import rdflib

if os.getcwd() not in sys.path:
    sys.path.insert(1, os.getcwd())
import software

import util.schema_graph as graph


# Import schema.org libraries



def Lint(args: argparse.Namespace) -> None:
    """Reformats the file(s) properly."""

    def LintOne(filename: str, output_filename: str) -> None:
        logging.info(" - reading file ...")
        g: graph.SchemaOrgGraph = graph.SchemaOrgGraph(Path(filename))
        logging.info(
            f" - writing back {output_filename if output_filename != filename else ''} ..."
        )
        g.serialize(output_filename, format="turtle")
        if not g.IdenticalTo(graph.SchemaOrgGraph(Path(output_filename))):
            logging.fatal(f"Linting file {filename} lost some information.")

    if args.output is not None and len(args.files) > 1:
        logging.fatal(f"Cannot use --output with multiple files!")
    for index, filename in enumerate(args.files):
        logging.info(f"Handling file {index} of {len(args.files)} ({filename})")
        LintOne(filename, args.output or filename)
        logging.info(" - validated.")


def MergeFiles(args: argparse.Namespace) -> None:
    """Merges a set of files into one."""
    logging.info(f"Merging files {len(args.files)} into {args.output}")
    merged: graph.SchemaOrgGraph = graph.SchemaOrgGraph(Path(args.files[0]))
    for filename in args.files[1:]:
        logging.info(f" - reading {filename} ...")
        merged.parse(filename, format="turtle")
    logging.info(f"Writing {args.output} ...")
    merged.serialize(args.output, format="turtle")

    for filename in args.files:
        if not merged.FullyContains(graph.SchemaOrgGraph(Path(filename))):
            logging.fatal(f"Merging files into {args.output} lost some information.")


def Annotate(args: argparse.Namespace) -> None:
    """Adds some annotations to properties and types."""
    if args.output is not None and len(args.files) > 1:
        logging.fatal(f"Cannot use --output with multiple files!")

    valid_parts: List[str] = ["pending", "attic", "meta", "GA"]
    if args.ispartof not in valid_parts:
        logging.fatal(
            f"PartOf annotation '{args.ispartof}' is not valid: select one of {valid_parts}"
        )
    new_part: rdflib.URIRef = rdflib.URIRef(f"https://{args.ispartof}.schema.org/")

    for filename in args.files:
        logging.info(f"Annotating {filename} ...")
        g: graph.SchemaOrgGraph = graph.SchemaOrgGraph(Path(filename))
        # Clean the existing parts
        g.remove((None, graph.SCHEMAORG.isPartOf, None))
        # GA is special as it is the unannotated state.
        if args.ispartof != "GA":
            for sub in itertools.chain(g.Types(), g.Properties()):
                g.add((sub, graph.SCHEMAORG.isPartOf, new_part))

        g.serialize(args.output or filename, format="turtle")
        logging.info(f" ... done, written to {args.output or filename}")


def main() -> None:
    """
    Parses command line arguments and dispatches to the appropriate
    command.
    """
    logging.basicConfig(level=logging.INFO)

    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Re-organize Turtle files")
    subparsers = parser.add_subparsers(dest="command")

    lint_parser = subparsers.add_parser("lint", help="Reformat files (aka linting)")
    lint_parser.add_argument("-o", "--output", help="Output file (default: overwrites)")
    lint_parser.add_argument("files", action="extend", nargs="+", type=str)

    merge_parser = subparsers.add_parser("merge", help="Merging several files")
    merge_parser.add_argument("-o", "--output", help="Output file")
    merge_parser.add_argument("files", action="extend", nargs="+", type=str)

    annotate_parser = subparsers.add_parser(
        "annotate", help="Add annotations to types and properties."
    )
    annotate_parser.add_argument("-o", "--output", help="Output file")
    annotate_parser.add_argument(
        "--ispartof",
        help="Which state classes and properties are in schema.org (eg. pending, attic)",
    )
    annotate_parser.add_argument("files", action="extend", nargs="+", type=str)

    # Parse and dispatch
    args: argparse.Namespace = parser.parse_args()
    if args.command == "lint":
        Lint(args)
    elif args.command == "merge":
        MergeFiles(args)
    elif args.command == "annotate":
        Annotate(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
