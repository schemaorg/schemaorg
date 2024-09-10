#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Common place for all globals to avoid circular dependencies."""

SITENAME = 'Schema.org'
BUILDOPTS = []
TERMS = []
PAGES = []
FILES = []
OUTPUTDIR = 'software/site'
DOCSDOCSDIR = '/docs'
TERMDOCSDIR = '/docs'
HANDLER_TEMPLATE = 'handlers-template.yaml'
HANDLER_FILE = 'handlers.yaml'
RELEASE_DIR = 'software/site/releases'

def hasOpt(opt):
    """Return true if `opt` is among the build options"""
    return opt in BUILDOPTS

def getOutputDir():
    return OUTPUTDIR

def getDocsOutputDir():
    os.path.join(OUTPUTDIR, 'docs')