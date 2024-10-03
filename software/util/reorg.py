#!/usr/bin/env python
"""A Tool to help maintain the set of ttl files in schema.org.

This helps reformatting, merging and splitting ttl files along
semantic axis.
"""

from collections.abc import Sequence
import rdflib
import argparse
import itertools
import logging
import sys

SCHEMAORG = rdflib.Namespace("https://schema.org/")

class SchemaOrgGraph(object):
  def __init__(self, filename: str = None, format: str = "turtle"):
    self.g = rdflib.Graph()
    # Binding it here, as by default it would bind the /elements/1.1/ instead
    # of the dc terms. this way, the elements get assigned 'dc1' or such
    # as a prefix, and we do not use that.
    self.g.bind("dc", rdflib.Namespace("http://purl.org/dc/terms/"), replace=True)
    if filename:
      self.g.parse(filename, format=format)

  def __getattr__(self, *args, **kwargs):
    return getattr(self.g, *args, **kwargs);

  def IdenticalTo(self, other: "SchemaOrgGraph"):
    only_in_other = other.g - self.g
    only_in_self = self.g - other.g
    if len(only_in_other) or len(only_in_self):
      raise ValueError(f"Graphs differ: {only_in_other + only_in_self}")
    return True

  def FullyContains(self, graph: "SchemaOrgGraph"):
    only_in_subset = graph.g - self.g
    if len(only_in_subset):
      raise ValueError(f"Graph does not contain it all: {only_in_subset}")
    return True

  def ListSubjects(self, subject_type: rdflib.term.URIRef):
    return set([s for s, p, o in self.g.triples((None, rdflib.RDF.type, subject_type))])

  def Types(self):
    return self.ListSubjects(rdflib.RDFS.Class)

  def Properties(self):
    return self.ListSubjects(rdflib.RDF.Property)


def Lint(args):
  """Reformats the file(s) properly."""
  def LintOne(filename, output_filename, format):
    logging.info(" - reading file ...")
    g = SchemaOrgGraph(filename, format=format)
    logging.info(f" - writing back {output_filename if output_filename != filename else ''} ...")
    g.serialize(output_filename, format=format)
    if not g.IdenticalTo(SchemaOrgGraph(output_filename, format=format)):
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
  merged = SchemaOrgGraph()
  for filename in args.files:
    logging.info(f" - reading {filename} ...")
    merged.parse(filename, format="turtle")
  logging.info(f"Writing {args.output} ...")
  merged.serialize(args.output, format="turtle")

  for filename in args.files:
    if not merged.FullyContains(SchemaOrgGraph(filename, format="turtle")):
      logging.fatal(f"Merging files into {args.output} lost some information.")


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
  lint_parser.add_argument("files", action="extend", nargs="+", type=str)

  merge_parser = subparsers.add_parser('merge', help='Merging several files')
  merge_parser.add_argument('-o', '--output', help='Output file')
  merge_parser.add_argument("files", action="extend", nargs="+", type=str)

  # Parse and dispatch
  args = parser.parse_args()
  if args.command == 'lint':
    Lint(args)
  elif args.command == 'merge':
    MergeFiles(args)
  else:
    parser.print_help()


if __name__ == "__main__":
  main()
