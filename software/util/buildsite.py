#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Import standard python libraries
import argparse
import glob
import os
import re
import shutil
import subprocess
import sys
import time
import rdflib
import logging
import colorama

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software

import software.util.buildfiles as buildfiles
import software.util.buildocspages as buildocspages
import software.util.buildtermpages as buildtermpages
import software.util.copystaticdocsplusinsert as copystaticdocsplusinsert
import software.util.fileutils as fileutils
import software.util.runtests as runtests_lib
import software.util.schemaglobals as schemaglobals
import software.util.schemaversion as schemaversion
import software.util.textutils as textutils

import software.SchemaExamples.schemaexamples as schemaexamples
import software.SchemaExamples.utils.assign_example_ids
import software.SchemaTerms.localmarkdown
import software.SchemaTerms.sdocollaborators as sdocollaborators
import software.SchemaTerms.sdotermsource as sdotermsource

log = logging.getLogger(__name__)

class PrettyLogFormatter(logging.Formatter):
    """Helper class to format the log messages from the various parts of the project."""

    COLORS = {
        'WARNING': colorama.Fore.YELLOW,
        'INFO': colorama.Fore.CYAN,
        'DEBUG': colorama.Fore.BLUE,
        'CRITICAL': colorama.Fore.MAGENTA,
        'ERROR': colorama.Fore.RED,
    }

    def __init__(self, use_color=True):
        logging.Formatter.__init__(self, fmt='%(levelname)s %(name)s: %(message)s')
        self.use_color = use_color

    @classmethod
    def _computeLevelName(cls, record):
        lower_msg = record.getMessage().casefold()
        if lower_msg == 'done' or lower_msg[:5] == 'done:':
            return colorama.Fore.LIGHTGREEN_EX + record.levelname + colorama.Fore.RESET
        if record.levelname in cls.COLORS:
            return cls.COLORS[record.levelname] + record.levelname + colorama.Fore.RESET
        return record.levelname

    @classmethod
    def _computeName(cls, record):
        components = record.name.split('.')
        return colorama.Style.DIM + components[-1] + colorama.Style.RESET_ALL

    def format(self, record):
        if self.use_color:
            record.levelname = self.__class__._computeLevelName(record)
            record.name = self.__class__._computeName(record)
        return logging.Formatter.format(self, record)


def initialize():
    """Initialize various systems, returns the args object"""
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


    for op in args.buildoption:
        schemaglobals-BUILDOPTS.extend(op)

    for ter in args.terms:
        schemaglobals.TERMS.extend(ter)

    for pgs in args.docspages:
        schemaglobals.PAGES.extend(pgs)

    for fls in args.files:
        schemaglobals.FILES.extend(fls)

    if args.output:
        schemaglobals.OUTPUTDIR = args.output

    if args.autobuild or args.release:
        schemaglobals.TERMS = ['ALL']
        schemaglobals.PAGES = ['ALL']
        schemaglobals.FILES = ['ALL']

    ###################################################
    #MARKDOWN INITIALISE
    ###################################################
    software.SchemaTerms.localmarkdown.Markdown.setWikilinkCssClass('localLink')
    software.SchemaTerms.localmarkdown.Markdown.setWikilinkPrePath('/')
    software.SchemaTerms.localmarkdown.Markdown.setWikilinkPostPath('')

    handler = logging.StreamHandler(sys.stdout)
    formatter = PrettyLogFormatter(use_color=os.isatty(sys.stdout.fileno()))
    handler.setFormatter(formatter)

    root_log = logging.getLogger()
    root_log.handlers = [handler]

    return args


def clear():
    if args.clearfirst or args.autobuild:
        log.info('Clearing %s directory' % schemaglobals.OUTPUTDIR)
        if os.path.isdir(schemaglobals.OUTPUTDIR):
            for root, dirs, files in os.walk(schemaglobals.OUTPUTDIR):
                for f in files:
                    if f != '.gitkeep':
                        os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))

###################################################
#RUN TESTS
###################################################
def runtests():
    if args.runtests or args.autobuild:
        log.info('Running test scripts before proceeding…')
        errorcount = runtests_lib.main('./software/tests/')
        if errorcount:
            log.error('Errors returned: %d' % errorcount)
            sys.exit(errorcount)
        else:
            log.info('Done: Tests successful!')


###################################################
#INITIALISE Directory
###################################################

