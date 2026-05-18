#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys
if os.getcwd() not in sys.path:
    sys.path.insert(1, os.getcwd())
import software

if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(1)

from SchemaTerms.sdotermsource import *
from SchemaTerms.sdoterm import *
from SchemaTerms.localmarkdown import Markdown

Markdown.setWikilinkCssClass("localLink")
Markdown.setWikilinkPrePath("/")


DATADIR = os.path.join(os.path.dirname(__file__), "../data")
triplesfile = os.path.join(DATADIR, "schemaorg-all-http.nt")
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

    term = SdoTermSource.getTerm(t,expanded=True)
    buf = sdotermToProtobuf(term)
    msg = protobufToMsg(buf)
    txt = protobufToText(buf)
    mfilename = os.path.join(os.path.dirname(__file__), "out-protomsgs", t + ".msg")
    tfilename = os.path.join(os.path.dirname(__file__), "out-protomsgs", t + ".txt")
    f = open(mfilename,"wb")
    f.write(msg)
    f.close()
    f = open(tfilename,"w")
    f.write(txt)
    f.close()

    print("Term: %s - %s" % (t, str(datetime.datetime.now()-tic))) #debug
print ("All terms took %s seconds" % str(datetime.datetime.now()-start)) #debug
