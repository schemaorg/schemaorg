#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import logging
import os
import sys
import typing
from typing import Any, Dict, List, Optional, Set

import software

import SchemaTerms.sdoterm as sdoterm
import SchemaTerms.sdotermsource as sdotermsource
import util.pretty_logger as pretty_logger
from util.sort_dict import sort_dict


log: logging.Logger = logging.getLogger(__name__)


CONTEXT: Optional[str] = None
SCHEMAURI: str = "http://schema.org/"


def getContext() -> str:
    global CONTEXT
    if not CONTEXT:
        CONTEXT = createcontext()
    return CONTEXT

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
            json_context[term.id] = {"@id": sdotermsource.prefixedIdFromUri(term.uri)}
        json_object: Dict[str, Any] = {"@context": json_context}
        return json.dumps(sort_dict(json_object), indent=2)
