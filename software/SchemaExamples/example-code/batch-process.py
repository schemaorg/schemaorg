#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import logging
import os
import sys

if os.getcwd() not in sys.path:
    sys.path.insert(1, os.getcwd())
import software

from SchemaExamples.schemaexamples import SchemaExamples


logging.basicConfig(level=logging.INFO)  # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)



exfiles = []
# globpatterns =
# ["/Users/wallisr/Development/Schema/main/schemaorg/data/*examples.txt",
# "/Users/wallisr/Development/Schema/main/schemaorg/data/ext/*/*examples.txt" ]
globpatterns = [os.path.join(os.path.dirname(__file__), "examples.txt")]

files = []
for g in globpatterns:
    files.extend(glob.glob(g))

log.info("Loading %d files" % len(files))
for f in files:
    # log.info("Loading: %s" % f)
    SchemaExamples.loadExamplesFiles(f)

log.info("Loaded %s examples" % SchemaExamples.count())

log.info("Process!")
for e in SchemaExamples.allExamples():
    if not e.hasHtml():
        log.info("Example %s has no html" % e.getKey())
    if not e.hasMicrodata():
        log.info("Example %s has no html" % e.getKey())
    if not e.hasRdfa():
        log.info("Example %s has no html" % e.getKey())
    if not e.hasJsonld():
        log.info("Example %s has no html" % e.getKey())

filename = ""
f = None

examples = SchemaExamples.allExamples(sort=True)
log.info("Writing %s examples" % len(examples))
for ex in examples:
    source = ex.exmeta['file']
    if source != filename:
        if f:
            f.close()
        filename = source
        # log.info("Writing %s.new" % filename)
        f = open(filename + ".new", "w")
    f.write(ex.serialize())
    f.write("\n")
f.close()
# print(ex.serialize())
