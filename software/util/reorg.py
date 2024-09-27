#!/usr/bin/env python
"""A Tool to help maintain the set of ttl files in schema.org.

This helps reformatting, merging and splitting ttl files along
semantic axis.
"""

from collections.abc import Sequence
from rdflib import Graph, Namespace
import logging
import sys
import argparse

def SchemaOrgGraph():
  """Creates a graph with usual namespaces set as we want in schemaorg."""
  g = Graph()
  g.bind("dc", Namespace("http://purl.org/dc/terms/"), replace=True)
  return g

def GraphsAreIdentical(g1, g2):
  only_in_g1 = g1 - g2
  only_in_g2 = g2 - g1
  # TODO: print sampled diffs if any.
  return len(only_in_g1) == 0 and len(only_in_g2) == 0

def Lint(args):
  """Reformats the file(s) properly."""
  def LintOne(filename, output_filename):
    logging.info(" - reading file ...")
    g = SchemaOrgGraph()
    g.parse(filename, format="turtle")
    logging.info(f" - writing back {output_filename if output_filename != filename else ''} ...")
    g.serialize(output_filename, format="turtle")

    v = SchemaOrgGraph()
    v.parse(output_filename, format="turtle")
    if not GraphsAreIdentical(v, g):
      logging.fatal(f"Linting file {filename} lost some information.")
    logging.info(" - validated.")

  if args.output is not None and len(args.files) > 1:
    logging.fatal(f"Cannot use --output with multiple files!")
  for index, filename in enumerate(args.files):
    logging.info(f"Handling file {index} of {len(args.files)} ({filename})")
    LintOne(filename, args.output or filename)


def main():
  """
  Parses command line arguments and dispatches to the appropriate
  command.
  """
  logging.basicConfig(level=logging.INFO)

  parser = argparse.ArgumentParser(description="Re-organize Turtle files")
  subparsers = parser.add_subparsers(dest='command')

  lint_parser = subparsers.add_parser('lint',
                                      help='Reformat files (aka linting)')
  lint_parser.add_argument('-o', '--output',
                           help='Output file (default: overwrites)')
  lint_parser.add_argument("files", action="extend", nargs="+", type=str);

  # Parse and dispatch
  args = parser.parse_args()
  if args.command == 'lint':
    Lint(args)
  else:
    parser.print_help()


if __name__ == "__main__":
  main()
