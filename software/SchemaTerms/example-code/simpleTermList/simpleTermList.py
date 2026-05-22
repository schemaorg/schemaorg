#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys

import rdflib

if os.getcwd() not in sys.path:
    sys.path.insert(1, os.getcwd())
import software

from SchemaTerms.localmarkdown import Markdown
from SchemaTerms.sdoterm import *
from SchemaTerms.sdotermsource import *


Markdown.setWikilinkCssClass("localLink")
Markdown.setWikilinkPrePath("/")

DATADIR = os.path.join(os.path.dirname(__file__), "../data")
if SdoTermSource.vocabUri().startswith("https://"):
    triplesfile = os.path.join(DATADIR, "schemaorg-all-https.nt")
else:
    triplesfile = os.path.join(DATADIR, "schemaorg-all-http.nt")


termgraph = rdflib.Graph()
termgraph.parse(triplesfile, format="nt")

print("loaded %s triples" % len(termgraph))

SdoTermSource.setSourceGraph(termgraph)
print("Types Count: %s" % len(SdoTermSource.getAllTypes(expanded=False)))
print("Properties Count: %s" % len(SdoTermSource.getAllProperties(expanded=False)))


for termname in ["acceptedAnswer", "Book"]:
    term = SdoTermSource.getTerm(termname)

    print("")
    print("TYPE: %s" % term.termType)
    print("URI: %s" % term.uri)
    print("ID: %s" % term.id)
    print("LABEL: %s" % term.label)
    print("")
    print("superPaths: %s" % term.superPaths)
    print("comment: %s" % term.comment)
    print("equivalents: %s" % term.equivalents)
    print("examples: %s" % term.examples)
    print("pending: %s" % term.pending)
    print("retired: %s" % term.retired)
    print("sources: %s" % term.sources)
    print("acknowledgements:" % term.acknowledgements)
    print("subs: %s" % term.subs)
    print("supers: %s" % term.supers)
    print("supersededBy: %s" % term.supersededBy)
    print("supersedes: %s" % term.supersedes)
    print("termStack: %s" % term.termStack)

    for stackElement in term.termStack:
        print("Element: %s" % stackElement)

    if term.termType == SdoTermType.TYPE or term.termType == SdoTermType.ENUMERATION:
        print("Properties: %s" % term.properties)
        print("All Properties: %s" % term.allproperties)
        print("Expected Type for: %s" % term.expectedTypeFor)

    if term.termType == SdoTermType.PROPERTY:
        print("Domain includes: %s" % term.domainIncludes)
        print("Range includes: %s" % term.rangeIncludes)
    else:
        if term.termType == SdoTermType.ENUMERATION:
            print("Enumeration Members: %s" % term.enumerationMembers)


        if term.termType == SdoTermType.ENUMERATIONVALUE:
            print("Parent Enumeration: %s" % term.enumerationParent)

        for p in term.properties:
            prop = SdoTermSource.getTerm(p)
            print("Prop: %s.  Pending: %s" % (prop.id, prop.pending))
            print("   Expected Types: %s" % prop.rangeIncludes)
            print("   Comment: %s" % prop.comment)
