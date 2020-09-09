#!/usr/bin/env python2.7
import unittest
import os
from os import path, getenv
from os.path import expanduser
import glob
import argparse
import sys
import csv

sys.path.append( os.getcwd() )
sys.path.insert( 1, 'lib' ) #Pickup libs, rdflib etc., from shipped lib directory
sys.path.insert( 1, 'sdopythonapp' ) #Pickup sdopythonapp functionality
sys.path.insert( 1, 'sdopythonapp/lib' ) #Pickup sdopythonapp libs, rdflib etc., from shipped lib directory
sys.path.insert( 1, 'sdopythonapp/site' ) #Pickup sdopythonapp from shipped site
# Ensure that the google.appengine.* packages are available
# in tests as well as all bundled third-party packages.

sdk_path = getenv('APP_ENGINE',  expanduser("~") + '/google-cloud-sdk/platform/google_appengine/')
sys.path.insert(0, sdk_path) # add AppEngine SDK to path

import logging
logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)

import dev_appserver
dev_appserver.fix_sys_path()

import webapp2

from testharness import *
#Setup testharness state BEFORE importing sdo libraries
setInTestHarness(True)

import api
import rdflib
from rdflib.term import URIRef, Literal
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from rdflib.plugins.sparql import prepareQuery, processUpdate
from rdflib.compare import graph_diff
from rdflib.namespace import RDFS, RDF
import threading


from sdoapp import *
from apirdfterm import *

#from api import inLayer, read_file, full_path, read_schemas, read_extensions, read_examples, namespaces, DataCache, getMasterStore
#from apirdflib import getNss, getRevNss
#from apimarkdown import Markdown

parser = argparse.ArgumentParser()
#parser.add_argument("-f","--format", default=[],action='append',nargs='*', choices=['xml', 'rdf', 'nquads','nt','json-ld','turtle','csv'])
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


for t in VTerm.getAllTerms():
    if not t.inLayers('attic') and not t.getId().startswith("http"): #drops non-schema terms and those in attic
        eqiv = OWL.equivalentClass
        if t.isProperty():
            eqiv = OWL.equivalentProperty
        
        p = URIRef(s_p + t.getId())
        s = URIRef(s_s + t.getId())
        outGraph.add((p, eqiv, s))
        outGraph.add((s, eqiv, p))
        #log.info("%s " % t.uri)
        
for ftype in exts:
    ext = exts[ftype]
    fname = "%s%s" % (args.output,ext)
    print("%s: Writing to: %s" % (sys.argv[0],fname))
    kwargs = {'sort_keys': True}
    file = open(fname, "w")
    format = ftype
    if format == "rdf":
        format = "pretty-xml"
    file.write(outGraph.serialize(format=format,auto_compact=True,**kwargs))
