#!/usr/bin/env python
import unittest
import os
from os import path, getenv
from os.path import expanduser
import logging # https://docs.python.org/2/library/logging.html#logging-levels
import glob
import argparse
import sys
sys.path.append( os.getcwd() ) 
sys.path.insert( 1, 'lib' ) #Pickup libs, rdflib etc., from shipped lib directory
# Ensure that the google.appengine.* packages are available
# in tests as well as all bundled third-party packages.

sdk_path = getenv('APP_ENGINE',  expanduser("~") + '/google-cloud-sdk/platform/google_appengine/')
sys.path.insert(0, sdk_path) # add AppEngine SDK to path

import dev_appserver
dev_appserver.fix_sys_path()

from api import *
import rdflib
from rdflib.term import URIRef, Literal
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from rdflib.plugins.sparql import prepareQuery
from rdflib.compare import graph_diff
import threading

from api import inLayer, read_file, full_path, read_schemas, read_extensions, read_examples, namespaces, DataCache, getMasterStore
from apirdflib import getNss


# Ensure that the google.appengine.* packages are available
# in tests as well as all bundled third-party packages.
import dev_appserver
dev_appserver.fix_sys_path()

parser = argparse.ArgumentParser()
parser.add_argument("-a","--autoext", default="Yes",help="Auto add format based file extension Yes|No. Default Yes")
parser.add_argument("-e","--exclude", default= [[]],action='append',nargs='*', help="Exclude graph(s) [core|extensions|bib|auto|meta|{etc} (Repeatable)")
parser.add_argument("-f","--format", default="nt", choices=['xml','nquads','nt','json-ld','turtle'])
parser.add_argument("-g","--quadgraphsuffix", help="Suffix for graph elements of quads.  eg. http://bib.schema.org/{suffix}")
parser.add_argument("-i","--include", default= [[]],action='append',nargs='*', help="Include graph(s) [core|extensions|bib|auto|meta|{etc} (Repeatable) overrides exclude")
parser.add_argument("-m","--markdownprocess", default="Yes", help="Process markdown in comments Yes|No. Default Yes")
parser.add_argument("-o","--output", required=True, help="output file")
args = parser.parse_args()
print "%s: Arguments: %s" % (sys.argv[0],args)

exts = {"xml":".xml","nquads":".nq","nt": ".nt","json-ld": ".jsonld", "turtle":".ttl"}
ext = ""
if args.autoext == "Yes":
    ext = exts[args.format]
    
graphsuffix =""
if args.quadgraphsuffix:
    graphsuffix = args.quadgraphsuffix

#Setup testharness state BEFORE importing sdoapp
setInTestHarness(True)
import sdoapp

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

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)
rdflib.plugin.register("json-ld", Serializer, "rdflib_jsonld.serializer", "JsonLDSerializer")


store = getMasterStore()
read_schemas(loadExtensions=True)
read_extensions(sdoapp.ENABLED_EXTENSIONS)
graphs = list(store.graphs())


from rdflib.namespace import RDFS
def MdComments(g):#Process Markdown
    for s,p,o in list(g.triples( (None, RDFS.comment, None) )):
        no = MD.parse(o)        #g.remove((s,p,o))
        g.set((s,p,Literal(no)))



outGraph = rdflib.Dataset()
simpleFormat = False
if args.format == "xml" or args.format == "nt" or args.format == "turtle":
    simpleFormat = True
    outGraph = rdflib.Graph()

gs = sorted(list(store.graphs()),key=lambda u: u.identifier)

for g in gs: #Put core first
    if str(g.identifier) == "http://schema.org/":
        gs.remove(g)
        gs.insert(0,g)
        break

for g in gs:
    id = str(g.identifier)
    if not id.startswith("http://"):#skip some internal graphs
        continue
    if id in skiplist: #Skip because we have been asked to
        continue
        
    print "%s: Processing: %s  (%s) with markdownprocess=%s" % (sys.argv[0],id,len(g), args.markdownprocess)
    if args.markdownprocess == "Yes":
        MdComments(g)
    if simpleFormat:
        outGraph += g
    else:
        o = outGraph.graph(URIRef("%s%s" % (id,graphsuffix)))
        o +=g

kwargs = {'sort_keys': True}
fname = "%s%s" % (args.output,ext)
print "%s: Writing to: %s" % (sys.argv[0],fname)
file = open(fname, "w")
file.write(outGraph.serialize(format=args.format,**kwargs))

    




