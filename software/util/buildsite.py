#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(1)

import os
import time
import shutil
for path in [os.getcwd(),"./software","./software/SchemaTerms","./software/SchemaExamples"]:
  sys.path.insert( 1, path ) #Pickup libs from local  directories

if os.path.basename(os.getcwd()) != "schemaorg":
    print("\nScript should be run from within the 'schemaorg' directory! - Exiting\n")
    sys.exit(1)

for dir in ["software/util","docs","software/gcloud","data"]:
    if not os.path.isdir(dir):
        print("\nRequired directory '%s' not found - Exiting\n" % dir)
        sys.exit(1)


import glob
import re
import argparse
import rdflib
import jinja2

import textutils
from sdotermsource import SdoTermSource
from sdocollaborators import collaborator
from sdoterm import *
from schemaexamples import SchemaExamples
from localmarkdown import Markdown
from schemaversion import *

SITENAME="Schema.org"
TEMPLATESDIR = "templates"

parser = argparse.ArgumentParser()
parser.add_argument("-a","--autobuild",default=False, action='store_true', help="clear output directory and build all components - overrides all other settings (except -examplesnum)")
parser.add_argument("-c","--clearfirst",default=False, action='store_true', help="clear output directory before creating contents")
parser.add_argument("-d","--docspages",default= [],action='append',nargs='*',  help="create docs page(repeatable) - ALL = all pages")
parser.add_argument("-e","--examplesnum",default=False, action='store_true',  help="Add missing example ids")
parser.add_argument("-f","--files",default= [],action='append',nargs='*',  help="create files(repeatable) - ALL = all files")
parser.add_argument("-o","--output", help="output site directory (default: ./software/site)")
parser.add_argument("-r","--runtests",default=False, action='store_true', help="run test scripts before creating contents")
parser.add_argument("-s","--static",default=False, action='store_true',  help="Refresh static docs in site image")
parser.add_argument("-t","--terms",default= [],action='append',nargs='*',  help="create page for term (repeatable) - ALL = all terms")
parser.add_argument("-b","--buildoption",default= [],action='append',nargs='*',  help="build option(repeatable) - flags to be passed to build code")
parser.add_argument("--release",default=False, action='store_true',  help="create page for term (repeatable) - ALL = all terms")
args = parser.parse_args()

BUILDOPTS = []
for op in args.buildoption:
    BUILDOPTS.extend(op)

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
    OUTPUTDIR = "software/site"
DOCSOUTPUTDIR = OUTPUTDIR + "/docs"

if args.autobuild or args.release:
    TERMS = ["ALL"]
    PAGES = ["ALL"]
    FILES = ["ALL"]

def hasOpt(opt):
    if opt in BUILDOPTS:
        return True
    return False

def clear():
    if args.clearfirst or args.autobuild:
        print("Clearing %s directory" % OUTPUTDIR)
        if os.path.isdir(OUTPUTDIR):
            for root, dirs, files in os.walk(OUTPUTDIR):
                for f in files:
                    if f != ".gitkeep":
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
        errorcount = runtests.main('./software/tests/')
        if errorcount:
            print("Errors returned: %d" % errorcount)
            sys.exit(errorcount)
        else:
            print("Tests successful!\n")

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
    createMissingDir(OUTPUTDIR + "/docs/contributors")
    createMissingDir(OUTPUTDIR + "/releases/%s" % getVersion())

    gdir = OUTPUTDIR + "/gcloud"
    createMissingDir(gdir)

    print("\nCopying docs static files")
    cmd = "./software/util/copystaticdocsplusinsert.py"
    os.system(cmd)
    print("Done")

    print("\nPreparing GCloud files")
    cmd = "cp software/gcloud/*.yaml %s" % gdir
    os.system(cmd)
    print("Files copied")

    cmd = 'sed "s/{{ver}}/%s/g" %s/handlers-template.yaml > %s/handlers.yaml' % (getVersion(),gdir,gdir)
    print("Created handlers.yaml for version: %s" % getVersion())
    os.system(cmd)
    print("Done\n")

from shutil import *
def mycopytree(src, dst, symlinks=False, ignore=None):
    #copes with already existing directories
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    if not os.path.isdir(dst):
        os.makedirs(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                mycopytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as err:
            errors.extend(err.args[0])
        except EnvironmentError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise Error (errors)


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
        if not SdoTermSource.SOURCEGRAPH:
            print("Loading triples files")
            SdoTermSource.loadSourceGraph("default")
            print ("loaded %s triples - %s terms" % (len(SdoTermSource.sourceGraph()),len(SdoTermSource.getAllTerms())) )
            collaborator.loadContributors()


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
jenv = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATESDIR), autoescape=True, cache_size=0)

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

def templateRender(template_path, extra_vars=None, template_instance=None):
  """Render a page template.

  Returns: the generated page.
  """
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

  template = template_instance or jenv.get_template(template_path)
  return template.render(tvars)

###################################################
#JINJA INITIALISATION - End
###################################################

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
###################################################
#COPY CREATED RELEASE FILES into Data area
###################################################
def copyReleaseFiles():
    print("Copying release files for version %s to data/releases" % getVersion() )
    SRCDIR = './software/site/releases/%s' % getVersion()
    DESTDIR = './data/releases/%s' % getVersion()
    mycopytree(SRCDIR,DESTDIR)
    cmd= "git add %s" % DESTDIR
    os.system(cmd)


if __name__ == '__main__':
    print("Version: %s  Released: %s" % (getVersion(),getCurrentVersionDate()))
    if args.release:
        args.autobuild = True
        print("BUILDING RELEASE VERSION")
        time.sleep(2)
        print()
    if args.examplesnum or args.release or args.autobuild:
        print("Checking Examples for assigned identifiers")
        time.sleep(2)
        print()
        cmd ="./software/SchemaExamples/utils/assign-example-ids.py"
        os.system(cmd)
        print()
    initdir()
    runtests()
    processTerms()
    processDocs()
    processFiles()
    if args.release:
        copyReleaseFiles()

