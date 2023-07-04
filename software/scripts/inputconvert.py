#!/usr/bin/env python2.7
import unittest
import os
from os import path, getenv
from os.path import expanduser
import logging # https://docs.python.org/2/library/logging.html#logging-levels
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

import rdflib
from rdflib.term import URIRef, Literal
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from rdflib.plugins.sparql import prepareQuery, processUpdate
from rdflib.compare import graph_diff
from rdflib.namespace import RDFS, RDF


rdflib.plugin.register("rdfa", Parser, "pyRdfa.rdflibparsers", "RDFaParser")

OUTTYPES = {'jsonld': 'jsonld','xml':'xml','nq':'nquads','rdf':'xml','ttl':'turtle'}

parser = argparse.ArgumentParser()
parser.add_argument("-i","--input" , action='append',nargs='*', help="Input file(s)")
parser.add_argument("-o","--outputdir", help="Output directory (Default = .)")
parser.add_argument("-f","--format", default='ttl', help="Output format ['xml', 'rdf', 'nquads','nt','jsonld','ttl']")
parser.add_argument("-c","--combinefile", default=None, help="Combine outputs into file")
parser.add_argument("-d","--defaultns", help="Default output namespace")
args = parser.parse_args()
print("%s: Arguments: %s" % (sys.argv[0],args))
if args.format not in OUTTYPES:
    parser.print_help()
    sys.exit(1)
format = args.format
combine = args.combinefile

SPARQL1 = """
PREFIX schema: <http://schema.org/> 

DELETE { ?s schema:category ?o }
WHERE {
    ?s schema:category ?o .
}
"""

def out(filename):
    graph.update(SPARQL1)
    graph.bind('',URIRef('http://schema.org/'),override=True)
    if args.outputdir:
        outfile = "%s/%s" % (args.outputdir,filename)
    else:
        outfile = filename
    print("Writing %s triples to  %s" % (len(graph),outfile))
    f = open(outfile,'w')
    f.write(graph.serialize(format=OUTTYPES.get(format),auto_compact=True))

files = args.input[0]
graph = rdflib.ConjunctiveGraph()

for fullfilename in files:
    if not combine:
        graph = rdflib.ConjunctiveGraph()
        
        
    if  args.outputdir:
        filename = os.path.basename(fullfilename)
    else:
        filename = fullfilename
    filestub, ext = os.path.splitext(filename)
    ext = ext[1:]

    graph.parse(fullfilename,format = ext)
    print("Loaded %s triples from %s" % (len(graph), filename))
    
    if not combine:
        out(filename="%s.%s" % (filestub,format))

if combine:
    print("Outputting ")
    out(filename=combine)
    
    





