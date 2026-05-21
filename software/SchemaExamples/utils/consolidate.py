#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
import os
import sys

import software

from SchemaExamples.schemaexamples import Example, SchemaExamples


logging.basicConfig(level=logging.INFO)  # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)


parser = argparse.ArgumentParser()
parser.add_argument("-o", "--output", required=True, help="output file")
args = parser.parse_args()


SchemaExamples.loadExamplesFiles("default")
print("Loaded %d examples " % (SchemaExamples.count()))

log.info("Consolidating..")

filename = args.output

log.info("Writing %s examples to file %s" % (SchemaExamples.count(),filename))
f = open(filename,"w")
f.write(SchemaExamples.allExamplesSerialised())
if f:
    f.close()
    print("Done")
