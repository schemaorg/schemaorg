#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Tool that validates the JSON-LD in the examples against the content of the `jsonldcontext.jsonld` file."""

import argparse
import logging
import os
from pathlib import Path
import re
import sys

import rdflib

from schemaorg import constants
import SchemaExamples.schemaexamples as schemaexamples


log = logging.getLogger(__name__)


CONTEXT_MATCH = re.compile(
    r'([\S\s]*"@context"\s*:\s*\[?[\S\s]*")https?://schema\.org/?("[\S\s]*)',
    re.M,
)
CURRENT_CONTEXT_FILE = (
    constants.PROJECT_ROOT / "software/site/docs/jsonldcontext.jsonld"
)


def validateJsonld(example):
    """Validate the JSON-LD in an example.

    Args:
        example: schemaexamples.Example
    Returns:
        None
    Throws:
        Exception is example is invalid.
    """
    if not example.hasJsonld():
        return None, None
    example_json = example.getJsonldRaw()

    while cmatch := CONTEXT_MATCH.match(example_json):
        example_json = (
            f"{cmatch.group(1)}file://{CURRENT_CONTEXT_FILE}{cmatch.group(2)}"
        )
    exGraph = rdflib.Graph()
    exGraph.parse(
        data=example_json,
        format="json-ld",
        base=f"http://example.com/{example.getKey()}",
    )


def _ExampleKey(example):
    return (
        f"[key={example.getKey()}, "
        f"file={example.getMeta('file')}{{{example.getMeta('filepos')}}}]"
    )


def validateExample(example, invalid_only, source_output):
    """Validate an example.

    Args:
        example: schemaexamples.Example
        invalid_only: If true, only information about invalid entries is logged (less verbose).
        source_output: If True, invalid source code is logged.
    Returns:
        True if the example is valid, False otherwise
    """
    if not invalid_only:
        log.info("Validating example %s", _ExampleKey(example))
    try:
        validateJsonld(example)
        return True
    except Exception as exception:
        log.error("Invalid JSON example %s: %s", _ExampleKey(example), exception)
        if source_output:
            source = "\n".join(
                f"{i:4d}: {x.rstrip()}"
                for i, x in enumerate(example.getJsonldRaw().splitlines(), start=1)
            )
            log.info("Source:\n%s", source)
        return False


def validate(example_list, invalid_only, source_output):
    """Validate all examples, or the ones matching `example_list`.

    Args:
        example_list: list of example keys (string), if empty, all examples are handled.
        invalid_only: If true, only information about invalid entries is logged (less verbose).
        source_output: If True, invalid source code is logged.
    """
    count = 0
    errorCount = 0

    loaded = schemaexamples.SchemaExamples.from_default()
    log.info("Loaded %d examples, processing", len(loaded))

    for ex in loaded.allExamples():
        if not example_list or ex.getKey() in example_list:
            count += 1
            if not validateExample(ex, invalid_only, source_output):
                errorCount += 1
    log.info("Done: Processed %d examples", count)
    if errorCount:
        log.error("Found %d invalid examples", errorCount)


if __name__ == "__main__":
    if not CURRENT_CONTEXT_FILE.is_file():
        log.error("%s file not found – check site build", CURRENT_CONTEXT_FILE)
        sys.exit(os.EX_CONFIG)

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-e",
        "--example",
        default=[],
        action="append",
        nargs="*",
        help="example to validate(repeatable) - default: all examples",
    )
    parser.add_argument(
        "-i",
        "--invalidonly",
        default=False,
        action="store_true",
        help="Only report invalid examples",
    )
    parser.add_argument(
        "-s",
        "--sourceoutput",
        default=False,
        action="store_true",
        help="Output invalid example source",
    )
    args = parser.parse_args()

    example_list = [ex for group in args.example for ex in group]

    validate(
        example_list=example_list,
        invalid_only=args.invalidonly,
        source_output=args.sourceoutput,
    )
