#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Import standard python libraries

import sys
import os
import glob
import re

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software
from sdotermsource import SdoTermSource,prefixedIdFromUri
from sdoterm import *

def createcontext():
    """Generates a basic JSON-LD context file for schema.org."""

    SCHEMAURI = "http://schema.org/"

    jsonldcontext = []
    jsonldcontext.append("{\n  \"@context\": {\n")
    jsonldcontext.append("        \"type\": \"@type\",\n")
    jsonldcontext.append("        \"id\": \"@id\",\n")
    jsonldcontext.append("        \"HTML\": { \"@id\": \"rdf:HTML\" },\n")
    #jsonldcontext.append("        \"@vocab\": \"%s\",\n" % SdoTermSource.vocabUri())
    jsonldcontext.append("        \"@vocab\": \"%s\",\n" % SCHEMAURI)
    ns = SdoTermSource.sourceGraph().namespaces()
    done = []
    for n in ns:
        for n in ns:
            pref, pth = n
            pref = str(pref)
            if not pref in done:
                done.append(pref)
                if pref == "schema":
                    pth = SCHEMAURI #Override vocab setting to maintain http compatibility
                if pref == "geo":
                    continue
                jsonldcontext.append("        \"%s\": \"%s\",\n" % (pref,pth))

    datatypepre = "schema:"
    vocablines = ""
    externalines = ""
    typins = ""
    for t in SdoTermSource.getAllTerms(expanded=True,suppressSourceLinks=True):
        if t.termType == SdoTerm.PROPERTY:
            range = t.rangeIncludes

            types = []

            #If Text in range don't output a @type value
            if not "Text" in range:
                if "URL" in range:
                    types.append("@id")
                if "Date" in range:
                    types.append("Date")
                if "Datetime" in range:
                    types.append("DateTime")

            typins = ""
            for typ in types:
                typins += ", \"@type\": \"" + typ + "\""

            line = "        \"" + t.id + "\": { \"@id\": \"" + prefixedIdFromUri(t.uri) + "\"" + typins + "},"
        elif t.termType == SdoTerm.REFERENCE:
            continue
        else:
            line =  "        \"" + t.id + "\": {\"@id\": \"" + prefixedIdFromUri(t.uri) + "\"},"

        if t.id.startswith("http:") or t.id.startswith("https:"):
            externalines += line
        else:
            vocablines += line

    jsonldcontext.append(vocablines)
    #jsonldcontext.append(externalines)
    jsonldcontext.append("}}\n")
    ret = "".join(jsonldcontext)
    ret = ret.replace("},}}","}\n    }\n}")
    ret = ret.replace("},","},\n")
    return ret
