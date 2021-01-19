#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(1)


import os
import io
for path in [os.getcwd(),"software/Util","software/SchemaTerms","software/SchemaExamples"]:
  sys.path.insert( 1, path ) #Pickup libs from local  directories

from buildsite import *
from sdotermsource import SdoTermSource, VOCABURI
from sdoterm import *
import rdflib
from rdflib.term import URIRef, Literal
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from rdflib.plugins.sparql import prepareQuery, processUpdate
from rdflib.namespace import RDFS, RDF



#from api import inLayer, read_file, full_path, read_schemas, read_extensions, read_examples, namespaces, DataCache, getMasterStore
#from apirdflib import getNss, getRevNss
#from apimarkdown import Markdown

parser = argparse.ArgumentParser()
parser.add_argument("-f","--format", default="all", choices=['xml', 'rdf', 'nquads','nt','json-ld','turtle','csv'])
parser.add_argument("-o","--output", required=True, help="output file")
args = parser.parse_args()

exts = {"rdf":".rdf","nt": ".nt","json-ld": ".jsonld", "turtle":".ttl"}


from rdflib.namespace import OWL
s_p = "http://schema.org/"
s_s = "https://schema.org/"
outGraph = rdflib.Graph()
outGraph.bind("schema_p",s_p)
outGraph.bind("schema_s",s_s)
outGraph.bind("owl",OWL)


for t in SdoTermSource.getAllTerms(expanded=True):
    if not t.retired: #drops non-schema terms and those in attic
        eqiv = OWL.equivalentClass
        if t.termType == SdoTerm.PROPERTY:
            eqiv = OWL.equivalentProperty
        
        p = URIRef(s_p + t.id)
        s = URIRef(s_s + t.id)
        outGraph.add((p, eqiv, s))
        outGraph.add((s, eqiv, p))
        #log.info("%s " % t.uri)
        
for ftype in exts:
    if args.format != "all" and args.format != ftype:
        continue
    ext = exts[ftype]
    fname = "%s%s" % (args.output,ext)
    print("%s: Writing to: %s" % (sys.argv[0],fname))
    kwargs = {'sort_keys': True}
    file = open(fname, "w")
    format = ftype
    if format == "rdf":
        format = "pretty-xml"
    out = outGraph.serialize(format=format,auto_compact=True,**kwargs).decode()
    file.write(out)