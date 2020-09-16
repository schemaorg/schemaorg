#!/usr/bin/env python2.7
import sys
import os
sys.path.append( os.getcwd() )
sys.path.insert( 1, 'markdown' ) #Pickup libs, rdflib etc., from shipped lib directory
sys.path.insert( 1, 'google/protobuf' ) #Pickup libs, rdflib etc., from shipped lib directory
import rdflib
from sdotermsource import *
from sdoterm import *

triplesfile = "data/schemaorg-all-https.nt"
termgraph = rdflib.Graph()
termgraph.parse(triplesfile, format="nt")

print ("loaded %s triples" % len(termgraph))

SdoTermSource.setQueryGraph(termgraph)
terms = SdoTermSource.getAllTerms()
print ("Terms Count: %s" % len(terms))

from schemapagesprotobuf import sdotermToProtobuf, sdotermToProtobufMsg, sdotermToProtobufText, protobufToMsg, protobufToText

import time,datetime

start = datetime.datetime.now() #debug
for t in terms:
    tic = datetime.datetime.now() #debug
    
    term = SdoTermSource.getTerm(t,expanded=True)
    buf = sdotermToProtobuf(term)
    msg = protobufToMsg(buf)
    txt = protobufToText(buf)
    mfilename = "protomsgs/" + t +".msg"
    tfilename = "protomsgs/" + t +".txt"
    f = open(mfilename,"wb")
    f.write(msg)
    f.close()
    f = open(tfilename,"w")
    f.write(txt)
    f.close()
    
    print("Term: %s - %s" % (t, str(datetime.datetime.now()-tic))) #debug
print ("All terms took %s seconds" % str(datetime.datetime.now()-start)) #debug
    



