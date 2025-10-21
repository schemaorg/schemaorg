#!/usr/bin/env python
# -*- coding: utf-8; python-indent-offset: 4 -*-
"""A Tool to help maintain the set of ttl files in schema.org.

This helps reformatting, merging and splitting ttl files along
semantic axis.
"""

import argparse
import itertools
import logging
import os
import rdflib
import sys

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software.util.schema_graph as graph


def Lint(args):
    """Reformats the file(s) properly."""

    def LintOne(filename, output_filename, format):
        logging.info(" - reading file ...")
        g = graph.SchemaOrgGraph(filename, format=format)
        logging.info(
            f" - writing back {output_filename if output_filename != filename else ''} ..."
        )
        g.serialize(output_filename, format=format)
        if not g.IdenticalTo(graph.SchemaOrgGraph(output_filename, format=format)):
            logging.fatal(f"Linting file {filename} lost some information.")

        if args.output is not None and len(args.files) > 1:
            logging.fatal(f"Cannot use --output with multiple files!")
        for index, filename in enumerate(args.files):
            logging.info(f"Handling file {index} of {len(args.files)} ({filename})")
            LintOne(filename, args.output or filename, format="turtle")
            logging.info(" - validated.")


def MergeFiles(args):
    """Merges a set of files into one."""
    logging.info(f"Merging files {len(args.files)} into {args.output}")
    merged = graph.SchemaOrgGraph()
    for filename in args.files:
        logging.info(f" - reading {filename} ...")
        merged.parse(filename, format="turtle")
    logging.info(f"Writing {args.output} ...")
    merged.serialize(args.output, format="turtle")

    for filename in args.files:
        if not merged.FullyContains(graph.SchemaOrgGraph(filename, format="turtle")):
            logging.fatal(f"Merging files into {args.output} lost some information.")


def Annotate(args):
    """Adds some annotations to properties and types."""
    if args.output is not None and len(args.files) > 1:
        logging.fatal(f"Cannot use --output with multiple files!")

    valid_parts = ["pending", "attic", "meta", "GA"]
    if args.ispartof not in valid_parts:
        logging.fatal(
            f"PartOf annotation '{args.ispartof}' is not valid: select one of {valid_parts}"
        )
    new_part = rdflib.URIRef(f"https://{args.ispartof}.schema.org/")

    for filename in args.files:
        logging.info(f"Annotating {filename} ...")
        g = graph.SchemaOrgGraph(filename, format="turtle")
        # Clean the existing parts
        g.remove((None, graph.SCHEMAORG.isPartOf, None))
        # GA is special as it is the unannotated state.
        if args.ispartof != "GA":
            for sub in itertools.chain(g.Types(), g.Properties()):
                g.add((sub, graph.SCHEMAORG.isPartOf, new_part))

        g.serialize(args.output or filename, format="turtle")
        logging.info(f" ... done, written to {args.output or filename}")


def main():
    """
    Parses command line arguments and dispatches to the appropriate
    command.
    """
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(description="Re-organize Turtle files")
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
    args = parser.parse_args()
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
