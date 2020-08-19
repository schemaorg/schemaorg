#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
import os
for path in [os.getcwd(),"SchemaPages","SchemaExamples"]:
  sys.path.insert( 1, path ) #Pickup libs from local  directories
  
import glob
import re
import argparse
import rdflib
import jinja2 

from sdotermsource import SdoTermSource
from sdoterm import *
from schemaexamples import SchemaExamples
from localmarkdown import Markdown

parser = argparse.ArgumentParser()
parser.add_argument("-g","--graph", default= [[]],action='append',nargs='*', help="graph file name or glob pattern (repeatable)")
parser.add_argument("-o","--output", help="output site directory (default: ./site | ./testsite)")
parser.add_argument("-p","--pages",default= [],action='append',nargs='*',  help="create docs page(repeatable) - defaults to all docs pages")
parser.add_argument("-t","--testsite", default=False, action='store_true', help="create test site format")
args = parser.parse_args()

SITENAME="SchemaPages"
TEMPLATESDIR = "templates"
TESTSITE=args.testsite
if args.output:
    OUTPUTDIR = args.output
elif TESTSITE:
    OUTPUTDIR = "testsite"
else:
    OUTPUTDIR = "site"
    
TRIPLESFILESGLOB = []
for gr in args.graph:
    TRIPLESFILESGLOB.extend(gr)
PAGES = []
for pgs in args.pages:
    PAGES.extend(pgs)
    
if TESTSITE:
    OUTPUT = "testsite"
    OUTPUTDIR = "testsite/docs"
    DOCSDIR = "."
    HREFSUFFIX=".html" 
    HREFPREFIX="../"
else:
    OUTPUT = "site"
    OUTPUTDIR = "site/docs"
    DOCSDIR = "/docs"
    HREFSUFFIX="" 
    HREFPREFIX="/"


###################################################
#TERMS SOURCE LOAD
###################################################
tripfiles = []
for g in TRIPLESFILESGLOB:
    tripfiles.extend(glob.glob(g))
if not len(tripfiles):
    print("No graph file(s) to load")
    sys.exit()
SdoTermSource.loadSourceGraph(tripfiles)
print ("loaded %s triples - %s terms" % (len(SdoTermSource.sourceGraph()),len(SdoTermSource.getAllTerms())) )


###################################################
#JINJA INITIALISATION
###################################################


jenv = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATESDIR),
        extensions=['jinja2.ext.autoescape'], autoescape=True, cache_size=0)
    

#Utility function (called from templates) to format the <a href=""> links
STRCLASSVAL=None
def sdotermlink(term):
    global STRCLASSVAL
    classval = ""
    if type(term) == str:
        if STRCLASSVAL:
            classval = STRCLASSVAL
        link = term
    elif term.termType == "Reference":
        return '<a href="%s" class="externlink" target="_blank">%s</a>' % (term.uri,term.label)
    else:
        link = term.id
        if term.pending:
            classval = 'class="ext ext-pending"'
        elif term.retired:
            classval = 'class="ext ext-attic"'

    return '<a %s href="%s%s%s" >%s</a>' % (classval,HREFPREFIX,link,HREFSUFFIX,link)
    
jenv.globals.update(sdotermlink=sdotermlink)
    

### Template rendering for term definitions
#   term: SDO Term definition either simple (strings only)
#         or expanded (nested definitions for related terms)

def templateRender(template,extra_vars=None):
    #Basic varibles configuring UI
    tvars = {
        'sitename': SITENAME,
        'home_page': "False",
        'href_prefix': "",
        'docsdir': DOCSDIR + "/"
    }
    if extra_vars:
        tvars.update(extra_vars)
    
    template = jenv.get_template(template)
    return template.render(tvars)

###################################################
#JINJA INITIALISATION - End
###################################################

CHECKEDPATHS =[]
def checkFilePath(path):
    if not path in CHECKEDPATHS:
        CHECKEDPATHS.append(path)
        if not path.startswith('/'):
            path = os.getcwd() + "/" + path
        try:
            os.makedirs(path)
        except OSError as e:
            if not os.path.isdir(path):
                raise e

def fileName(doc):
    checkFilePath(OUTPUTDIR)
    func, filename = PAGELIST.get(doc,None)
    
    return OUTPUTDIR + "/" + filename + ".html"

def schemasPage(page):
    extra_vars = {
        'home_page': "False",
        'title': SITENAME + ' - Schemas',
        'termcounts': SdoTermSource.termCounts()
    }
    return templateRender("docs/Schemas.tpl",extra_vars)
    
    

def homePage(page):
    global STRCLASSVAL
    title = SITENAME
    template = "docs/Home.tpl"
    filt = None
    overrideclassval = None
    if page == "PendingHome":
        title += " - Pending"
        template = "docs/PendingHome.tpl"
        filt = "pending"
        overrideclassval = 'class="ext ext-pending"'
    elif page == "AtticHome":
        title += " - Retired"
        template = "docs/AtticHome.tpl"
        filt="attic"
        overrideclassval = 'class="ext ext-attic"'
    sectionterms={}
    termcount=0
    if filt:
        terms = SdoTermSource.getAllTerms(layer=filt)
        terms = SdoTermSource.termsFromIds(terms)
        print("filt=%s %s" % (filt,len(terms)))
        terms.sort(key = lambda u: (u.category, u.id))
        first = True
        cat = None
        for t in terms:
            if first or t.category != cat:
                first = False
                cat = t.category 
                ttypes = {}
                sectionterms[cat] = ttypes
                ttypes[SdoTerm.TYPE] = []
                ttypes[SdoTerm.PROPERTY] = []
                ttypes[SdoTerm.DATATYPE] = []
                ttypes[SdoTerm.ENUMERATION] = []
                ttypes[SdoTerm.ENUMERATIONVALUE] = []
            if t.termType == SdoTerm.REFERENCE:
                continue
            ttypes[t.termType].append(t.id)
            termcount += 1
    
    extra_vars = {
        'home_page': "True",
        'title': SITENAME,
        'termcount': termcount,
        'sectionterms': sectionterms
    }
    STRCLASSVAL = overrideclassval
    ret =  templateRender(template,extra_vars)
    STRCLASSVAL = None
    return ret



PAGELIST = {"Home": (homePage,"home"),
             "PendingHome": (homePage,"pending.home"),
             "AtticHome": (homePage,"attic.home"),
             "Schemas": (schemasPage,"schemas")
         }
if not len(PAGES):
    PAGES = PAGELIST.keys()

print("Copying docs static files")
cmd = "cp -r docs %s" % OUTPUT
os.system(cmd)


for p in PAGES:
    func, filename = PAGELIST.get(p,None)
    if func:
        content = func(p)
        fn = fileName(p)
        f = open(fn,"w")
        f.write(content)
        f.close()
        print("Created %s" % fn)
    else:
        print("Unknown page name: %s" % p)

"""import time,datetime
start = datetime.datetime.now()
lastCount = 0
for t in TERMS:
    tic = datetime.datetime.now() #diagnostics
    term = SdoTermSource.getTerm(t,expanded=True)

    if term.termType == SdoTerm.REFERENCE: #Don't create pages for reference types
        continue
    examples = SchemaExamples.examplesForTerm(term.id)
    pageout = templateRender(term,examples)
    f = open(fileName(term.id),"w")
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
"""




