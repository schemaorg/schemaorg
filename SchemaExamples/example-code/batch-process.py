#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import os
for path in [os.getcwd()]:
  sys.path.insert( 1, path ) #Pickup libs from shipped lib directory

import logging
logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)

from schemaexamples import schemaExamples


exfiles = []
import glob
#globpatterns = ["/Users/wallisr/Development/Schema/main/schemaorg/data/*examples.txt",
#                    "/Users/wallisr/Development/Schema/main/schemaorg/data/ext/*/*examples.txt" ]
globpatterns = ["example-code/examples.txt"]

files = []
for g in globpatterns:
    files.extend(glob.glob(g))
    
log.info("Loading %d files" % len(files))
for f in files:
    #log.info("Loading: %s" % f)
    schemaExamples.loadExamplesFile(f)

log.info("Loaded %s examples" % schemaExamples.count())

log.info("Process!")
for e in schemaExamples.allExamples():
    if not e.hasHtml():
        log.info("Example %s has no html" % e.key())
    if not e.hasMicrodata():
        log.info("Example %s has no html" % e.key())
    if not e.hasRdfa():
        log.info("Example %s has no html" % e.key())
    if not e.hasJsonld():
        log.info("Example %s has no html" % e.key())

filename = ""
f = None

examples = schemaExamples.allExamples(sort=True)
log.info("Writing %s examples" % len(examples))
for ex in examples:
    source = ex.exmeta['file']
    if source != filename:
        if f:
            f.close()
        filename = source
        #log.info("Writing %s.new" % filename)
        f = open(filename + ".new","w")
    f.write(ex.serialize())
    f.write("\n")
f.close()
#print(ex.serialize())