def initdir(output_dir, handler_path):
    log.info('Building site in "%s" directory' % output_dir)
    fileutils.createMissingDir(output_dir)
    clear()
    fileutils.createMissingDir(os.path.join(output_dir, 'docs'))
    fileutils.createMissingDir(os.path.join(output_dir, 'docs/contributors'))
    fileutils.createMissingDir(os.path.join(output_dir, 'empty')) #For apppengine 404 handler
    fileutils.createMissingDir(os.path.join(output_dir, 'releases', schemaversion.getVersion()))

    gdir = os.path.join(output_dir, 'gcloud')
    fileutils.createMissingDir(gdir)

    log.info('Copying docs static files')
    copystaticdocsplusinsert.copyFiles('./docs', './software/site/docs')
    log.info('Done')

    log.info('Preparing GCloud files')
    gcloud_files = glob.glob('software/gcloud/*.yaml')
    for path in gcloud_files:
      shutil.copy(path, gdir)
    log.info('Done: copied %d files' % len(gcloud_files))
    log.info('Creating %s from %s for version: %s' %
        (handler_path, schemaglobals.HANDLER_TEMPLATE, schemaversion.getVersion()))
    with open(os.path.join(gdir, schemaglobals.HANDLER_TEMPLATE)) as template_file:
      template_data = template_file.read()
      with open(os.path.join(gdir, handler_path), mode='w') as yaml_file:
        handler_data = template_data.replace('{{ver}}', schemaversion.getVersion())
        yaml_file.write(handler_data)
    log.info('Done')


###################################################
#TERMS SOURCE LOAD
###################################################
LOADEDTERMS = False
def loadTerms():
    global LOADEDTERMS
    if not LOADEDTERMS:
        LOADEDTERMS = True
        if not sdotermsource.SdoTermSource.SOURCEGRAPH:
            log.info('Loading triples files')
            sdotermsource.SdoTermSource.loadSourceGraph('default')
            log.info('Done: loaded %s triples - %s terms' % (len(
                sdotermsource.SdoTermSource.sourceGraph()),
                len(sdotermsource.SdoTermSource.getAllTerms())) )
            sdocollaborators.collaborator.loadContributors()

###################################################
#BUILD INDIVIDUAL TERM PAGES
###################################################
def processTerms(terms):
    if len(terms):
        log.info('Building term definition pages')
        loadTerms()
        schemaexamples.SchemaExamples.loaded()
        log.info('Done')
    buildtermpages.buildTerms(terms)

###################################################
#BUILD DYNAMIC DOCS PAGES
###################################################
def processDocs(pages):
    if len(pages):
        log.info('Building dynamic documentation pages')
        loadTerms()
        buildocspages.buildDocs(pages)
        log.info('Done')

###################################################
#BUILD FILES
###################################################
def processFiles(files):
    if len(files):
        log.info('Building supporting files')
        loadTerms()
        schemaexamples.SchemaExamples.loaded()
        buildfiles.buildFiles(files)
        log.info('Done')

###################################################
#Run ruby tests
###################################################

def runRubyTests(release_dir):
    log.info('Setting up LATEST')
    version = schemaversion.getVersion()
    src_dir = os.path.join(os.getcwd(), release_dir, version)
    dst_dir = os.path.join(os.getcwd(), release_dir, 'LATEST')
    os.symlink(src_dir, dst_dir)
    cmd = ['bundle', 'exec', 'rake']
    cwd = os.path.join(os.getcwd(), 'software/scripts')
    log.info('Running tests')
    subprocess.check_call(cmd, cwd=cwd)
    log.info('Cleaning up %s' % dst_dir)
    os.unlink(dst_dir)
    log.info('Done')

###################################################
#COPY CREATED RELEASE FILES into Data area
###################################################


def copyReleaseFiles(release_dir):
    version = schemaversion.getVersion()
    log.info('Copying release files for version %s to data/releases' % version)
    srcdir = os.path.join(os.getcwd(), release_dir, version)
    destdir = os.path.join(os.getcwd(), 'data/releases/', version)
    fileutils.mycopytree(srcdir, destdir)
    cmd = ['git', 'add', destdir]
    subprocess.check_call(cmd)
    log.info('Done')


###################################################
# Main program
###################################################

if __name__ == '__main__':
    args = initialize()

    software.CheckWorkingDirectory()
    log.info('Version: %s  Released: %s' % (schemaversion.getVersion(), schemaversion.getCurrentVersionDate()))
    if args.release:
        args.autobuild = True
        log.info('BUILDING RELEASE VERSION')
    if args.examplesnum or args.release or args.autobuild:
        log.info('Checking Examples for assigned identifiers')
        software.SchemaExamples.utils.assign_example_ids.AssignExampleIds()
        log.info('Done')
    initdir(output_dir=schemaglobals.OUTPUTDIR, handler_path=schemaglobals.HANDLER_FILE)
    runtests()
    processTerms(terms=schemaglobals.TERMS)
    processDocs(pages=schemaglobals.PAGES)
    processFiles(files=schemaglobals.FILES)
    if args.rubytests:
        runRubyTests(release_dir=schemaglobals.RELEASE_DIR)
    if args.release:
        copyReleaseFiles(release_dir=schemaglobals.RELEASE_DIR)


