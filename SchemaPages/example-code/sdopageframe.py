#!/usr/bin/env python2.7

import sys
import os
sys.path.append( os.getcwd() )
sys.path.insert( 1, 'markdown' ) #Pickup libs, rdflib etc., from shipped lib directory

import rdflib

from sdotermsource import *
from sdoterm import *
from localmarkdown import Markdown

Markdown.setWikilinkCssClass("localLink")
Markdown.setWikilinkPrePath("/")


triplesfile = "data/schemaorg-all-https.nt"
termgraph = rdflib.Graph()
termgraph.parse(triplesfile, format="nt")

print ("loaded %s triples" % len(termgraph))

SdoTermSource.setQueryGraph(termgraph)
print ("Types Count: %s" % len(SdoTermSource.getAllTypes(expanded=False)))
print ("Properties Count: %s" % len(SdoTermSource.getAllProperties(expanded=False)))


term = SdoTermSource.getTerm("acceptedAnswer")

print("")
print("TYPE: %s" % term.termType)
print("URI: %s" % term.uri)
print("ID: %s" % term.id)
print("LABEL: %s" % term.label)
print("")
print("superPaths: %s" % term.superPaths)
print("comment: %s" % term.comment)
print("equivalents: %s" % term.equivalents)
print("examples: %s" % term.examples)
print("pending: %s" % term.pending)
print("retired: %s" % term.retired)
print("sources: %s" % term.sources)
print("acknowledgements:" % term.acknowledgements)
print("subs: %s" % term.subs)
print("supers: %s" % term.supers)
print("supersededBy: %s" % term.supersededBy)
print("supersedes: %s" % term.supersedes)
print("termStack: %s" % term.termStack)

for stackElement in term.termStack:
  print("Element: %s" % stackElement)
  
if term.termType == SdoTerm.TYPE or term.termType == SdoTerm.ENUMERATION:
    print("Properties: %s" % term.properties)
    print("All Properties: %s" % term.allproperties)
    print("Expected Type for: %s" % term.expectedTypeFor)
      
if term.termType == SdoTerm.PROPERTY:
    print("Domain includes: %s" % term.domainIncludes)
    print("Range includes: %s" % term.rangeIncludes)

if term.termType == SdoTerm.ENUMERATION:
    print("Enumeration Members: %s" % term.enumerationMembers)
    
    
if term.termType == SdoTerm.ENUMERATIONVALUE:
    print("Parent Enumeration: %s" %  term.enumerationParent)
    
for p in term.properties:
  prop = SdoTermSource.getTerm(p)
  print("Prop: %s.  Pending: %s" % (prop.id,prop.pending))
  print("   Expected Types: %s" % prop.rangeIncludes)
  print("   Comment: %s" % prop.comment)



