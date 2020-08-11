#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import os
for path in [os.getcwd(),"SchemaExamples"]:
  sys.path.insert( 1, path ) #Pickup libs from shipped lib directory

import logging
logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)

from schemaexamples import schemaExamples


exfiles = []
import glob
globpatterns = ["data/*examples.txt","data/ext/*/*examples.txt" ]

files = []
for g in globpatterns:
    files.extend(glob.glob(g))
    
log.info("Loading %d files" % len(files))
for f in files:
    #log.info("Loading: %s" % f)
    schemaExamples.loadExamplesFile(f)

log.info("Loaded %s examples" % schemaExamples.count())

log.info("Processing")

count = 1
for e in schemaExamples.allExamples(sort=True):
    e.setKey('eg-{0:03d}'.format(count))
    count += 1
    

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