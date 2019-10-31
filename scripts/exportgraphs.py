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

import dev_appserver
dev_appserver.fix_sys_path()

from testharness import *
#Setup testharness state BEFORE importing sdo libraries
setInTestHarness(True)

from api import *
import rdflib
from rdflib.term import URIRef, Literal
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from rdflib.plugins.sparql import prepareQuery, processUpdate
from rdflib.compare import graph_diff
from rdflib.namespace import RDFS, RDF
import threading

from api import inLayer, read_file, full_path, read_schemas, read_extensions, read_examples, namespaces, DataCache, getMasterStore
from apirdflib import getNss
from apimarkdown import Markdown

os.environ["WARMUPSTATE"] = "off"
from sdoapp import *

from sdordf2csv import sdordf2csv


rdflib.plugin.register("json-ld", Serializer, "rdflib_jsonld.serializer", "JsonLDSerializer")

# Ensure that the google.appengine.* packages are available
# in tests as well as all bundled third-party packages.
import dev_appserver
dev_appserver.fix_sys_path()

parser = argparse.ArgumentParser()
parser.add_argument("-a","--autoext", default="Yes",help="Auto add format based file extension Yes|No. Default Yes")
parser.add_argument("-e","--exclude", default= [[]],action='append',nargs='*', help="Exclude graph(s) [core|extensions|all|bib|auto|meta|{etc} (Repeatable) -  'attic' always excluded unless explictly included")
parser.add_argument("-f","--format", default=[],action='append',nargs='*', choices=['xml', 'rdf', 'nquads','nt','json-ld','turtle','csv'])
parser.add_argument("-g","--quadgraphsuffix", help="Suffix for graph elements of quads.  eg. http://bib.schema.org/{suffix}")
parser.add_argument("-i","--include", default= [[]],action='append',nargs='*', help="Include graph(s) [core|extensions|all|attic|bib|auto|meta|{etc} (Repeatable) overrides exclude - 'attic' always excluded unless explictly individually included")
parser.add_argument("-m","--markdownprocess", default="Yes", help="Process markdown in comments Yes|No. Default Yes")
parser.add_argument("-o","--output", required=True, help="output file")
args = parser.parse_args()
print("%s: Arguments: %s" % (sys.argv[0],args))

exts = {"xml":".xml","rdf":".rdf","nquads":".nq","nt": ".nt","json-ld": ".jsonld", "turtle":".ttl", "csv":".csv"}
#ext = ""
#if args.autoext == "Yes":
#    ext = exts[args.format[0]]

graphsuffix =""
if args.quadgraphsuffix:
    graphsuffix = args.quadgraphsuffix

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

import sdoapp
from sdoapp import ENABLED_EXTENSIONS

class Export():
    def __init__(self):
        self.setSkips()
        self.setFormats()
        self.getGraphs()
        self.loadGraphs()

    def setFormats(self):
        self.formats = []
        for f in args.format:
            self.formats.append(str(f[0]))
        
    def setSkips(self):
        self.skiplist = []
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
        #if not getNss('attic') in self.skiplist: #Always skip attic by defualt
        #    self.skiplist.append(getNss('attic'))

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


    def MdComments(self,g):#Process Markdown
        Markdown.setPre("http://schema.org/")
        for s,p,o in list(g.triples( (None, RDFS.comment, None) )):
            no = Markdown.parse(o)        #g.remove((s,p,o))
            g.set((s,p,Literal(no)))
        Markdown.setPre()

    def loadGraphs(self):
        self.fullGraph = getQueryGraph()
        self.fullGraph.bind('owl', 'http://www.w3.org/2002/07/owl#')
        self.fullGraph.bind('rdfa', 'http://www.w3.org/ns/rdfa#')
        self.fullGraph.bind('dct', 'http://purl.org/dc/terms/')
        self.fullGraph.bind('schema', 'http://schema.org/')
        
        self.skipOddTriples(self.fullGraph)

        for s in self.skiplist:
            #print(" SKIPPING: %s" % s)
            self.skipTriples(s,self.fullGraph)
            
        if args.markdownprocess == "Yes":
            self.MdComments(self.fullGraph)
            
        self.outGraph = self.fullGraph

    def skipTriples(self,skip, graph):
        
        if not len(skip):
            return
        if skip.endswith("/"):
            skip = skip[:len(skip) -1]
        print("skip %s" % skip)

        delcore="""PREFIX schema: <http://schema.org/>
        DELETE {?term ?p ?o}
        WHERE {
             ?term ?p ?o.
                    ?term a ?t.
                    FILTER NOT EXISTS {?term schema:isPartOf ?x}.
        }"""
        
        delext ="""PREFIX schema: <http://schema.org/>
        DELETE {?s ?p ?o}
        WHERE {
            ?s a ?t;
            schema:isPartOf <%s>.
            ?s ?p ?o.
        }""" % skip
        

        if skip == "http://schema.org":
            q = delcore
        else:
            q = delext
        
        before = len(graph) 
        
        processUpdate(graph,q)
        

    def skipOddTriples(self, graph):
        
        delf = """
        DELETE {?s ?p ?o}
        WHERE {
            ?s ?p ?o.
            FILTER (! strstarts(str(?s), "http://schema.org")).
        }"""
        
        processUpdate(graph,delf)
        
        
    def output(self):
        for fmt in self.formats:
            if fmt == 'csv':
                self.outputCSV()
            else:
                ext = exts[fmt]
                kwargs = {'sort_keys': True}
                fname = "%s%s" % (args.output,ext)
                print("%s: Writing to: %s" % (sys.argv[0],fname))
                file = open(fname, "w")
                format = fmt
                if format == "xml" or format == "rdf":
                    format = "pretty-xml"
                    
                if fmt in ["rdf","xml","nt","turtle","csv"]: #Need only triples
                    gr = self.outGraph
                else:                                        #Need quads
                    gr = rdflib.Dataset()
                    g = gr.graph(URIRef("http://schema.org/%s" % graphsuffix))
                    g += self.fullGraph
                
                file.write(gr.serialize(format=format,auto_compact=True,**kwargs))


    def outputCSV(self):
        markdown = False
        if args.markdownprocess == "Yes":
            markdown = True

        csv = sdordf2csv(queryGraph=self.outGraph,fullGraph=self.fullGraph,markdownComments=markdown)
        print("%s processing csv output" % sys.argv[0])
        print("%s processing csv types output" % sys.argv[0])

        fname = "%s-types%s" % (args.output,".csv")
        log.info("\t%s" % fname)
        print("%s: Writing to: %s" % (sys.argv[0],fname))
        file = open(fname, "w")
        csv.outputCSVtypes(file)
        file.close()

        print("%s processing csv properties output" % sys.argv[0])

        fname = "%s-properties%s" % (args.output,".csv")
        log.info("\t%s" % fname)
        print("%s: Writing to: %s" % (sys.argv[0],fname))
        file = open(fname, "w")
        csv.outputCSVproperties(file)
        file.close()



if __name__ == "__main__":
    ex = Export()
    ex.output()
