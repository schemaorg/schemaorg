#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Import libraries that are needed to check version
import os
import sys

if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print('Python version %s.%s not supported version 3.6 or above required - exiting' % (sys.version_info.major,sys.version_info.minor))
    sys.exit(os.EX_CONFIG)

for path in [os.getcwd(),'./software','./software/SchemaTerms','./software/SchemaExamples']:
  sys.path.insert( 1, path ) #Pickup libs from local  directories

if os.path.basename(os.getcwd()) != 'schemaorg':
    print('\nScript should be run from within the "schemaorg" directory! - Exiting\n')
    sys.exit(os.EX_USAGE)

for dir in ['software/util','docs','software/gcloud','data']:
    if not os.path.isdir(dir):
        print('\nRequired directory "%s" not found - Exiting\n' % dir)
        sys.exit(os.EX_CONFIG)

# Import standard python libraries
import argparse
import glob
import re
import shutil
import subprocess
import textutils
import time
import shutil

import rdflib
import jinja2
import fileutils
import runtests
import buildtermpages
import buildocspages

from sdotermsource import SdoTermSource
from sdocollaborators import collaborator
from sdoterm import *
from schemaexamples import SchemaExamples
from localmarkdown import Markdown
from schemaversion import *


SITENAME = 'Schema.org'
TEMPLATESDIR = 'templates'

parser = argparse.ArgumentParser()
parser.add_argument('-a','--autobuild', default=False, action='store_true', help='clear output directory and build all components - overrides all other settings (except -examplesnum)')
parser.add_argument('-c','--clearfirst', default=False, action='store_true', help='clear output directory before creating contents')
parser.add_argument('-d','--docspages', default=[],action='append',nargs='*', help='create docs page(repeatable) - ALL = all pages')
parser.add_argument('-e','--examplesnum', default=False, action='store_true', help='Add missing example ids')
parser.add_argument('-f','--files', default=[], action='append', nargs='*', help='create files(repeatable) - ALL = all files')
parser.add_argument('-o','--output', help='output site directory (default: ./software/site)')
parser.add_argument('-r','--runtests', default=False, action='store_true', help='run test scripts before creating contents')
parser.add_argument('-s','--static', default=False, action='store_true', help='Refresh static docs in site image')
parser.add_argument('-t','--terms', default=[], action='append', nargs='*', help='create page for term (repeatable) - ALL = all terms')
parser.add_argument('-b','--buildoption',default= [],action='append', nargs='*', help='build option(repeatable) - flags to be passed to build code')
parser.add_argument('--rubytests', default=False, action='store_true', help='run the post generation ruby tests')
parser.add_argument('--release', default=False, action='store_true', help='create page for term (repeatable) - ALL = all terms')
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
    OUTPUTDIR = 'software/site'

DOCSOUTPUTDIR = os.path.join(OUTPUTDIR, 'docs')

if args.autobuild or args.release:
    TERMS = ['ALL']
    PAGES = ['ALL']
    FILES = ['ALL']

def hasOpt(opt):
    if opt in BUILDOPTS:
        return True
    return False

def clear():
    if args.clearfirst or args.autobuild:
        print('Clearing %s directory' % OUTPUTDIR)
        if os.path.isdir(OUTPUTDIR):
            for root, dirs, files in os.walk(OUTPUTDIR):
                for f in files:
                    if f != '.gitkeep':
                        os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))

def StartMessage(message):
    column, lines = shutil.get_terminal_size()
    print('▼' * column)
    print(message)
    return time.time()

def EndMessage(message='Done', timestamp=None):
    column, lines = shutil.get_terminal_size()
    if timestamp:
      elapsed = time.time() - timestamp
      message = '%s in %s seconds' % (message, elapsed)
    print(message)
    print('▲' * column)


###################################################
#RUN TESTS
###################################################
def run_all_unit_tests():
    """Run all unit-tests"""

    if not args.runtests and not args.autobuild:
        return
    start = StartMessage("Running test scripts before proceeding..")
    errorcount = runtests.main('./software/tests/')
    EndMessage(timestamp=start)
    if errorcount:
        print('%d test failures' % errorcount)
        sys.exit(errorcount)
    else:
        print('All tests successful!\n')


DOCSDOCSDIR = '/docs'
TERMDOCSDIR = '/docs'
DOCSHREFSUFFIX=''
DOCSHREFPREFIX='/'
TERMHREFSUFFIX=''
TERMHREFPREFIX='/'

###################################################
#INITIALISE Directory
###################################################

HANDLER_TEMPLATE = 'handlers-template.yaml'
HANDLER_FILE = 'handlers.yaml'

