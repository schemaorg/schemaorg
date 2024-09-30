#!/usr/bin/env python
import unittest
import os
from os import path, getenv
from os.path import expanduser
import logging  # https://docs.python.org/2/library/logging.html#logging-levels
import glob
import argparse
import StringIO
import sys

sys.path.append(os.getcwd())
sys.path.insert(1, "lib")  # Pickup libs, rdflib etc., from shipped lib directory
# Ensure that the google.appengine.* packages are available
# in tests as well as all bundled third-party packages.

sdk_path = getenv(
    "APP_ENGINE", expanduser("~") + "/google-cloud-sdk/platform/google_appengine/"
)
sys.path.insert(0, sdk_path)  # add AppEngine SDK to path

import dev_appserver

dev_appserver.fix_sys_path()

from testharness import *

# Setup testharness state BEFORE importing sdo libraries
setInTestHarness(True)

from api import *
import rdflib
from rdflib import Graph
from rdflib import RDF, RDFS
from rdflib.term import URIRef, Literal
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from rdflib.plugins.sparql import prepareQuery
from rdflib.compare import graph_diff
import threading

from api import (
    inLayer,
    read_file,
    full_path,
    read_schemas,
    read_extensions,
    read_examples,
    namespaces,
    DataCache,
    getMasterStore,
)
from apirdflib import getNss


# Ensure that the google.appengine.* packages are available
# in tests as well as all bundled third-party packages.
import dev_appserver

dev_appserver.fix_sys_path()

import sdoapp

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument(
    "-e",
    "--exclude",
    default=[[]],
    action="append",
    nargs="*",
    help="Exclude graph(s) [core|extensions|bib|auto|meta|{etc} (Repeatable)",
)
parser.add_argument(
    "-i",
    "--include",
    default=[[]],
    action="append",
    nargs="*",
    help="Include graph(s) [core|extensions|bib|auto|meta|{etc} (Repeatable) overrides exclude",
)
parser.add_argument(
    "-t", "--triples", default="No", help="Show triple differences Yes|No. Default No"
)
parser.add_argument(
    "-n", "--names", default="No", help="List term names Yes|No. Default No"
)
args = parser.parse_args()
showDiffs = False
if args.triples.lower() == "yes":
    showDiffs = True
showNames = False
if args.names.lower() == "yes":
    showNames = True


def getCurrentGraph():
    currentGraph = Graph()
    skiplist = []
    for e in args.exclude:
        for s in e:
            if s == "core":
                skiplist.append("http://schema.org/")
            elif s == "extensions":
                for i in sdoapp.ENABLED_EXTENSIONS:
                    skiplist.append(getNss(i))
            else:
                skiplist.append(getNss(s))

    for e in args.include:
        for s in e:
            if s == "core" and "http://schema.org/" in skiplist:
                skiplist.remove("http://schema.org/")
            elif s == "extensions":
                for i in sdoapp.ENABLED_EXTENSIONS:
                    if getNss(i) in skiplist:
                        skiplist.remove(getNss(i))
            elif getNss(s) in skiplist:
                skiplist.remove(getNss(s))

    store = getMasterStore()
    read_schemas(loadExtensions=True)
    read_extensions(sdoapp.ENABLED_EXTENSIONS)
    graphs = list(store.graphs())

    gs = sorted(list(store.graphs()), key=lambda u: u.identifier)

    for g in gs:  # Put core first
        if str(g.identifier) == "http://schema.org/":
            gs.remove(g)
            gs.insert(0, g)
            break

    for g in gs:
        id = str(g.identifier)
        if not id.startswith("http://"):  # skip some internal graphs
            continue
        if id in skiplist:  # Skip because we have been asked to
            continue

        currentGraph += g
    return currentGraph


def getPreviousGraph(sources):
    graph = Graph()
    parse_errors = rdflib.Graph()
    for s in sources:
        graph.parse(s, format="rdfa", pgraph=parse_errors)

    return graph


def termsInGraph(g):
    """terms that are not defined as properties or types, stringified."""
    _terms = []
    # g.bind("rdf",RDF)
    # g.bind("rdfs",RDFS)
    for s, p, o in g.triples((None, RDF.type, None)):
        if s not in _terms:
            _terms.append(str(s))
    return _terms


def compareCommonTerms(terms, buff):
    global currentGraph, previousGraph, showDiffs
    currentGraph.bind("schema", "http://schema.org/")
    currentGraph.bind("dc", "http://purl.org/dc/terms/")
    currentGraph.bind("rdf", RDF)
    currentGraph.bind("rdfs", RDFS)
    changedCount = 0
    for t in sorted(terms):
        c = Graph()
        p = Graph()
        for trip in currentGraph.triples((URIRef(t), None, None)):
            c.add(trip)
        for trip in previousGraph.triples((URIRef(t), None, None)):
            p.add(trip)
        newg = c - p
        dropg = p - c
        if len(newg) > 0 or len(dropg) > 0:
            changedCount += 1
            buff.write("   Changed term: %s\n" % t)
            if showDiffs:
                for s, p, o in newg.triples((None, None, None)):
                    buff.write(
                        "       New:     %s %s %s\n"
                        % (str(s), currentGraph.qname(p), o)
                    )
                for s, p, o in dropg.triples((None, None, None)):
                    buff.write(
                        "       Dropped: %s %s %s\n"
                        % (str(s), currentGraph.qname(p), o)
                    )
    return changedCount


currentGraph = None
previousGraph = None

import codecs
import sys

UTF8Writer = codecs.getwriter("utf8")
sys.stdout = UTF8Writer(sys.stdout)


if __name__ == "__main__":
    currentGraph = getCurrentGraph()
    previousGraph = getPreviousGraph(
        [
            "https://raw.github.com/schemaorg/schemaorg/sdo-phobos/data/schema.rdfa",
            "https://raw.github.com/schemaorg/schemaorg/sdo-phobos/data/ext/auto/auto.rdfa",
            "https://raw.github.com/schemaorg/schemaorg/sdo-phobos/data/ext/bib/bsdo-1.0.rdfa",
            "https://raw.github.com/schemaorg/schemaorg/sdo-phobos/data/ext/bib/comics.rdfa",
        ]
    )

    curTypes = set(termsInGraph(currentGraph))
    prevTypes = set(termsInGraph(previousGraph))

    print("Current terms count %s" % len(curTypes))
    print("Previous terms Count %s" % len(prevTypes))

    new = curTypes.difference(prevTypes)
    dropped = prevTypes.difference(curTypes)
    common = curTypes.intersection(prevTypes)

    print("==========   Terms  ================")
    print("Dropped terms %s" % len(dropped))
    if showNames:
        for i in sorted(dropped):
            print("   Dropped term %s" % i)
    print("New terms %s" % len(new))
    if showNames:
        for i in sorted(new):
            print("   New term %s" % i)

    buff = StringIO.StringIO()
    print("Changed terms %s" % compareCommonTerms(common, buff))
    if showNames:
        print(buff.getvalue())
