#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
import os
for path in [os.getcwd(),"Util","SchemaPages","SchemaExamples"]:
  sys.path.insert( 1, path ) #Pickup libs from local  directories

from buildsitepages import *
from sdotermsource import SdoTermSource
from sdoterm import *
from schemaexamples import SchemaExamples

#Calculate filename for term page
def termFileName(termid):
    pth = [OUTPUTDIR]
    if not TESTSITE: #Local testsite puts term files all in single directory
                      #Production site puts them in several subdirectories
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
    
terms = SdoTermSource.getAllTerms()

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
    if 'ALL' in terms:
        terms = SdoTermSource.getAllTerms(supressSourceLinks=True)

    print("Processing %s terms" % len(terms))
 
    import time,datetime
    start = datetime.datetime.now()
    lastCount = 0
    for t in terms:
        tic = datetime.datetime.now() #diagnostics
        term = SdoTermSource.getTerm(t,expanded=True)

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
