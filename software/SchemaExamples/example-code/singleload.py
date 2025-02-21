#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
write back to another file
"""

SchemaExamples.loadExamplesFile("data/ext/pending/issue-894-examples.txt")
#print(SchemaExamples.examplesForTerm("Event"))


#filename = "out" + term.id +".html"
filename = "SchemaExamples/example-code/out"

exes = sorted(SchemaExamples.allExamples(), key=lambda x: (x.exmeta['file'],x.exmeta['filepos']))
f = open(filename,"w")
for ex in exes:
    f.write(ex.serialize())
    f.write("\n")
f.close()
