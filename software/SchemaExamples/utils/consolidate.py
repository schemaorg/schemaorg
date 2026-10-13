#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging
from pathlib import Path

from SchemaExamples.schemaexamples import SchemaExamples


logging.basicConfig(level=logging.INFO)  # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)


parser = argparse.ArgumentParser()
parser.add_argument("-o", "--output", required=True, help="output file")
args = parser.parse_args()


SchemaExamples.loadExamplesFiles("default")
print(f"Loaded {SchemaExamples.count()} examples ")

log.info("Consolidating..")

filename = args.output

log.info(f"Writing {SchemaExamples.count()} examples to file {filename}")
Path(filename).write_text(SchemaExamples.allExamplesSerialised(), encoding="utf-8")
print("Done")
