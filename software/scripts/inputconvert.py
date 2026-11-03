#!/usr/bin/env python3

from __future__ import annotations

import argparse
import os
from os import getenv
from os.path import expanduser
import sys

import rdflib
from rdflib.parser import Parser
from rdflib.term import URIRef

from schemaorg.sdo_uri import SCHEMA_URL

# Ensure that the google.appengine.* packages are available
# in tests as well as all bundled third-party packages.

sdk_path = getenv(
    "APP_ENGINE", f"{expanduser('~')}/google-cloud-sdk/platform/google_appengine/"
)
sys.path.insert(0, sdk_path)  # add AppEngine SDK to path


rdflib.plugin.register("rdfa", Parser, "pyRdfa.rdflibparsers", "RDFaParser")

# The rdfa sources predate https; keep the http:// namespace.
SCHEMA_HTTP = SCHEMA_URL._replace(scheme="http").geturl()

OUTTYPES = {
    "jsonld": "jsonld",
    "xml": "xml",
    "nq": "nquads",
    "rdf": "xml",
    "ttl": "turtle",
}

parser = argparse.ArgumentParser()
parser.add_argument("-i", "--input", action="append", nargs="*", help="Input file(s)")
parser.add_argument("-o", "--outputdir", help="Output directory (Default = .)")
parser.add_argument(
    "-f",
    "--format",
    default="ttl",
    help="Output format ['xml', 'rdf', 'nquads','nt','jsonld','ttl']",
)
parser.add_argument(
    "-c", "--combinefile", default=None, help="Combine outputs into file"
)
parser.add_argument("-d", "--defaultns", help="Default output namespace")
args = parser.parse_args()
print(f"{sys.argv[0]}: Arguments: {args}")
if args.format not in OUTTYPES:
    parser.print_help()
    sys.exit(1)
format = args.format
combine = args.combinefile

SPARQL1 = f"""
PREFIX schema: <{SCHEMA_HTTP}>

DELETE {{ ?s schema:category ?o }}
WHERE {{
    ?s schema:category ?o .
}}
"""


def out(filename):
    graph.update(SPARQL1)
    graph.bind("", URIRef(SCHEMA_HTTP), override=True)
    if args.outputdir:
        outfile = f"{args.outputdir}/{filename}"
    else:
        outfile = filename
    print(f"Writing {len(graph)} triples to  {outfile}")
    f = open(outfile, "w")
    f.write(graph.serialize(format=OUTTYPES.get(format), auto_compact=True))


files = args.input[0]
graph = rdflib.ConjunctiveGraph()

for fullfilename in files:
    if not combine:
        graph = rdflib.ConjunctiveGraph()

    if args.outputdir:
        filename = os.path.basename(fullfilename)
    else:
        filename = fullfilename
    filestub, ext = os.path.splitext(filename)
    ext = ext[1:]

    graph.parse(fullfilename, format=ext)
    print(f"Loaded {len(graph)} triples from {filename}")

    if not combine:
        out(filename=f"{filestub}.{format}")

if combine:
    print("Outputting ")
    out(filename=combine)
