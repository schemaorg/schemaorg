#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(1)

import os
for path in [os.getcwd(),"Util","SchemaPages","SchemaExamples"]:
  sys.path.insert( 1, path ) #Pickup libs from local  directories

from buildsite import *
from sdotermsource import SdoTermSource
from sdoterm import *
from schemaexamples import SchemaExamples

#Calculate filename for term page
def termFileName(termid):
    pth = [OUTPUTDIR]
    if re.match('^[a-z].*',termid):
        pth.append("/terms/properties/")
    elif re.match('^[0-9A-Z].*',termid):
        pth.append("/terms/types/")
    pth.append(termid[0])
    path = "".join(pth)
    
    checkFilePath(path)    

    elements = [path]
    elements.append('/')
    elements.append(termid)
    elements.append('.html')
    return "".join(elements)
    
#Prep of rendering values for term pages
def termtemplateRender(term,examples):
    #Basic varibles configuring UI
    extra_vars = {
        'title': term.label,
        'menu_sel': "Schemas",
        'home_page': "False",
        'docsdir': TERMDOCSDIR,
        'term': term,
        'examples': examples
    }
    
    return templateRender("terms/TermPage.j2",extra_vars)


def buildTerms(terms):
    all = ["ALL","All","all"]
    for a in all:
        if a in terms:
            terms = SdoTermSource.getAllTerms(supressSourceLinks=True)
            break
    import time,datetime
    start = datetime.datetime.now()
    lastCount = 0
    if len(terms):
        print("\nBuilding term pages...\n")
    for t in terms:
        tic = datetime.datetime.now() #diagnostics
        term = SdoTermSource.getTerm(t,expanded=True)
        if not term:
            print("No such term: %s\n" % t)
            continue

        if term.termType == SdoTerm.REFERENCE: #Don't create pages for reference types
            continue
        examples = SchemaExamples.examplesForTerm(term.id)
        pageout = termtemplateRender(term,examples)
        f = open(termFileName(term.id),"w")
        f.write(pageout)
        f.close()

        #diagnostics ##########################################
        termsofar = len(SdoTermSource.termCache()) #diagnostics
        termscreated = termsofar - lastCount       #diagnostics
        lastCount = termsofar                      #diagnostics
        print("Term: %s (%d) - %s" % (t, termscreated, str(datetime.datetime.now()-tic))) #diagnostics
        #      Note: (%d) = number of individual newly created (not cached) term definitions to
        #            build this expanded definition. ie. All Properties associated with a Type, etc.
    
    if len(terms):
        print()
        print ("All terms took %s seconds" % str(datetime.datetime.now()-start)) #diagnostics
