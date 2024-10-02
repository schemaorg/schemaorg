#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(1)

# To be executed in the SchemaTerms/example-code/{example} directory
import os
for path in [os.getcwd(),"..","../..","../../.."]: #Adds in current, example-code, and SchemaTerms directory into path
  sys.path.insert( 1, path ) #Pickup libs from local  directories

import rdflib
from rdflib.namespace import OWL
import argparse
import glob
from sdotermsource import *
from sdoterm import *

parser = argparse.ArgumentParser()
parser.add_argument("-o","--output", required=True, help="output file")
args = parser.parse_args()

exts = {"rdf":".rdf","nt": ".nt","json-ld": ".jsonld", "turtle":".ttl"}

files = []
triplesfilesglob = ["data/*.ttl","data/ext/*/*.ttl"]
schemaroot = "../../../"
for g in triplesfilesglob:
        files.extend(glob.glob(schemaroot + g))
SdoTermSource.loadSourceGraph(files)

s_p = "http://schema.org/"
s_s = "https://schema.org/"
outGraph = rdflib.Graph()
outGraph.bind("schema_p",s_p)
outGraph.bind("schema_s",s_s)
outGraph.bind("owl",OWL)

VOCABURI = SdoTermSource.vocabUri()
terms = SdoTermSource.getAllTerms()
print("Loaded %d terms" % len(terms))

for term in terms:
    t = SdoTermSource.getTerm(term)

    if t.uri.startswith(VOCABURI): #Filter out non Schema terms
        eqiv = OWL.equivalentClass
        if t.termType == SdoTerm.PROPERTY:
            eqiv = OWL.equivalentProperty

        p = URIRef(s_p + t.id)
        s = URIRef(s_s + t.id)
        outGraph.add((p, eqiv, s))
        outGraph.add((s, eqiv, p))
        print(t.id)

for ftype in exts:
    ext = exts[ftype]
    fname = "%s%s" % (args.output,ext)
    print("%s: Writing to: %s" % (sys.argv[0],fname))
    kwargs = {'sort_keys': True}
    f = open(fname, "w")
    format = ftype
    if format == "rdf":
        format = "pretty-xml"
    output = outGraph.serialize(format=format,auto_compact=True,**kwargs).decode()
    f.write(output)

        
        

