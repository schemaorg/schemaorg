#!/usr/bin/env python3
"""Tool to reformat, merge, and annotate schema.org Turtle files."""

from __future__ import annotations

import argparse
import itertools
import logging
from pathlib import Path

import rdflib

from schemaorg.publish import turtle
from schemaorg.sdo_uri import SdoUri
import util.schema_graph as graph


def Lint(args: argparse.Namespace) -> None:
    """Reformats the file(s) properly."""

    def LintOne(filename: str, output_filename: str) -> None:
        logging.info(" - reading file ...")
        g: graph.SchemaOrgGraph = graph.SchemaOrgGraph([Path(filename)])
        logging.info(
            " - writing back %s ...",
            output_filename if output_filename != filename else "",
        )
        g.serialize(output_filename, format="turtle")
        if not g.IdenticalTo(graph.SchemaOrgGraph([Path(output_filename)])):
            logging.fatal("Linting file %s lost some information.", filename)

    if args.output is not None and len(args.files) > 1:
        logging.fatal("Cannot use --output with multiple files!")
    for index, filename in enumerate(args.files):
        logging.info("Handling file %d of %d (%s)", index, len(args.files), filename)
        LintOne(filename, args.output or filename)
        logging.info(" - validated.")


def MergeFiles(args: argparse.Namespace) -> None:
    """Merges a set of files into one."""
    logging.info("Merging files %d into %s", len(args.files), args.output)
    # The loader takes the whole list, so the merge is the load.
    merged: graph.SchemaOrgGraph = graph.SchemaOrgGraph(
        [Path(f) for f in args.files]
    )
    logging.info("Writing %s ...", args.output)
    merged.serialize(args.output, format="turtle")

    for filename in args.files:
        if not merged.FullyContains(graph.SchemaOrgGraph([Path(filename)])):
            logging.fatal("Merging files into %s lost some information.", args.output)


def Annotate(args: argparse.Namespace) -> None:
    """Adds some annotations to properties and types."""
    if args.output is not None and len(args.files) > 1:
        logging.fatal("Cannot use --output with multiple files!")

    valid_parts: list[str] = ["pending", "attic", "meta", "GA"]
    if args.ispartof not in valid_parts:
        logging.fatal(
            "PartOf annotation '%s' is not valid: select one of %s",
            args.ispartof,
            valid_parts,
        )
    new_part: rdflib.URIRef = SdoUri.for_layer(args.ispartof).uri

    for filename in args.files:
        logging.info("Annotating %s ...", filename)
        g: graph.SchemaOrgGraph = graph.SchemaOrgGraph([Path(filename)])
        # Clean the existing parts
        g.remove((None, graph.SCHEMAORG.isPartOf, None))
        # GA is special as it is the unannotated state.
        if args.ispartof != "GA":
            for sub in itertools.chain(g.Types(), g.Properties()):
                g.add((sub, graph.SCHEMAORG.isPartOf, new_part))

        g.serialize(args.output or filename, format="turtle")
        logging.info(" ... done, written to %s", args.output or filename)


def main() -> None:
    """
    Parses command line arguments and dispatches to the appropriate
    command.
    """
    logging.basicConfig(level=logging.INFO)

    # Every subcommand rewrites .ttl files that humans review in diffs, so
    # opt into the deterministic subject ordering. This is a global rdflib
    # mutation, which is why it lives in the entry point and not in a
    # library import.
    turtle.register_as_turtle()

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
