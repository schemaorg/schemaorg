#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import logging
import os
import sys

if os.getcwd() not in sys.path:
    sys.path.insert(1, os.getcwd())
import software

from SchemaExamples.schemaexamples import Example, SchemaExamples


logging.basicConfig(level=logging.INFO)  # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)


"""
Load examples from file
"""
root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
globpatterns = [os.path.join(root, "data/*examples.txt"), os.path.join(root, "data/ext/*/*examples.txt")]

files = []
for g in globpatterns:
    files.extend(glob.glob(g))

os.chdir(root)
print("Loading %d files" % len(files))
SchemaExamples.loadExamplesFiles(files)

for term in ["CreativeWork", "Person", "Atlas", "DefinedTerm"]:
    for ex in SchemaExamples.examplesForTerm(term):
        print("%s has example key: %s" % (term, ex.getKey()))
