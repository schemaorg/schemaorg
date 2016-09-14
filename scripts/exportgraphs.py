#!/usr/bin/env python
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
from rdflib.namespace import RDFS, RDF
import threading

from api import inLayer, read_file, full_path, read_schemas, read_extensions, read_examples, namespaces, DataCache, getMasterStore
from apirdflib import getNss
from apimarkdown import Markdown

from sdordf2csv import sdordf2csv


rdflib.plugin.register("json-ld", Serializer, "rdflib_jsonld.serializer", "JsonLDSerializer")

# Ensure that the google.appengine.* packages are available
# in tests as well as all bundled third-party packages.
import dev_appserver
dev_appserver.fix_sys_path()

parser = argparse.ArgumentParser()
parser.add_argument("-a","--autoext", default="Yes",help="Auto add format based file extension Yes|No. Default Yes")
parser.add_argument("-e","--exclude", default= [[]],action='append',nargs='*', help="Exclude graph(s) [core|extensions|all|bib|auto|meta|{etc} (Repeatable) -  'attic' always excluded unless explictly included")
parser.add_argument("-f","--format", default="nt", choices=['xml', 'rdf', 'nquads','nt','json-ld','turtle','csv'])
parser.add_argument("-g","--quadgraphsuffix", help="Suffix for graph elements of quads.  eg. http://bib.schema.org/{suffix}")
parser.add_argument("-i","--include", default= [[]],action='append',nargs='*', help="Include graph(s) [core|extensions|all|attic|bib|auto|meta|{etc} (Repeatable) overrides exclude - 'attic' always excluded unless explictly individually included")
parser.add_argument("-m","--markdownprocess", default="Yes", help="Process markdown in comments Yes|No. Default Yes")
parser.add_argument("-o","--output", required=True, help="output file")
args = parser.parse_args()
print "%s: Arguments: %s" % (sys.argv[0],args)

exts = {"xml":".xml","rdf":".rdf","nquads":".nq","nt": ".nt","json-ld": ".jsonld", "turtle":".ttl", "csv":".csv"}
ext = ""
if args.autoext == "Yes":
    ext = exts[args.format]
    
graphsuffix =""
if args.quadgraphsuffix:
    graphsuffix = args.quadgraphsuffix

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

#Setup testharness state BEFORE importing sdoapp
setInTestHarness(True)
import sdoapp
from sdoapp import ENABLED_EXTENSIONS 

class Export():
    def __init__(self):
        self.setSkips()
        self.getGraphs()
        self.loadGraphs()

    def setSkips(self):
        self.skiplist = [''] 
        for e in args.exclude:
            for s in e:
                if s == "core":
                    self.skiplist.append("http://schema.org/")
                elif s == "extensions":
                    for i in sdoapp.ENABLED_EXTENSIONS:
                        self.skiplist.append(getNss(i))
                elif s == "all":
                    self.skiplist.append("http://schema.org/")
                    for i in sdoapp.ENABLED_EXTENSIONS:
                        self.skiplist.append(getNss(i))
                else:
                    self.skiplist.append(getNss(s))
        if not getNss('attic') in self.skiplist: #Always skip attic by defualt
            self.skiplist.append(getNss('attic'))

        for e in args.include:
            for s in e:
                if s == "core" and "http://schema.org/" in self.skiplist:
                    self.skiplist.remove("http://schema.org/")
                elif s == "extensions":
                    for i in sdoapp.ENABLED_EXTENSIONS:
                        if getNss(i) in self.skiplist:
                            self.skiplist.remove(getNss(i))
                elif s == "all":
                    self.skiplist.remove("http://schema.org/")
                    for i in sdoapp.ENABLED_EXTENSIONS:
                        if getNss(i) in self.skiplist and getNss(i) != "attic":
                            self.skiplist.remove(getNss(i))
                elif getNss(s) in self.skiplist:
                    self.skiplist.remove(getNss(s))

    def getGraphs(self):
        self.store = getMasterStore()
        self.fullGraph = getQueryGraph()
        read_schemas(loadExtensions=True)
        read_extensions(sdoapp.ENABLED_EXTENSIONS)
        self.graphs = list(self.store.graphs())


    def MdComments(self,g):#Process Markdown
        Markdown.setPre("http://schema.org/")
        for s,p,o in list(g.triples( (None, RDFS.comment, None) )):
            no = Markdown.parse(o)        #g.remove((s,p,o))
            g.set((s,p,Literal(no)))
        Markdown.setPre()

    def loadGraphs(self):
        self.outGraph = rdflib.Dataset()
        simpleFormat = False
        if args.format == "rdf" or args.format == "xml" or args.format == "nt" or args.format == "turtle" or args.format == "csv":
            simpleFormat = True
            self.outGraph = rdflib.Graph()
            self.fullGraph = getQueryGraph()
            self.outGraph.bind('owl', 'http://www.w3.org/2002/07/owl#')
            self.outGraph.bind('rdfa', 'http://www.w3.org/ns/rdfa#')
            self.outGraph.bind('dct', 'http://purl.org/dc/terms/')
            self.outGraph.bind('schema', 'http://schema.org/')

        gs = sorted(list(self.store.graphs()),key=lambda u: u.identifier)

        for g in gs: #Put core first
            if str(g.identifier) == "http://schema.org/":
                gs.remove(g)
                gs.insert(0,g)
                break

        for g in gs:
            id = str(g.identifier)
            if not id.startswith("http://"):#skip some internal graphs
                continue    
            print "%s: Processing: %s  (%s) with markdownprocess=%s" % (sys.argv[0],id,len(g), args.markdownprocess)
            if args.markdownprocess == "Yes":
                self.MdComments(g)
            if simpleFormat:
                if id not in self.skiplist:
                    self.outGraph += g
            else:
                if id not in self.skiplist:
                    o = self.outGraph.graph(URIRef("%s%s" % (id,graphsuffix)))
                    o +=g

    def output(self):
        if args.format == 'csv':
            self.outputCSV()
        else:
            kwargs = {'sort_keys': True}
            fname = "%s%s" % (args.output,ext)
            print "%s: Writing to: %s" % (sys.argv[0],fname)
            file = open(fname, "w")
            format = args.format
            if format == "xml" or format == "rdf":
                format = "pretty-xml"
            file.write(self.outGraph.serialize(format=format,**kwargs))


    def outputCSV(self):
        markdown = False
        if args.markdownprocess == "Yes":
            markdown = True
        
        csv = sdordf2csv(queryGraph=self.outGraph,fullGraph=self.fullGraph,markdownComments=markdown)
        print "%s processing csv output" % sys.argv[0]
        print "%s processing csv types output" % sys.argv[0]

        fname = "%s-types%s" % (args.output,ext)
        log.info("\t%s" % fname)
        print "%s: Writing to: %s" % (sys.argv[0],fname)
        file = open(fname, "w")
        csv.outputCSVtypes(file)
        file.close()

        fname = "%s-properties%s" % (args.output,ext)
        log.info("\t%s" % fname)
        print "%s: Writing to: %s" % (sys.argv[0],fname)
        file = open(fname, "w")
        csv.outputCSVproperties(file)
        file.close()
        fname = "%s-enumvalues%s" % (args.output,ext)
        log.info("\t%s" % fname)
        print "%s: Writing to: %s" % (sys.argv[0],fname)
        file = open(fname, "w")
        csv.outputCSVenums(file)
        file.close()
                
if __name__ == "__main__":
    ex = Export()
    ex.output()

    




