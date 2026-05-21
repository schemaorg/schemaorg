#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
write back to another file
"""

SchemaExamples.loadExamplesFiles("data/ext/pending/issue-894-examples.txt")
# print(SchemaExamples.examplesForTerm("Event"))


# filename = "out" + term.id +".html"
filename = os.path.join(os.path.dirname(__file__), "out")

exes = sorted(SchemaExamples.allExamples(), key=lambda x: (x.exmeta['file'], x.exmeta['filepos']))
f = open(filename, "w")
for ex in exes:
    f.write(ex.serialize())
    f.write("\n")
f.close()
