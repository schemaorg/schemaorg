#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sys
if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(1)

# To be executed in the SchemaTerms/example-code/{example} directory
import os
for path in [os.getcwd(),"..","../..","../../.."]: #Adds in current, example-code, and SchemaTerms directory into path
  sys.path.insert( 1, path ) #Pickup libs from local  directories

import rdflib

from sdotermsource import *
from sdoterm import *
from localmarkdown import Markdown

Markdown.setWikilinkCssClass("localLink")
Markdown.setWikilinkPrePath("/")

if VOCABURI.startswith("https://"):
    triplesfile = "../data/schemaorg-all-https.nt"
else:
    triplesfile = "../data/schemaorg-all-http.nt"


termgraph = rdflib.Graph()
termgraph.parse(triplesfile, format="nt")

print ("loaded %s triples" % len(termgraph))

SdoTermSource.setSourceGraph(termgraph)
print ("Types Count: %s" % len(SdoTermSource.getAllTypes(expanded=False)))
print ("Properties Count: %s" % len(SdoTermSource.getAllProperties(expanded=False)))



def showTerm(term,ind=""):
    print("")
    print("%sID: %s" % (ind,term.id))
    print("%sExpanded %s" %(ind,term.expanded))
    print("%sTYPE: %s" % (ind,term.termType))
    print("%sURI: %s" % (ind,term.uri))
    print("%sLABEL: %s" % (ind,term.label))
    print("")
    print("%ssuperPaths: %s" % (ind,term.superPaths))
    print("%scomment: %s" % (ind,term.comment))
    print("%sequivalents: %s" % (ind,term.equivalents))
    print("%sexamples: %s" % (ind,term.examples))
    print("%spending: %s" % (ind,term.pending))
    print("%sretired: %s" % (ind,term.retired))
    print("%ssources: %s" % (ind,term.sources))
    print("%sacknowledgements: %s" % (ind,term.acknowledgements))
    print("%ssubs: %s" % (ind,term.subs))
    print("%ssupers: %s" % (ind,term.supers))
    print("%ssupersededBy: %s" % (ind,term.supersededBy))
    print("%ssupersedes: %s" % (ind,term.supersedes))

    if term.termType == SdoTerm.TYPE or term.termType == SdoTerm.ENUMERATION or term.termType == SdoTerm.DATATYPE:
        if term.expanded:
            print("%sProperties count %s" % (ind,len(term.properties)))
            for p in term.properties:
                showTerm(p,ind=ind +"   ")
            print("%sExpected Type for count %s" % (ind,len(term.expectedTypeFor)))
            for t in term.expectedTypeFor:
                showTerm(t,ind=ind +"   ")
        else:
            print("%sProperties: %s" % (ind,term.properties))
            print("%sExpected Type for: %s" % (ind,term.expectedTypeFor))

    if term.termType == SdoTerm.PROPERTY:
        print("%sDomain includes: %s" % (ind,term.domainIncludes))
        print("%sRange includes: %s" % (ind,term.rangeIncludes))

    if term.termType == SdoTerm.ENUMERATION:
        print("%sEnumeration Members: %s" % (ind,term.enumerationMembers))


    if term.termType == SdoTerm.ENUMERATIONVALUE:
        print("%sParent Enumeration: %s" %  (ind,term.enumerationParent))

    if term.expanded:
        print("%stermStack count: %s " % (ind,len(term.termStack)))
        for t in term.termStack:
            showTerm(t,ind=ind +"...")
    else:
        print("%stermStack: %s " % (ind,term.termStack))

for termname in ["acceptedAnswer","Book"]:
    term = SdoTermSource.getTerm(termname,expanded=True)
    showTerm(term)
