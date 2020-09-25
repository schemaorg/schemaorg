#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import sys
if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(1)

# To be executed in the SchemaTerms/example-code/{example} directory
import os
for path in [os.getcwd(),"..","../..","../../.."]: #Adds in current, example-code, and SchemaTerms directory into path
  sys.path.insert( 1, path ) #Pickup libs from local  directories

from sdotermsource import *
from sdoterm import *
from localmarkdown import Markdown

Markdown.setWikilinkCssClass("localLink")
Markdown.setWikilinkPrePath("/")


triplesfile = "../data/schemaorg-all-http.nt"
SdoTermSource.VOCABURI = "https://schema.org/" #Force to https as loaded https file
SdoTermSource.loadSourceGraph(triplesfile)
print ("loaded %s triples" % len(SdoTermSource.sourceGraph()))

terms = SdoTermSource.getAllTerms()
print ("Terms Count: %s" % len(terms))

from schematermsprotobuf import sdotermToProtobuf, sdotermToProtobufMsg, sdotermToProtobufText, protobufToMsg, protobufToText

import time,datetime

start = datetime.datetime.now() #debug
for t in terms:
    tic = datetime.datetime.now() #debug
    
    term = SdoTermSource.getTerm(t,expanded=False)
    buf = sdotermToProtobuf(term)
    msg = protobufToMsg(buf)
    txt = protobufToText(buf)
    mfilename = "out-protomsgs/" + t +".msg"
    tfilename = "out-protomsgs/" + t +".txt"
    f = open(mfilename,"wb")
    f.write(msg)
    f.close()
    f = open(tfilename,"w")
    f.write(txt)
    f.close()
    
    print("Term: %s - %s" % (t, str(datetime.datetime.now()-tic))) #debug
print ("All terms took %s seconds" % str(datetime.datetime.now()-start)) #debug
    



