#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import os
for path in [os.getcwd(),"./SchemaExamples","./software/SchemaExamples"]:
  sys.path.insert( 1, path ) #Pickup libs from shipped lib directory

import logging
import argparse
logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)

from schemaexamples import SchemaExamples, Example

parser = argparse.ArgumentParser()
parser.add_argument("-o","--output", required=True, help="output file")
args = parser.parse_args()


SchemaExamples.loadExamplesFiles("default")
print("Loaded %d examples " % (SchemaExamples.count()))

log.info("Consolidating..")

filename = args.output

log.info("Writing %s examples to file %s" % (SchemaExamples.count(),filename))
f = open(filename,"w", encoding='utf8')
f.write(SchemaExamples.allExamplesSerialised())
if f:
    f.close()
    print("Done")
