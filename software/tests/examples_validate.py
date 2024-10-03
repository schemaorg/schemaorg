#!/usr/bin/env python3
# -*- coding: utf-8 -*-


"""Tool that validates the JSON-LD in the examples agains the content of the `jsonldcontext.jsonld` file."""

# Import standard python libraries

import argparse
import io
import logging
import os
import rdflib
import re
import sys

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software
import software.SchemaExamples.schemaexamples as schemaexamples


log = logging.getLogger(__name__)


CONTEXT_MATCH = re.compile(
    '([\\S\\s]*"@context"\\s*:\\s*\\[?[\\S\\s]*")https?:\\/\\/schema\\.org\\/?("[\\S\\s]*)',
    re.M,
)
CURRENT_CONTEXT_FILE = os.path.join(
    os.getcwd(), "software", "site", "docs", "jsonldcontext.jsonld"
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

    while True:
        cmatch = CONTEXT_MATCH.match(example_json)
        if not cmatch:
            break
        example_json = (
            cmatch.group(1) + "file://" + CURRENT_CONTEXT_FILE + cmatch.group(2)
        )
    exGraph = rdflib.Graph()
    exGraph.parse(
        data=example_json,
        format="json-ld",
        base=os.path.join("http://example.com/", example.getKey()),
    )


def _ExampleKey(example):
    return "[key=%s, file=%s{%s}]" % (
        example.getKey(),
        example.getMeta("file"),
        example.getMeta("filepos"),
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
                [
                    "{:4d}: {}".format(i, x.rstrip())
                    for i, x in enumerate(example.getJsonldRaw().splitlines(), start=1)
                ]
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

    schemaexamples.SchemaExamples.loaded()
    log.info("Loaded %d examples, processing" % (schemaexamples.SchemaExamples.count()))

    for ex in schemaexamples.SchemaExamples.allExamples(sort=True):
        if not example_list or ex.getKey() in example_list:
            count += 1
            if not validateExample(ex, invalid_only, source_output):
                errorCount += 1
    log.info("Done: Processed %d examples", count)
    if errorCount:
        log.error("Found %d invalid examples", errorCount)


if __name__ == "__main__":
    if not os.path.isfile(CURRENT_CONTEXT_FILE):
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

    example_list = []
    for example in args.example:
        example_list.extend(ex)

    validate(
        example_list=example_list,
        invalid_only=args.invalidonly,
        source_output=args.sourceoutput,
    )
