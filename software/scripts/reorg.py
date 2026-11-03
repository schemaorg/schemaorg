#!/usr/bin/env python3
"""Tool to reformat, merge, and annotate schema.org Turtle files."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import itertools
import logging
from pathlib import Path

import rdflib

from schemaorg.publish import turtle
from schemaorg.sdo_uri import SdoUri
import util.schema_graph as graph

log: logging.Logger = logging.getLogger(__name__)

VALID_PARTS: tuple[str, ...] = ("pending", "attic", "meta", "GA")


def Lint(args: argparse.Namespace) -> None:
    """Reformat Turtle file(s) deterministically."""
    if args.output is not None and len(args.files) > 1:
        raise SystemExit("Cannot use --output with multiple files.")

    def lint_one(source: Path, target: Path) -> None:
        log.info(" - reading file ...")
        g = graph.SchemaOrgGraph([source])
        suffix = f" {target}" if target != source else ""
        log.info(" - writing back%s ...", suffix)
        g.serialize(target, format="turtle")
        if not g.IdenticalTo(graph.SchemaOrgGraph([target])):
            log.error("Linting file %s lost some information.", source)
            raise SystemExit(1)

    total = len(args.files)
    for index, filename in enumerate(args.files, start=1):
        source_path = Path(filename)
        target_path = Path(args.output) if args.output else source_path
        log.info("Handling file %d of %d (%s)", index, total, filename)
        lint_one(source_path, target_path)
        log.info(" - validated.")


def MergeFiles(args: argparse.Namespace) -> None:
    """Merge multiple Turtle files into one."""
    input_paths = [Path(f) for f in args.files]
    output_path = Path(args.output)
    log.info("Merging %d files into %s", len(input_paths), output_path)
    # The loader takes the whole list, so the merge is the load.
    merged = graph.SchemaOrgGraph(input_paths)
    log.info("Writing %s ...", output_path)
    merged.serialize(output_path, format="turtle")

    written = graph.SchemaOrgGraph([output_path])
    for path in input_paths:
        if not written.FullyContains(graph.SchemaOrgGraph([path])):
            log.error("Merging files into %s lost some information.", output_path)
            raise SystemExit(1)


def Annotate(args: argparse.Namespace) -> None:
    """Set or clear schema:isPartOf annotations on types and properties."""
    if args.output is not None and len(args.files) > 1:
        raise SystemExit("Cannot use --output with multiple files.")
    if args.ispartof not in VALID_PARTS:
        raise SystemExit(
            f"PartOf annotation '{args.ispartof}' is not valid: "
            f"select one of {list(VALID_PARTS)}"
        )

    # GA is the unannotated state.
    new_part: rdflib.URIRef | None = (
        SdoUri.for_layer(args.ispartof).uri if args.ispartof != "GA" else None
    )

    for filename in args.files:
        source_path = Path(filename)
        target_path = Path(args.output) if args.output else source_path
        log.info("Annotating %s ...", source_path)
        g = graph.SchemaOrgGraph([source_path])
        g.remove((None, graph.SCHEMAORG.isPartOf, None))
        if new_part is not None:
            for sub in itertools.chain(g.Types(), g.Properties()):
                g.add((sub, graph.SCHEMAORG.isPartOf, new_part))

        g.serialize(target_path, format="turtle")
        log.info(" ... done, written to %s", target_path)


def main(argv: Sequence[str] | None = None) -> None:
    """Parse CLI arguments and dispatch to the selected subcommand."""
    logging.basicConfig(level=logging.INFO)

    # Every subcommand rewrites .ttl files that humans review in diffs, so
    # opt into the deterministic subject ordering. This is a global rdflib
    # mutation, which is why it lives in the entry point and not in a
    # library import.
    turtle.register_as_turtle()

    parser = argparse.ArgumentParser(description="Re-organize Turtle files")
    subparsers = parser.add_subparsers(dest="command", required=True)

    lint_parser = subparsers.add_parser("lint", help="Reformat files (aka linting)")
    lint_parser.add_argument("-o", "--output", help="Output file (default: overwrites)")
    lint_parser.add_argument("files", nargs="+")

    merge_parser = subparsers.add_parser("merge", help="Merging several files")
    merge_parser.add_argument("-o", "--output", required=True, help="Output file")
    merge_parser.add_argument("files", nargs="+")

    annotate_parser = subparsers.add_parser(
        "annotate", help="Add annotations to types and properties."
    )
    annotate_parser.add_argument("-o", "--output", help="Output file")
    annotate_parser.add_argument(
        "--ispartof",
        required=True,
        choices=VALID_PARTS,
        help="Target state in schema.org (pending, attic, meta, or GA)",
    )
    annotate_parser.add_argument("files", nargs="+")

    args = parser.parse_args(argv)
    if (
        args.command in ("lint", "annotate")
        and args.output is not None
        and len(args.files) > 1
    ):
        parser.error("Cannot use --output with multiple files!")

    if args.command == "lint":
        Lint(args)
    elif args.command == "merge":
        MergeFiles(args)
    elif args.command == "annotate":
        Annotate(args)


if __name__ == "__main__":
    main()
