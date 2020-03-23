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

parser = argparse.ArgumentParser()
parser.add_argument("-e","--exclude", default= [[]],action='append',nargs='*', help="Exclude graph(s) [core|extensions|all|bib|auto|meta|{etc} (Repeatable) -  'attic' always excluded unless explictly included")
parser.add_argument("-p","--pausetime", default=0, help="Seconds between requests")
parser.add_argument("-i","--include", default= [[]],action='append',nargs='*', help="Include graph(s) [core|extensions|all|attic|bib|auto|meta|{etc} (Repeatable) overrides exclude - 'attic' always excluded unless explictly individually included")
parser.add_argument("-s","--site", required=True, help="site")
args = parser.parse_args()

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
        self.exercise(self.outGraph)
        self.exerciseStatics("")

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
                props.update({s:"http://schema.org"})

        for p in sorted(props.keys()):
            self.access(p,props[p])

    def exerciseStatics(self, graph):
        for s in STATICPAGES:
            self.access(s,graph)

    def access(self, id, ext):
        if id.startswith("http://schema.org"):
            id = id[18:]
        ext = ""
        #ext = getRevNss(str(ext))
        #if ext == "core":
        #    ext = ""
        #else:
        #    ext = ext + "."

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
                print("  %s  %s" % (r.getcode(), str(datetime.datetime.now()-load_start)))
                success = True

            except urllib2.HTTPError as e:
              print("  got error: {} - {}".format(e.code, e.reason))
              if e.code == 500:
                  fivehundred += 1

            time.sleep(float(args.pausetime))

            if not fivehundred or fivehundred > 5:
                break

        return




if __name__ == "__main__":
    ex = Exercise()
