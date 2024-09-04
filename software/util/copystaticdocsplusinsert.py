#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

""" Tool that handles includes in static html files. """

import sys
if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(os.EX_SOFTWARE)

import os
import glob
import re

for path in [os.getcwd(),"software/SchemaTerms","software/SchemaExamples","software/util"]:
  sys.path.insert(1, path) #Pickup libs from local directories

import fileutils

if os.path.basename(os.getcwd()) != "schemaorg":
    print("\nScript should be run from within the 'schemaorg' directory! - Exiting\n")
    sys.exit(os.EX_DATAERR)

for directory in ("software/util","docs","software/site","templates/static-doc-inserts"):
    if not os.path.isdir(directory):
        print("\nRequired directory '%s' not found - Exiting\n" % directory)
        sys.exit(os.EX_NOINPUT)

from shutil import *
from schemaversion import *
import convertmd2htmldocs


INSERTS = {}
for f_path in glob.glob('./templates/static-doc-inserts/*.html'):
    fn = os.path.basename(f_path).lower()
    fn, _ = os.path.splitext(fn)
    with open(f_path) as input_file:
        indata = input_file.read()
    fn = fn[4:] #drop sdi- from file name
    indata = indata.replace('{{version}}', getVersion())
    indata = indata.replace('{{versiondate}}', getCurrentVersionDate())
    indata = indata.replace('{{docsdir}}', "/docs")
    INSERTS[fn] = indata

SRCDIR = './docs'
DESTDIR = './software/site/docs'

def copydocs():
    fileutils.mycopytree(SRCDIR, DESTDIR)

def htmlinserts():
    """Perform susbstitions on all HTML files in DESTDIR."""
    print("\tAdding header/footer templates to all html files")
    docs = glob.glob(os.path.join(DESTDIR, '*.html'))
    for doc in docs:
        insertcopy(doc)
        print(".", end='')
    print("\n\tAdded")

def insertcopy(doc, docdata=None):
    """Apply all substitutions defined in INSERTS to a file.

    The resulting output is written to a path in DESTDIR based on the path `doc`.

    Parameters:
      doc (str): path to the file to load, only used if docdata is None.
      docdata (str): data to apply the replacement, if empty, data is loaded from doc.
   """
    if not docdata:
        with open(doc) as docfile:
            docdata = docfile.read()

    if re.search('<!-- #### Static Doc Insert', docdata,re.IGNORECASE):
        for sub in INSERTS:
            subpattern = re.compile("<!-- #### Static Doc Insert %s .* -->" % sub,re.IGNORECASE)
            docdata = subpattern.sub(INSERTS.get(sub),docdata,re.IGNORECASE)

        targetfile = os.path.join(DESTDIR, os.path.basename(doc))
        with open(targetfile, "w") as outfile:
            outfile.write(docdata)
        #print("adding inserts to: " + targetfile)



if __name__ == '__main__':
    copydocs()
    print("\tConverting .md docs to html")
    convertmd2htmldocs.mddocs(DESTDIR, DESTDIR)
    htmlinserts()
    print("Done")
    os.sys.exit(0)