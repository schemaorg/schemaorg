#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

""" Tool that handles includes in static html files. """

# Import standard python libraries

import sys
import os
import glob
import re

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software
import software.util.schemaversion as schemaversion
import software.util.fileutils as fileutils
import software.util.convertmd2htmldocs as convertmd2htmldocs


def _getInserts():
    for f_path in glob.glob('./templates/static-doc-inserts/*.html'):
        fn = os.path.basename(f_path).lower()
        fn, _ = os.path.splitext(fn)
        with open(f_path) as input_file:
            indata = input_file.read()
        fn = fn[4:] #drop sdi- from file name
        indata = indata.replace('{{version}}', schemaversion.getVersion())
        indata = indata.replace('{{versiondate}}', schemaversion.getCurrentVersionDate())
        indata = indata.replace('{{docsdir}}', "/docs")
        yield (fn, indata)


class Replacer:

    def __init__(self, destdir):
        self.inserts = dict(_getInserts())
        self.destdir = destdir

    def insertcopy(self, doc, docdata=None):
        """Apply all substitutions defined in self.inserts to a file.

        The resulting output is written to a path in `destdir` based on the path `doc`.

        Parameters:
            doc (str): path to the file to load, only used if docdata is None.
            docdata (str): data to apply the replacement, if empty, data is loaded from doc.
        """
        if not docdata:
            with open(doc) as docfile:
                docdata = docfile.read()

        if re.search('<!-- #### Static Doc Insert', docdata,re.IGNORECASE):
            for sub in self.inserts:
                subpattern = re.compile("<!-- #### Static Doc Insert %s .* -->" % sub,re.IGNORECASE)
                docdata = subpattern.sub(self.inserts.get(sub),docdata,re.IGNORECASE)

            targetfile = os.path.join(self.destdir, os.path.basename(doc))
            with open(targetfile, "w") as outfile:
                outfile.write(docdata)



SRCDIR = './docs'
DESTDIR = './software/site/docs'


def htmlinserts(destdir, indent):
    """Perform susbstitions on all HTML files in DESTDIR."""
    print("%sAdding header/footer templates to all html files" % indent)
    docs = glob.glob(os.path.join(destdir, '*.html'))
    replacer = Replacer(destdir=destdir)
    print(indent, end='')
    for doc in docs:
        replacer.insertcopy(doc)
        print(".", end='')
    print("\n%sAdded" % indent)


def copyFiles(srcdir, destdir, indent=''):
    fileutils.mycopytree(srcdir, destdir)
    print("%sConverting .md docs to html" % indent)
    convertmd2htmldocs.mddocs(DESTDIR, DESTDIR)
    htmlinserts(destdir=destdir, indent=indent)
    print("%sDone" % indent)


if __name__ == '__main__':
    copyFiles(SRCDIR, DESTDIR)
