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

os.environ["PAGESTOREMODE"] = "FILESTORE"
os.environ["WARMUPSTATE"] = "off"

import api
import rdflib
from rdflib.term import URIRef, Literal
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from rdflib.plugins.sparql import prepareQuery, processUpdate
from rdflib.compare import graph_diff
from rdflib.namespace import RDFS, RDF
import threading

#from api import inLayer, read_file, full_path, read_schemas, read_extensions, read_examples, namespaces, DataCache, getMasterStore
#from apirdflib import getNss, getRevNss
#from apimarkdown import Markdown

parser = argparse.ArgumentParser()
parser.add_argument("-s","--httpscheme", default="https", help="httpscheme [http|https] (default: https)")
parser.add_argument("-t","--targetsite", default="", help="Target site (eg. schema.org, webschemas.org, localhost:8080)")
args = parser.parse_args()

#os.environ["DEVELOPVERSION"] = args.devsite.lower()
os.environ["DEVELOPVERSION"] = "true" #overriden later by css
os.environ["TARGETSITE"] = args.targetsite
os.environ["FORCEINDEXPAGES"] = "True" #Supresses <meta name="robots" content="noindex">

from sdoapp import *
from apirdfterm import *
setHttpScheme(args.httpscheme)
setHostPort("")

from datetime import datetime 
TARGETVERSION="8.0"
now = datetime.today().isoformat()

class dummyrequest(webapp2.Request):
    def __init__(self, *argv):
        #super(dummyrequest,self).__init__(*argv)
        self.headers = {}
        
class dummyresponse(webapp2.Response):
    def __init__(self,*argv):
        #super(dummyresponse,self).__init__(*argv)
        self._headerlist = []
        self.headers = {}
        self.status_code = 100
        
    def write(self,*argv):
        #log.info("DUMMYWRITE")
        pass
        
"""class dummystring (StringIO.StringIO):
    def __init__(self,x):
        super(dummystring,self).__init__()
    def __len__(self):
        return 0
"""
#dummyrequest = webapp2.RequestHandler(webapp2.Request({}),dummyresponse())
unit = ShowUnit()
unit.request = webapp2.Request({})
unit.response = dummyresponse()
setArguments(["_pageFlush"])
setAppVar("DEVELOPVERSION","True")

setAppVar("DocsLocationOverride","/docs/")
setAppVar("DEBUGOUT","<!-- Build for version: %s -->\n<!-- Build date: %s -->\n<!-- Build location: %s -->" % (TARGETVERSION,now,os.getcwd()))


setAppVar("LocationOverride","docs")
for ext in ["","auto","bib","health-lifesci","meta","pending","iot","attic"]:
    setHostExt(ext)
    log.info("Build Homepage: %s" % ext)
    unit.handleHomepage("/")
setHostExt("")

log.info("Build jsonldcontext.json")
context = api.GetJsonLdContext()
api.PageStore.put("json:jsonldcontext.json",context)
api.PageStore.put("txt:jsonldcontext.json.txt",context)
api.PageStore.put("jsonld:jsonldcontext.jsonld",context)

log.info("Build Schemas Page")
unit.handleSchemasPage("schemas.html")

log.info("Build Developers Page")
unit.handleDumpsPage('developers.html')

log.info("Build Full Page")
unit.handleFullHierarchyPage('full.html')

log.info("Build tree.jsonld")
unit.handleJSONSchemaTree('jsonld:tree.jsonld',ALL_LAYERS)

setAppVar("LocationOverride",None)

for t in VTerm.getAllTerms():
    if not t.getId().startswith("http"):
        unit.emitExactTermPage(t)