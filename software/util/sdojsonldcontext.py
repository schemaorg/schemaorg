#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import standard python libraries

import json
import logging
import os
import sys
import typing

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software
import software.SchemaTerms.sdotermsource as sdotermsource
import software.SchemaTerms.sdoterm as sdoterm
import software.util.pretty_logger as pretty_logger

log = logging.getLogger(__name__)


CONTEXT = None
SCHEMAURI = "http://schema.org/"


def getContext():
    global CONTEXT
    if not CONTEXT:
        CONTEXT = createcontext()
    return CONTEXT


def _convertTypes(type_range: typing.Collection[str]) -> typing.Set[str]:
    types = set()
    if "Text" in type_range:
        return types
    if "URL" in type_range:
        types.add("@id")
    if "Date" in type_range:
        types.add("Date")
    if "Datetime" in type_range:
        types.add("DateTime")
    return types


def createcontext():
    """Generates a basic JSON-LD context file for schema.org."""
    with pretty_logger.BlockLog(message="Creating JSON-LD context", logger=log):
        json_context = {
            "type": "@type",
            "id": "@id",
            "HTML": {"@id": "rdf:HTML"},
            "@vocab": SCHEMAURI,
        }

        done_namespaces = set()
        for pref, path in sdotermsource.SdoTermSource.sourceGraph().namespaces():
            pref = str(pref)
            if not pref in done_namespaces:
                done_namespaces.add(pref)
                if pref == "schema":
                    path = SCHEMAURI  # Override vocab setting to maintain http compatibility
                if pref == "geo":
                    continue
                json_context[pref] = path

        for term in sdotermsource.SdoTermSource.getAllTerms(
            expanded=True, suppressSourceLinks=True
        ):
            if term.termType == sdoterm.SdoTermType.REFERENCE:
                continue
            term_json = {"@id": sdotermsource.prefixedIdFromUri(term.uri)}
            if term.termType == sdoterm.SdoTermType.PROPERTY:
                types = _convertTypes(term.rangeIncludes)
                if len(types) == 1:
                    term_json["@type"] = types.pop()
                elif len(types) > 1:
                    term_json["@type"] = sorted(types)
            json_context[term.id] = term_json
        json_object = {"@context": json_context}
        return json.dumps(json_object, indent=2)