def initdir():
    start = StartMessage('Building site in "%s" directory' % OUTPUTDIR)
    fileutils.createMissingDir(OUTPUTDIR)
    clear()
    fileutils.createMissingDir(os.path.join(OUTPUTDIR, 'docs'))
    fileutils.createMissingDir(os.path.join(OUTPUTDIR, 'docs/contributors'))
    fileutils.createMissingDir(os.path.join(OUTPUTDIR, 'empty')) #For apppengine 404 handler
    fileutils.createMissingDir(os.path.join(OUTPUTDIR, 'releases', getVersion()))

    gdir = os.path.join(OUTPUTDIR, 'gcloud')
    fileutils.createMissingDir(gdir)

    print('\nCopying docs static files')
    cmd = ['./software/util/copystaticdocsplusinsert.py']
    subprocess.check_call(cmd)
    print('Done')

    print('\nPreparing GCloud files')
    gcloud_files = glob.glob('software/gcloud/*.yaml')
    for path in gcloud_files:
      shutil.copy(path, gdir)
    print('Done: copied %d files' % len(gcloud_files))
    print('\nCreating %s from %s for version: %s' % (HANDLER_FILE, HANDLER_TEMPLATE, getVersion()))
    with open(os.path.join(gdir, HANDLER_TEMPLATE)) as template_file:
      template_data = template_file.read()
      with open(os.path.join(gdir, HANDLER_FILE), mode='w') as yaml_file:
        handler_data = template_data.replace('{{ver}}', getVersion())
        yaml_file.write(handler_data)
    print('Done\n')


###################################################
#MARKDOWN INITIALISE
###################################################
Markdown.setWikilinkCssClass('localLink')
Markdown.setWikilinkPrePath('/')
Markdown.setWikilinkPostPath('')

###################################################
#TERMS SOURCE LOAD
###################################################
LOADEDTERMS = False
def loadTerms():
    global LOADEDTERMS
    if not LOADEDTERMS:
        LOADEDTERMS = True
        if not SdoTermSource.SOURCEGRAPH:
            print('Loading triples files')
            SdoTermSource.loadSourceGraph('default')
            print ('loaded %s triples - %s terms' % (len(SdoTermSource.sourceGraph()),len(SdoTermSource.getAllTerms())) )
            collaborator.loadContributors()


###################################################
#EXAMPLES SOURCE LOAD
###################################################
LOADEDEXAMPLES = False
def loadExamples():

    global LOADEDEXAMPLES
    if not LOADEDEXAMPLES:
        SchemaExamples.loadExamplesFiles('default')
        print('Loaded %d examples ' % (SchemaExamples.count()))

###################################################
#JINJA INITIALISATION
###################################################
jenv = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATESDIR), autoescape=True, cache_size=0)

def jinjaDebug(text):
    print('Jinja: %s' % text)
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
  #Basic variables configuring UI
  tvars = {
      'local_vars': local_vars,
      'version': getVersion(),
      'versiondate': getCurrentVersionDate(),
      'sitename': SITENAME,
      'TERMHREFPREFIX': TERMHREFPREFIX,
      'TERMHREFSUFFIX': TERMHREFSUFFIX,
      'DOCSHREFPREFIX': DOCSHREFPREFIX,
      'DOCSHREFSUFFIX': DOCSHREFSUFFIX,
      'home_page': 'False'
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
        # os.path.join ignores the first argument if `path` is absolute.
        path = os.path.join(os.getcwd(), path)
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
    if len(TERMS):
        print('Building term definition pages\n')
        loadTerms()
        loadExamples()
    buildtermpages.buildTerms(TERMS)

###################################################
#BUILD DYNAMIC DOCS PAGES
###################################################
def processDocs():
    global PAGES

    if len(PAGES):
        print('Building dynamic documentation pages\n')
        loadTerms()
        buildocspages.buildDocs(PAGES)

###################################################
#BUILD FILES
###################################################
def processFiles():
    global FILES
    import buildfiles
    if len(FILES):
        print('Building supporting files\n')
        loadTerms()
        loadExamples()
        buildfiles.buildFiles(FILES)

###################################################
#Run ruby tests
###################################################

RELEASE_DIR = 'software/site/releases'

def runRubyTests():
    print('Setting up LATEST')
    src_dir = os.path.join(os.getcwd(), RELEASE_DIR, getVersion())
    dst_dir = os.path.join(os.getcwd(), RELEASE_DIR, 'LATEST')
    os.symlink(src_dir, dst_dir)
    cmd = ['bundle', 'exec', 'rake']
    cwd = os.path.join(os.getcwd(), 'software/scripts')
    print('Running tests')
    subprocess.check_call(cmd, cwd=cwd)
    print('Cleaning up %s' % dst_dir)
    os.unlink(dst_dir)
    print('Done')

###################################################
#COPY CREATED RELEASE FILES into Data area
###################################################


def copyReleaseFiles():
    print('Copying release files for version %s to data/releases' % getVersion() )
    SRCDIR = os.path.join(os.getcwd(), RELEASE_DIR, getVersion())
    DESTDIR = os.path.join(os.getcwd(), 'data/releases/', getVersion())
    fileutils.mycopytree(SRCDIR, DESTDIR)
    cmd = ['git', 'add', DESTDIR]
    subprocess.check_call(cmd)

if __name__ == '__main__':
    print('Version: %s  Released: %s' % (getVersion(),getCurrentVersionDate()))
    if args.release:
        args.autobuild = True
        print('BUILDING RELEASE VERSION')
        time.sleep(2)
        print()
    if args.examplesnum or args.release or args.autobuild:
        print('Checking Examples for assigned identifiers')
        time.sleep(2)
        print()
        cmd = ['./software/SchemaExamples/utils/assign-example-ids.py']
        subprocess.check_call(cmd)
        print()
    initdir()
    run_all_unit_tests()
    processTerms()
    processDocs()
    processFiles()
    if args.rubytests:
      runRubyTests()
    if args.release:
        copyReleaseFiles()


