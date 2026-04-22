#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import os
import sys
import typing
from typing import Any, Dict, Optional, Set, List

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software
import software.SchemaTerms.sdotermsource as sdotermsource
import software.SchemaTerms.sdoterm as sdoterm
import software.util.pretty_logger as pretty_logger
from software.util.sort_dict import sort_dict

log: logging.Logger = logging.getLogger(__name__)


CONTEXT: Optional[str] = None
SCHEMAURI: str = "http://schema.org/"


def getContext() -> str:
    global CONTEXT
    if not CONTEXT:
        CONTEXT = createcontext()
    return CONTEXT


def _convertTypes(type_range: typing.Collection[str]) -> typing.Set[str]:
    types: Set[str] = set()
    if "Text" in type_range:
        return types
    if "URL" in type_range:
        types.add("@id")
    if "Date" in type_range:
        types.add("Date")
    if "Datetime" in type_range:
        types.add("DateTime")
    return types


def createcontext() -> str:
    """Generates a basic JSON-LD context file for schema.org."""
    with pretty_logger.BlockLog(message="Creating JSON-LD context", logger=log):
        json_context: Dict[str, Any] = {
            "type": "@type",
            "id": "@id",
            "HTML": {"@id": "rdf:HTML"},
            "@vocab": SCHEMAURI,
        }

        done_namespaces: Set[str] = set()
        for pref, path in sdotermsource.SdoTermSource.sourceGraph().namespaces():
            pref_str: str = str(pref)
            if pref_str not in done_namespaces:
                done_namespaces.add(pref_str)
                if pref_str == "schema":
                    path = SCHEMAURI  # Override vocab setting to maintain http compatibility
                if pref_str == "geo":
                    continue
                json_context[pref_str] = path

        all_terms: List[sdoterm.SdoTerm] = sdotermsource.SdoTermSource.getAllTerms(
            expanded=True, suppressSourceLinks=True
        )
        for term in all_terms:
            if not isinstance(term, sdoterm.SdoTerm):
                continue
            if term.termType == sdoterm.SdoTermType.REFERENCE:
                continue
            term_json: Dict[str, Any] = {"@id": sdotermsource.prefixedIdFromUri(term.uri)}
            if term.termType == sdoterm.SdoTermType.PROPERTY:
                types: Set[str] = _convertTypes(term.rangeIncludes.ids)
                if len(types) == 1:
                    term_json["@type"] = types.pop()
                elif len(types) > 1:
                    term_json["@type"] = sorted(list(types))
            json_context[term.id] = term_json
        json_object: Dict[str, Any] = {"@context": json_context}
        return json.dumps(sort_dict(json_object), indent=2)
