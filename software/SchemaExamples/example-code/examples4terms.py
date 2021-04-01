#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import os
for path in [os.getcwd(),"SchemaExamples"]:
  sys.path.insert( 1, path ) #Pickup libs from shipped lib directory

import logging
logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)

from schemaexamples import Example, SchemaExamples

"""
Load examples from file
"""
import glob
globpatterns = ["data/*examples.txt","data/ext/*/*examples.txt" ]

files = []
for g in globpatterns:
    files.extend(glob.glob(g))
    
print("Loading %d files" % len(files))
SchemaExamples.loadExamplesFiles(files)

for term in ["CreativeWork","Person","Atlas","DefinedTerm"]:
    for ex in SchemaExamples.examplesForTerm(term):
        print("%s has example key: %s" % (term,ex.getKey()))
    