#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import logging

for path in [os.getcwd(),'./SchemaExamples','./software/SchemaExamples']:
    sys.path.insert(1, path) # Pickup libs from shipped lib directory

import schemaexamples

def AssignExampleIds():
    """Check if all examples are assigned an identity, if not, assign one and rewrite the file."""
    log = logging.getLogger(__name__)

    schemaexamples.SchemaExamples.loadExamplesFiles('default')
    log.info('Loaded %d examples ' % (schemaexamples.SchemaExamples.count()))

    log.info('Processing')

    # Map from filename to example
    changedFiles = {}

    for example in schemaexamples.SchemaExamples.allExamples(sort=True):
        if not example.hasValidId():
            example.setKey(schemaexamples.Example.nextId())
            filename = example.getMeta('file')
            if filename in changedFiles.keys():
                log.error('Two examples with the same filename %s: %s and %s' % (filename, changedFiles[filename], example))

    if not changedFiles:
        log.info('No new identifiers assigned')
        return

    log.info('Writing %s updated examples' % len(changedFiles))

    for filename, example in changedFiles.items():
        log.info('Writing example file %s' % filename)
        with open(filename, 'w', encoding='utf-8') as file_handle:
            file_handle.write(example.serialize())
            file_handle.write('\n')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
    AssignExampleIds()
