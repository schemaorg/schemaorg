#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import os
for path in [os.getcwd(),"./SchemaExamples","./software/SchemaExamples"]:
  sys.path.insert( 1, path ) #Pickup libs from shipped lib directory

import logging
logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)

import schemaexamples


def reassign_ids():
    schemaexamples.SchemaExamples.loadExamplesFiles("default")
    log.info("Loaded %d examples " % schemaexamples.SchemaExamples.count())
    log.info("Processing")

    changedExamples = {}
    examples = schemaexamples.SchemaExamples.allExamples(sort=True)

    for ex in examples:
        if not ex.hasValidId():
            ex.setKey(schemaexamples.Example.nextId())
            filename = ex.getMeta('file')
            changedExamples[filename] = ex


    if not changedExamples:
        log.info("No new identifiers assigned")
    return

    log.info("Writing %s updated examples files" % len(changedExamples))

    for filename, example in changedExamples:
        log.info("Writing %s" % filename)
        tempfile = filename + '.tmp'
        with open(tempfile, 'w') as temp_handle:
            temp_handle.write(ex.serialize())
            temp_handle.write("\n")
        # Overwrite atomically
        os.replace(tempfile, filename)


if __name__ == '__main__':
    reassign_ids()