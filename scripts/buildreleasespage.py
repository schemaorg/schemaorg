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

parser = argparse.ArgumentParser()
parser.add_argument("-o","--outputfile", required=True, help="output file")
args = parser.parse_args()
print "%s: Arguments: %s" % (sys.argv[0],args)
ofile = open(args.outputfile,'w')


import dev_appserver
dev_appserver.fix_sys_path()

from testharness import *
#Setup testharness state BEFORE importing sdo libraries
setInTestHarness(True)

from api import *
import rdflib
from rdflib import Graph
from rdflib.term import URIRef, Literal
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from rdflib.plugins.sparql import prepareQuery
from rdflib.compare import graph_diff
from rdflib.namespace import RDFS, RDF
import threading

os.environ["WARMUPSTATE"] = "off"
from sdoapp import *
from sdoapp import SCHEMA_VERSION

page = ShowUnit().buildFullReleasePage('version/build-latest', SCHEMA_VERSION,'core')

print("Writing releases page to file %s" %  args.outputfile)
ofile.write(page.encode('utf-8'))
ofile.close()
