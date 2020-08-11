#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import os
for path in [os.getcwd(),"SchemaExamples"]:
  sys.path.insert( 1, path ) #Pickup libs from shipped lib directory

import logging
logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)

from schemaexamples import SchemaExamples, Example


exfiles = []
import glob
globpatterns = ["data/*examples.txt","data/ext/*/*examples.txt" ]

files = []
for g in globpatterns:
    files.extend(glob.glob(g))
    
log.info("Loading %d files" % len(files))
for f in files:
    #log.info("Loading: %s" % f)
    SchemaExamples.loadExamplesFile(f)

log.info("Loaded %s examples" % SchemaExamples.count())

log.info("Processing")

#Example.nextIdReset()
changedFiles=[]
changedCount = 0

for ex in SchemaExamples.allExamples(sort=True):
    if not ex.hasValidId():
        ex.setKey(Example.nextId())
        changedCount += 1
        if not ex.getMeta('file') in changedFiles:
            changedFiles.append(ex.getMeta('file'))

filename = ""
f = None

examples = SchemaExamples.allExamples(sort=True)
log.info("Writing %s changed examples into %s files" % (changedCount,len(changedFiles)))

#OUTFILESUFFIX = ".new"
OUTFILESUFFIX = "" #Overwrite sourcefiles

for ex in examples:
    source = ex.getMeta('file')
    if source not in changedFiles:
        continue
    if source != filename:
        if f:
            f.close()
        filename = source
        fn = filename + OUTFILESUFFIX
        log.info("Writing %s" % fn)
        f = open(fn,"w")
    f.write(ex.serialize())
    f.write("\n")
f.close()
#print(ex.serialize())