#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
import os
import shutil
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
from schemaversion import *

SITENAME="SchemaPages"
TEMPLATESDIR = "templates"
TRIPLESFILESGLOB = ["data/*.ttl","data/ext/*/*.ttl"]
EXAMPLESFILESGLOB = ["data/*examples.txt","data/ext/*/*examples.txt"]

parser = argparse.ArgumentParser()
parser.add_argument("-c","--clearfirst",default=False, action='store_true', help="clear output directory before creating contents")
parser.add_argument("-d","--docspages",default= [],action='append',nargs='*',  help="create docs page(repeatable) - ALL = all pages")
parser.add_argument("-f","--files",default= [],action='append',nargs='*',  help="create files(repeatable) - ALL = all files")
parser.add_argument("-o","--output", help="output site directory (default: ./site | ./testsite)")
parser.add_argument("-p","--pagesfor",default= [],action='append',nargs='*',  help="create page for term (repeatable) - ALL = all terms")
parser.add_argument("-t","--testsite", default=False, action='store_true', help="create test site format")
args = parser.parse_args()

TERMS = []
for ter in args.pagesfor:
    TERMS.extend(ter)
PAGES = []
for pgs in args.docspages:
    PAGES.extend(pgs)
FILES = []
for fls in args.files:
    FILES.extend(fls)

TESTSITE=args.testsite

if args.output:
    OUTPUTDIR = args.output
elif TESTSITE:
    OUTPUTDIR = "testsite"
else:
    OUTPUTDIR = "site"
DOCSOUTPUTDIR = OUTPUTDIR + "/docs"

def clear():
    if args.clearfirst:
        print("Clearing %s directory" % OUTPUTDIR)
        for root, dirs, files in os.walk(OUTPUTDIR):
            for f in files:
                os.unlink(os.path.join(root, f))
            for d in dirs:
                shutil.rmtree(os.path.join(root, d))

"""if TESTSITE:
    DOCSDOCSDIR = "."
    TERMDOCSDIR = "docs/"
    DOCSHREFSUFFIX=".html" 
    DOCSHREFPREFIX="../"
    TERMHREFSUFFIX=".html" 
    TERMHREFPREFIX=""
"""
if TESTSITE:
    DOCSDOCSDIR = "/docs"
    TERMDOCSDIR = "/docs"
    DOCSHREFSUFFIX=".html" 
    DOCSHREFPREFIX="../"
    TERMHREFSUFFIX=".html" 
    TERMHREFPREFIX=""
else:
    DOCSDOCSDIR = "/docs"
    TERMDOCSDIR = "/docs"
    DOCSHREFSUFFIX="" 
    DOCSHREFPREFIX="/"
    TERMHREFSUFFIX="" 
    TERMHREFPREFIX="/"
    
###################################################
#INITIALISE Directory
###################################################
def initdir():
    print("Building site in '%s' directory" % OUTPUTDIR)
    clear()
    print("Copying docs static files")
    cmd = "cp -r docs %s" % OUTPUTDIR
    os.system(cmd)
    print("Done")
    
###################################################
#MARKDOWN INITIALISE
###################################################
Markdown.setWikilinkCssClass("localLink")
if TESTSITE:
    Markdown.setWikilinkPrePath("./")
        #Local test site uses .html filename in href
    Markdown.setWikilinkPostPath(".html")
    HREFSUFFIX=".html" 
else:
    Markdown.setWikilinkPrePath("/")
        #Production site uses no suffix in link - mapping to file done in server config
    Markdown.setWikilinkPostPath("")
    HREFSUFFIX="" 

###################################################
#TERMS SOURCE LOAD
###################################################
def loadTerms():
    print("Loading triples files")
    tripfiles = []
    for g in TRIPLESFILESGLOB:
        tripfiles.extend(glob.glob(g))
    if not len(tripfiles):
        print("No triples file(s) to load")
    else:
        SdoTermSource.loadSourceGraph(tripfiles)
        print ("loaded %s triples - %s terms" % (len(SdoTermSource.sourceGraph()),len(SdoTermSource.getAllTerms())) )


###################################################
#EXAMPLES SOURCE LOAD
###################################################
def loadExamples():
    print("Loading examples files")
    exfiles = []
    for g in EXAMPLESFILESGLOB:
        exfiles.extend(glob.glob(g))
    if not len(exfiles):
        print("No examples file(s) to load")
    else:
        SchemaExamples.loadExamplesFiles(exfiles)
        print("Loaded %d examples from  %d examples files" % (SchemaExamples.count(),len(exfiles)))

###################################################
#JINJA INITIALISATION
###################################################
jenv = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATESDIR),
        extensions=['jinja2.ext.autoescape'], autoescape=True, cache_size=0)
    

### Template rendering 

def templateRender(template,extra_vars=None):
    #Basic varibles configuring UI
    tvars = {
        'version': getVersion(),
        'versiondate': getCurrentVersionDate(),
        'sitename': SITENAME,
        'TERMHREFPREFIX': TERMHREFPREFIX,
        'TERMHREFSUFFIX': TERMHREFSUFFIX,
        'DOCSHREFPREFIX': DOCSHREFPREFIX,
        'DOCSHREFSUFFIX': DOCSHREFSUFFIX,
        'home_page': "False"
    }
    if extra_vars:
        tvars.update(extra_vars)
    
    template = jenv.get_template(template)
    return template.render(tvars)


###################################################
#JINJA INITIALISATION - End
###################################################
###################################################
#Comment Handling
###################################################

def StripHtmlTags(source):
    if source and len(source) > 0:
        return re.sub('<[^<]+?>', '', source)
    return ""

def ShortenOnSentence(source,lengthHint=250):
    if source and len(source) > lengthHint:
        source = source.strip()
        sentEnd = re.compile('[.!?]')
        sentList = sentEnd.split(source)
        com=""
        count = 0
        while count < len(sentList):
            if(count > 0 ):
                if len(com) < len(source):
                    com += source[len(com)]
            com += sentList[count]
            count += 1
            if count == len(sentList):
                if len(com) < len(source):
                    com += source[len(source) - 1]
            if len(com) > lengthHint:
                if len(com) < len(source):
                    com += source[len(com)]
                break
                
        if len(source) > len(com) + 1:
            com += ".."
        source = com
    return source

#Check / create file paths
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

###################################################
#BUILD INDIVIDUAL TERM PAGES
###################################################
def processTerms():
    global TERMS
    import buildtermpages
    if "ALL" in TERMS:
        TERMS = SdoTermSource.getAllTerms()
    buildtermpages.buildTerms(TERMS)

###################################################
#BUILD DYNAMIC DOCS PAGES
###################################################
def processDocs():
    global PAGES
    import buildocspages
    buildocspages.buildDocs(PAGES)

###################################################
#BUILD FILES
###################################################
def processFiles():
    global FILES
    import buildfiles
    buildfiles.buildFiles(FILES)

if __name__ == '__main__':
    initdir()
    print("Version: %s  Released: %s" % (getVersion(),getCurrentVersionDate()))
    loadTerms()
    loadExamples()
    processTerms()
    processDocs()
    processFiles()

