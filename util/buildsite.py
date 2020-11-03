#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(1)

import os
import shutil
for path in [os.getcwd(),"SchemaTerms","SchemaExamples"]:
  sys.path.insert( 1, path ) #Pickup libs from local  directories
  
if os.path.basename(os.getcwd()) != "schemaorg":
    print("\nScript should be run from within the 'schemaorg' directory! - Exiting\n")
    sys.exit(1)

for dir in ["util","docs","gcloud","data"]:
    if not os.path.isdir(dir):
        print("\nRequired directory '%s' not found - Exiting\n" % dir)
        sys.exit(1)


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

SITENAME="Schema.org"
TEMPLATESDIR = "templates"

parser = argparse.ArgumentParser()
parser.add_argument("-a","--autobuild",default=False, action='store_true', help="clear output directory and build all components - overrides all other settings")
parser.add_argument("-c","--clearfirst",default=False, action='store_true', help="clear output directory before creating contents")
parser.add_argument("-d","--docspages",default= [],action='append',nargs='*',  help="create docs page(repeatable) - ALL = all pages")
parser.add_argument("-f","--files",default= [],action='append',nargs='*',  help="create files(repeatable) - ALL = all files")
parser.add_argument("-o","--output", help="output site directory (default: ./site)")
parser.add_argument("-r","--runtests",default=False, action='store_true', help="run test scripts before creating contents")
parser.add_argument("-s","--static",default=False, action='store_true',  help="Refresh static docs in site image")
parser.add_argument("-t","--terms",default= [],action='append',nargs='*',  help="create page for term (repeatable) - ALL = all terms")
args = parser.parse_args()

TERMS = []
for ter in args.terms:
    TERMS.extend(ter)
PAGES = []
for pgs in args.docspages:
    PAGES.extend(pgs)
FILES = []
for fls in args.files:
    FILES.extend(fls)

if args.output:
    OUTPUTDIR = args.output
else:
    OUTPUTDIR = "site"
DOCSOUTPUTDIR = OUTPUTDIR + "/docs"

if args.autobuild:
    TERMS = ["ALL"]
    PAGES = ["ALL"]
    FILES = ["ALL"]

def clear():
    if args.clearfirst or args.autobuild:
        print("Clearing %s directory" % OUTPUTDIR)
        if os.path.isdir(OUTPUTDIR):
            for root, dirs, files in os.walk(OUTPUTDIR):
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))

###################################################
#RUN TESTS
###################################################
def runtests():
    import runtests
    if args.runtests or args.autobuild:
        print("Running test scripts before proceeding...\n")
        errorcount = runtests.main('./tests/')
        if errorcount:
            print("Errors returned: %d" % errorcount)
            sys.exit(errorcount)
        else:
            print("Tests succesful!\n")

DOCSDOCSDIR = "/docs"
TERMDOCSDIR = "/docs"
DOCSHREFSUFFIX="" 
DOCSHREFPREFIX="/"
TERMHREFSUFFIX="" 
TERMHREFPREFIX="/"
    
###################################################
#INITIALISE Directory
###################################################
def createMissingDir(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

def initdir():
    print("Building site in '%s' directory" % OUTPUTDIR)
    createMissingDir(OUTPUTDIR)
    clear()
    createMissingDir(OUTPUTDIR + "/docs")
    gdir = OUTPUTDIR + "/gcloud"
    createMissingDir(gdir)

    print("\nCopying docs static files")
    cmd = "./util/copystaticdocs+insert.py"
    os.system(cmd)
    print("Done")

    print("\nPreparing GCloud files")
    cmd = "cp gcloud/*.yaml %s" % gdir
    os.system(cmd)
    print("Files copied")

    cmd = 'sed "s/{{ver}}/%s/g" %s/handlers-template.yaml > %s/handlers.yaml' % (getVersion(),gdir,gdir)
    print("Created handlers.yaml for version: %s" % getVersion())
    os.system(cmd)
    print("Done\n")
    
###################################################
#MARKDOWN INITIALISE
###################################################
Markdown.setWikilinkCssClass("localLink")
Markdown.setWikilinkPrePath("/")
Markdown.setWikilinkPostPath("")

###################################################
#TERMS SOURCE LOAD
###################################################
LOADEDTERMS = False
def loadTerms():
    global LOADEDTERMS
    if not LOADEDTERMS:
        LOADEDTERMS = True
        print("Loading triples files")
        SdoTermSource.loadSourceGraph("default")
        print ("loaded %s triples - %s terms" % (len(SdoTermSource.sourceGraph()),len(SdoTermSource.getAllTerms())) )


###################################################
#EXAMPLES SOURCE LOAD
###################################################
LOADEDEXAMPLES = False
def loadExamples():

    global LOADEDEXAMPLES
    if not LOADEDEXAMPLES:
        SchemaExamples.loadExamplesFiles("default")
        print("Loaded %d examples " % (SchemaExamples.count()))

###################################################
#JINJA INITIALISATION
###################################################
jenv = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATESDIR),
        extensions=['jinja2.ext.autoescape'], autoescape=True, cache_size=0)
    
def jinjaDebug(text):
    print("Jinja: %s" % text)
    return ''

jenv.filters['debug']=jinjaDebug

local_vars = {}
def set_local_var(local_vars, name, value):
  local_vars[name] = value
  return ''
jenv.globals['set_local_var'] = set_local_var


### Template rendering 

def templateRender(template,extra_vars=None):
    #Basic varibles configuring UI
    tvars = {
        'local_vars': local_vars,
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
    import buildtermpages
    global TERMS
    if len(TERMS):
        print("Building term definition pages\n")
        loadTerms()
        loadExamples()
    buildtermpages.buildTerms(TERMS)

###################################################
#BUILD DYNAMIC DOCS PAGES
###################################################
def processDocs():
    global PAGES
    import buildocspages
    if len(PAGES):
        print("Building dynamic documentation pages\n")
        loadTerms()
        buildocspages.buildDocs(PAGES)

###################################################
#BUILD FILES
###################################################
def processFiles():
    global FILES
    import buildfiles
    if len(FILES):
        print("Building supporting files\n")
        loadTerms()
        loadExamples()
        buildfiles.buildFiles(FILES)

if __name__ == '__main__':
    print("Version: %s  Released: %s" % (getVersion(),getCurrentVersionDate()))
    initdir()
    if args.autobuild:
        print("Checking Examples for assigned identifiers")
        cmd ="./SchemaExamples/utils/assign-example-ids.py"
        os.system(cmd)

    runtests()
    processTerms()
    processDocs()
    processFiles()

