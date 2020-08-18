#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import os
sys.path.append( os.getcwd() )
sys.path.insert( 1, 'markdown' ) #Pickup libs, rdflib etc., from shipped lib directory

import rdflib
from sdotermsource import *
from sdoterm import *
from localmarkdown import Markdown

import jinja2 
Markdown.setWikilinkCssClass("localLink")
Markdown.setWikilinkPrePath("/")


triplesfile = "data/schemaorg-all-https.nt"
termgraph = rdflib.Graph()
termgraph.parse(triplesfile, format="nt")

print ("loaded %s triples" % len(termgraph))

SdoTermSource.setQueryGraph(termgraph)
#print ("Types Count: %s" % len(SdoTermSource.getAllTypes(expanded=False)))
#print ("Properties Count: %s" % len(SdoTermSource.getAllProperties(expanded=False)))

###################################################
#JINJA INITIALISATION
###################################################

#Setup Jinja2 environment - template(s) location etc.
#TEMPLATESFOLDER = "SchemaPages/templates"
TEMPLATESDIR = "templates"

jenv = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATESDIR),
        extensions=['jinja2.ext.autoescape'], autoescape=True, cache_size=0)

### Template rendering for term definitions
#   term: SDO Term definition either simple (strings only)
#         or expanded (nested definitions for related terms)

def templateRender(term):
    #Basic varibles configuring UI
    tvars = {
        'sitename': "SchemaPages",
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
    
terms = SdoTermSource.getAllTerms()
print("Processing %s terms" % len(terms))

#term = SdoTermSource.getTerm("Permit",expanded=True)
#pageout = templateRender(term)

#print(pageout)

terms = ["Text","DataType","PronounceableText","Thing","about","CreativeWork","MonetaryAmount","LinkRole","EBook","BookFormatType"]


import time,datetime
start = datetime.datetime.now()
lastCount = 0
for t in terms:
    tic = datetime.datetime.now() #diagnostics

    term = SdoTermSource.getTerm(t,expanded=True)
    pageout = templateRender(term)
    filename = "    /" + term.id +".html"
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




