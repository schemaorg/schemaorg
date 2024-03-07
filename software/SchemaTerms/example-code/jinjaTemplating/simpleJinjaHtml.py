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

import rdflib
from sdotermsource import *
from sdoterm import *
from localmarkdown import Markdown

import jinja2 
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

###################################################
#JINJA INITIALISATION
###################################################

#Setup Jinja2 environment - template(s) location etc.
#TEMPLATESFOLDER = "SchemaTerms/templates"
TEMPLATESDIR = "templates"

jenv = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATESDIR),
        extensions=['jinja2.ext.autoescape'], autoescape=True, cache_size=0)

### Template rendering for term definitions
#   term: SDO Term definition either simple (strings only)
#         or expanded (nested definitions for related terms)

def templateRender(term):
    #Basic variables configuring UI
    tvars = {
        'sitename': "SchemaTerms",
        'menu_sel': "Schemas",
        'home_page': "False",
        'href_prefix': "",
        'term': term
    }
    
    page=None

    if term.expanded:
      if term.termType == SdoTerm.TYPE:
          page = "expanded/TypePageEx.tpl"
      elif term.termType == SdoTerm.PROPERTY:
          page = "expanded/PropertyPageEx.tpl"
      elif term.termType == SdoTerm.ENUMERATION:
          page = "expanded/EnumerationPageEx.tpl"
      elif term.termType == SdoTerm.ENUMERATIONVALUE:
          page = "expanded/EnumerationValuePageEx.tpl"
      elif term.termType == SdoTerm.DATATYPE:
          page = "expanded/DataTypePageEx.tpl"
    else:
      if term.termType == SdoTerm.TYPE:
          page = "simple/TypePage.tpl"
      elif term.termType == SdoTerm.PROPERTY:
          page = "simple/PropertyPage.tpl"
      elif term.termType == SdoTerm.ENUMERATION:
          page = "simple/EnumerationPage.tpl"
      elif term.termType == SdoTerm.ENUMERATIONVALUE:
          page = "simple/EnumerationValuePage.tpl"
      elif term.termType == SdoTerm.DATATYPE:
          page = "simple/DataTypePage.tpl"
    if not page:
        print("Invalid term type: %s" % term.termType)
        return
 
    template = jenv.get_template(page)
    return template.render(tvars)

###################################################
#JINJA INITIALISATION - End
###################################################
    
#terms = SdoTermSource.getAllTerms()

terms = ["DataType","about","Action","CreativeWork","MonetaryAmount","PronounceableText","Thing","Text","LinkRole","EBook","BookFormatType"]
print("Processing %s terms" % len(terms))


import time,datetime
start = datetime.datetime.now()
lastCount = 0
for t in terms:
    tic = datetime.datetime.now() #diagnostics

    term = SdoTermSource.getTerm(t,expanded=True)
    pageout = templateRender(term)
    filename = "html/" + term.id +".html"
    f = open(filename,"w")
    f.write(pageout)
    f.close()

    #diagnostics ##########################################
    termsofar = len(SdoTermSource.termCache()) #diagnostics
    termscreated = termsofar - lastCount       #diagnostics
    lastCount = termsofar                      #diagnostics
    print("Term: %s (%d) - %s" % (t, termscreated, str(datetime.datetime.now()-tic))) #diagnostics
    #      Note: (%d) = number of individual newly created (not cached) term definitions to
    #            build this expanded definition. ie. All Properties associated with a Type, etc.
    
print()
print ("All terms took %s seconds" % str(datetime.datetime.now()-start)) #diagnostics




