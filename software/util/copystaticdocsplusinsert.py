#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Tool that handles includes in static html files."""

# Import standard python libraries

import sys
import os
import glob
import re
import logging
from typing import Dict, Generator, Tuple, Optional, List


# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software
import software.util.schemaversion as schemaversion
import software.util.fileutils as fileutils
import software.util.convertmd2htmldocs as convertmd2htmldocs

log: logging.Logger = logging.getLogger(__name__)


def _getInserts() -> Generator[Tuple[str, str], None, None]:
    for f_path in glob.glob("./templates/static-doc-inserts/*.html"):
        fn: str = os.path.basename(f_path).lower()
        fn, _ = os.path.splitext(fn)
        with open(f_path) as input_file:
            indata: str = input_file.read()
        fn = fn[4:]  # drop sdi- from file name
        indata = indata.replace("{{version}}", schemaversion.getVersion())
        indata = indata.replace(
            "{{versiondate}}", str(schemaversion.getCurrentVersionDate())
        )
        indata = indata.replace("{{docsdir}}", "/docs")
        yield (fn, indata)


class Replacer:
    def __init__(self, destdir: str) -> None:
        self.inserts: Dict[str, str] = dict(_getInserts())
        self.destdir: str = destdir

    def insertcopy(self, doc: str, docdata: Optional[str] = None) -> None:
        """Apply all substitutions defined in self.inserts to a file.

        The resulting output is written to a path in `destdir` based on the path `doc`.

        Parameters:
            doc (str): path to the file to load, only used if docdata is None.
            docdata (str): data to apply the replacement, if empty, data is loaded from doc.
        """
        if not docdata:
            with open(doc) as docfile:
                docdata = docfile.read()

        if re.search("<!-- #### Static Doc Insert", docdata, re.IGNORECASE):
            for sub, insert_content in self.inserts.items():
                subpattern: re.Pattern = re.compile(
                    f"<!-- #### Static Doc Insert {sub} .* -->", re.IGNORECASE
                )
                docdata = subpattern.sub(insert_content, docdata)

            targetfile: str = os.path.join(self.destdir, os.path.basename(doc))
            with open(targetfile, "w") as outfile:
                outfile.write(docdata)


SRCDIR: str = "./docs"
DESTDIR: str = "./software/site/docs"


def htmlinserts(destdir: str) -> None:
    """Perform susbstitions on all HTML files in DESTDIR."""
    log.info("Adding header/footer templates to all html files")
    docs: List[str] = sorted(glob.glob(os.path.join(destdir, "*.html")))
    replacer: Replacer = Replacer(destdir=destdir)
    for doc in docs:
        replacer.insertcopy(doc)
    log.info(f"Added to {len(docs)} files")


def copyFiles(srcdir: str, destdir: str) -> None:
    """Copy and complete all the static document pages."""
    fileutils.mycopytree(srcdir, destdir)
    log.info("Converting .md docs to html")
    convertmd2htmldocs.mddocs(DESTDIR, DESTDIR)
    htmlinserts(destdir=destdir)
    log.info("Done")


if __name__ == "__main__":
    copyFiles(SRCDIR, DESTDIR)
