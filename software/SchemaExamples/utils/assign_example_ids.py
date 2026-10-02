#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from pathlib import Path

from SchemaExamples import schemaexamples


def AssignExampleIds():
    """Check if all examples are assigned an identity, if not, assign one and rewrite the file."""
    log = logging.getLogger(__name__)

    schemaexamples.SchemaExamples.loadExamplesFiles('default')
    log.info(f'Loaded {schemaexamples.SchemaExamples.count()} examples ')

    log.info('Processing')

    # Map from filename to example
    changedFiles = {}

    for example in schemaexamples.SchemaExamples.allExamples(sort=True):
        if not example.hasValidId():
            example.setKey(schemaexamples.Example.nextId())
            filename = example.getMeta('file')
            if filename in changedFiles:
                log.error(f'Two examples with the same filename {filename}: {changedFiles[filename]} and {example}')

    if not changedFiles:
        log.info('No new identifiers assigned')
        return

    log.info(f'Writing {len(changedFiles)} updated examples')

    for filename, example in changedFiles.items():
        log.info(f'Writing example file {filename}')
        Path(filename).write_text(f'{example.serialize()}\n', encoding='utf-8')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)  # dev_appserver.py --log_level debug .
    AssignExampleIds()
