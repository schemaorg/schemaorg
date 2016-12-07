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

from api import setInTestHarness
setInTestHarness(True)

from api import inLayer, read_file, full_path, read_schemas, read_extensions, read_examples, namespaces, DataCache, getMasterStore
from apirdflib import getNss, getRevNss
from apimarkdown import Markdown

from sdordf2csv import sdordf2csv


rdflib.plugin.register("json-ld", Serializer, "rdflib_jsonld.serializer", "JsonLDSerializer")

# Ensure that the google.appengine.* packages are available
# in tests as well as all bundled third-party packages.
import dev_appserver
dev_appserver.fix_sys_path()

parser = argparse.ArgumentParser()
parser.add_argument("-e","--exclude", default= [[]],action='append',nargs='*', help="Exclude graph(s) [core|extensions|all|bib|auto|meta|{etc} (Repeatable) -  'attic' always excluded unless explictly included")
parser.add_argument("-p","--pausetime", default=0, help="Seconds between requests")
parser.add_argument("-i","--include", default= [[]],action='append',nargs='*', help="Include graph(s) [core|extensions|all|attic|bib|auto|meta|{etc} (Repeatable) overrides exclude - 'attic' always excluded unless explictly individually included")
parser.add_argument("-s","--site", required=True, help="site")
args = parser.parse_args()
print "%s: Arguments: %s" % (sys.argv[0],args)

pause = 0
if args.pausetime:
    pause = args.pausetime

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

#Setup testharness state BEFORE importing sdoapp
import sdoapp
from sdoapp import ENABLED_EXTENSIONS 

STATICPAGES = ["","docs/schemas.html","docs/full.html"]

class Exercise():
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



    def loadGraphs(self):
        self.outGraph = rdflib.ConjunctiveGraph()

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
            if id not in self.skiplist:
                print "%s: Processing: %s  (%s) " % (sys.argv[0],id,len(g))
                self.exercise(g)
                self.exerciseStatics(g.identifier)

    def exercise(self, graph):
        types = {}
        props = {}
        exts = []
        for (s,p,o) in graph.triples((None,RDF.type,RDFS.Class)):
            if s.startswith("http://schema.org"):
                types.update({s:graph.identifier})

        for t in sorted(types.keys()):
            self.access(t,types[t])
            
        for (s,p,o) in graph.triples((None,RDF.type,RDF.Property)):
            if s.startswith("http://schema.org"):
                props.update({s:graph.identifier})

        for p in sorted(props.keys()):
            self.access(p,props[p])

    def exerciseStatics(self, graph):
        for s in STATICPAGES:
            self.access(s,graph)

    def access(self, id, ext):
        if id.startswith("http://schema.org"):
            id = id[18:]
        ext = getRevNss(str(ext))
        if ext == "core":
            ext = ""
        else:
            ext = ext + "."
            
        site = args.site
        scheme = "http://"
        if site.startswith("http://"):
            site = site[7:]
        elif site.startswith("https://"):
            site = site[8:]
            scheme = "https://"
        #log.info("%s  %s  %s  %s" % (scheme,ext,site,id))
        path = "%s%s%s/%s" % (scheme,ext,site,id)
        self.fetch(path)
    
    def fetch(self, url):
        import urllib2
        import time,datetime
        
        success = False
        fivehundred = 0
        while not success:
            load_start = datetime.datetime.now()
            try:
                sys.stdout.write(url)
                sys.stdout.flush()
                r = urllib2.urlopen(url)
                print "  " + str(datetime.datetime.now()-load_start)
                success = True

            except urllib2.HTTPError as e:
              print("got error: {} - {}".format(e.code, e.reason))
              if e.code == 500:
                  fivehundred += 1
            
            time.sleep(args.pausetime)

            if not fivehundred or fivehundred > 5:
                break
            
        return

        

                
if __name__ == "__main__":
    ex = Exercise()
    

    




