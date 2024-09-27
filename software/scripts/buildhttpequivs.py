#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import os
import argparse

import rdflib
from rdflib.term import URIRef
from rdflib.namespace import OWL

# Import schema.org libraries
if os.getcwd() not in sys.path:
    sys.path.insert(1, os.getcwd())

import software.SchemaTerms.sdotermsource as sdotermsource
import software.SchemaTerms.sdoterm as sdoterm

exts = {"rdf": ".rdf", "nt": ".nt", "json-ld": ".jsonld", "turtle": ".ttl"}


def buildequivs(format):
    s_p = "http://schema.org/"
    s_s = "https://schema.org/"
    outGraph = rdflib.Graph()
    outGraph.bind("schema_p", s_p)
    outGraph.bind("schema_s", s_s)
    outGraph.bind("owl", OWL)

    for t in sdotermsource.SdoTermSource.getAllTerms(expanded=True):
        if not t.retired:  # drops non-schema terms and those in attic
            eqiv = OWL.equivalentClass
            if t.termType == sdoterm.SdoTerm.PROPERTY:
                eqiv = OWL.equivalentProperty

            p = URIRef(s_p + t.id)
            s = URIRef(s_s + t.id)
            outGraph.add((p, eqiv, s))
            outGraph.add((s, eqiv, p))
            # log.info("%s " % t.uri)

    for ftype in exts:
        if format != "all" and format != ftype:
            continue
        ext = exts[ftype]
        kwargs = {"sort_keys": True}
        format = ftype
        if format == "rdf":
            format = "pretty-xml"
        return outGraph.serialize(format=format, auto_compact=True, **kwargs)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-f",
        "--format",
        default="all",
        choices=["xml", "rdf", "nquads", "nt", "json-ld", "turtle", "csv"],
    )
    parser.add_argument("-o", "--output", required=True, help="output file")
    args = parser.parse_args()

    out = buildequivs(format=args.format)

    fname = "%s%s" % (args.output, ext)
    print("%s: Writing to: %s" % (buildequivs, fname))
    file = open(fname, "w", encoding="utf8")
    file.write(out)
