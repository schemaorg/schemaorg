#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import glob
import logging

# Ensure we can find schemaexamples.py
for path in [os.getcwd()]:
    sys.path.insert(1, path)

logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

from schemaexamples import SchemaExamples as schemaExamples

# --- UPDATED GLOB PATTERNS ---
# This will now look in the data folder and its subdirectories
globpatterns = [
    "data/*examples.txt", 
    "data/ext/*/*examples.txt",
    "example-code/examples.txt"
]

files = []
for g in globpatterns:
    files.extend(glob.glob(g))
    
log.info("Loading %d files" % len(files))
for f in files:
    schemaExamples.loadExamplesFiles(f)

log.info("Loaded %s examples" % schemaExamples.count())

log.info("Process!")
for e in schemaExamples.allExamples():
    # Fixed: e.key() changed to e.getKey()
    # Fixed: Log messages now accurately describe what is missing
    if not e.hasHtml():
        log.info("Example %s has no html" % e.getKey())
    if not e.hasMicrodata():
        log.info("Example %s has no microdata" % e.getKey())
    if not e.hasRdfa():
        log.info("Example %s has no rdfa" % e.getKey())
    if not e.hasJsonld():
        log.info("Example %s has no jsonld" % e.getKey())

filename = ""
f_out = None # Renamed to avoid confusion with loop variable 'f'

examples = schemaExamples.allExamples(sort=True)
log.info("Writing %s examples" % len(examples))

for ex in examples:
    source = ex.exmeta['file']
    if source != filename:
        if f_out:
            f_out.close()
        filename = source
        # Creates a file like 'data/examples.txt.new'
        f_out = open(filename + ".new", "w", encoding="utf-8")
        
    f_out.write(ex.serialize())
    f_out.write("\n")

if f_out:
    f_out.close()