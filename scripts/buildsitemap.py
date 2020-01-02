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
from time import gmtime, strftime

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
from rdflib.plugins.sparql import prepareQuery
from rdflib.compare import graph_diff
from rdflib.namespace import RDFS, RDF
import threading

from api import inLayer, read_file, full_path, read_schemas, read_extensions, read_examples, namespaces, DataCache, getMasterStore
from apirdflib import getNss, getRevNss
from apimarkdown import Markdown

os.environ["WARMUPSTATE"] = "off"
from sdoapp import *

from sdordf2csv import sdordf2csv


rdflib.plugin.register("json-ld", Serializer, "rdflib_jsonld.serializer", "JsonLDSerializer")

# Ensure that the google.appengine.* packages are available
# in tests as well as all bundled third-party packages.
import dev_appserver
dev_appserver.fix_sys_path()

TODAY = strftime("%Y-%m-%d",gmtime())
parser = argparse.ArgumentParser()
parser.add_argument("-e","--exclude", default= [[]],action='append',nargs='*', help="Exclude graph(s) [core|extensions|all|bib|auto|meta|{etc} (Repeatable) -  'attic' always excluded")
parser.add_argument("-o","--output", default="docs/sitemap.xml", help="output file (default: docs/sitemap.xml)")
parser.add_argument("-s","--site", default="schema.org", help="site (default: schema.org)")
parser.add_argument("-d","--date", default=TODAY, help="modified date (defaut: %s)" % TODAY)
args = parser.parse_args()
#print "%s: Arguments: %s" % (sys.argv[0],args)


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

#Setup testharness state BEFORE importing sdoapp
import sdoapp
from sdoapp import ENABLED_EXTENSIONS

STATICPAGES = ["docs/schemas.html",
"docs/full.html",
"docs/gs.html",
"docs/about.html",
"docs/howwework.html",
"docs/releases.html",
"docs/faq.html",
"docs/datamodel.html",
"docs/developers.html",
"docs/extension.html",
"docs/meddocs.html",
"docs/hotels.html"]

class SiteMap():
    def __init__(self):
        self.today = args.date
        self.count = 0
        self.openFile()
        self.setSkips()
        self.getGraphs()
        self.loadGraphs()
        self.listStatics()
        self.closeFile()


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

    def openFile(self):
        hdr = """<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
"""
        self.file = open(args.output,'w')
        self.file.write(hdr)

    def closeFile(self):
        self.file.write("\n</urlset>")
        print("Wrote %s entries to %s" % (self.count,args.output))
        self.file.close()

    def getGraphs(self):
        self.store = getMasterStore()
        self.fullGraph = getQueryGraph()
        #read_schemas(loadExtensions=True)
        #read_extensions(sdoapp.ENABLED_EXTENSIONS)
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
                print("%s: Processing: %s  (%s) " % (sys.argv[0],id,len(g)))
                self.list(g)
                self.access("",g.identifier)

    def list(self, graph):
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

    def listStatics(self):
        for s in STATICPAGES:
            self.access(s,"http://schema.org")

    def access(self, id, ext):
        if id.startswith("http://schema.org"):
            id = id[18:]
        ext = getRevNss(str(ext))

        if ext == "core" or ext == "":
            ext = ""
        else:
            ext = ext + "."

        site = args.site
        scheme = "https://"
        if site.startswith("http://"):
            site = site[7:]
        elif site.startswith("https://"):
            site = site[8:]
            scheme = "https://"
        #log.info("%s  %s  %s  %s" % (scheme,ext,site,id))
        path = "%s%s%s/%s" % (scheme,ext,site,id)
        #log.info(path)
        self.outputEntry(path)

    def outputEntry(self,path,update=None):
        if not update:
            update = self.today

        entry = """  <url>
   <loc>%s</loc>
   <lastmod>%s</lastmod>
  </url>""" % (path,update)
        self.output(entry)

    def output(self,txt):
        self.count +=1
        self.file.write(txt)








if __name__ == "__main__":
    ex = SiteMap()
