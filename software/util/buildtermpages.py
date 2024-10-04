#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import standard python libraries

import os
import re
import time
import sys
import logging

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software
import software.util.schemaglobals as schemaglobals
import software.util.fileutils as fileutils
import software.util.jinga_render as jinga_render

import software.SchemaTerms.sdotermsource as sdotermsource
import software.SchemaTerms.sdoterm as sdoterm
import software.SchemaExamples.schemaexamples as schemaexamples


log = logging.getLogger(__name__)


def termFileName(termid):
    """Generate filename for term page.

    Parameters:
      termid (str): term identifier.
    Returns:
      File path the term page should be generated at.
    """
    path_components = [schemaglobals.OUTPUTDIR, "terms"]
    if re.match("^[a-z].*", termid):
        path_components.append("properties")
    elif re.match("^[0-9A-Z].*", termid):
        path_components.append("types")
    else:
        raise ValueError("Invalid terminid: '" + termid + "'")
    path_components.append(termid[0])
    directory = os.path.join(*path_components)
    fileutils.checkFilePath(directory)
    filename = termid + ".html"
    return os.path.join(directory, filename)


# This template will be used ~2800 times, so we reuse it.
TEMPLATE = jinga_render.GetJinga().get_template("terms/TermPage.j2")


def termtemplateRender(term, examples, json):
    """Render the term with examples and associated JSON.

    Parameters:
      term (sdoterm.SdoTerm): term to generate the page for
      examples (schemaexamples.Example): collection of examples for the term.
    Returns:
      string with the generate web-page.
    """
    assert isinstance(term, sdoterm.SdoTerm)
    for ex in examples:
        exselect = ["", "", "", ""]
        if ex.hasHtml():
            exselect[0] = "selected"
        elif ex.hasMicrodata():
            exselect[1] = "selected"
        elif ex.hasRdfa():
            exselect[2] = "selected"
        elif ex.hasJsonld():
            exselect[3] = "selected"
        ex.exselect = exselect

    extra_vars = {
        "title": term.label,
        "menu_sel": "Schemas",
        "home_page": "False",
        "BUILDOPTS": schemaglobals.BUILDOPTS,
        "docsdir": schemaglobals.TERMDOCSDIR,
        "term": term,
        "jsonldPayload": json,
        "examples": examples,
    }
    return jinga_render.templateRender(
        template_path=None, extra_vars=extra_vars, template_instance=TEMPLATE
    )


def RenderAndWriteSingleTerm(term_key):
    """Renders a single term and write the result into a file.

    Parameters:
      term_key (str): key for the term.
    Returns:
      elapsed time for the generation (seconds).
    """
    tic = time.perf_counter()
    term = sdotermsource.SdoTermSource.getTerm(term_key, expanded=True)
    if not term:
        log.error("No such term: %s\n" % term_key)
        return 0
    if (
        term.termType == sdoterm.SdoTermType.REFERENCE
    ):  # Don't create pages for reference types
        return 0
    examples = schemaexamples.SchemaExamples.examplesForTerm(term.id)
    json = sdotermsource.SdoTermSource.getTermAsRdfString(term.id, "json-ld", full=True)
    pageout = termtemplateRender(term, examples, json)
    with open(termFileName(term.id), "w", encoding="utf8") as outfile:
        outfile.write(pageout)
    elapsed = time.perf_counter() - tic
    log.info("Term '%s' generated in %0.4f seconds" % (term_key, elapsed))
    return elapsed


def buildTerms(terms):
    """Build the rendered version for a collection of terms."""
    if any(filter(lambda term: term in ("ALL", "All", "all"), terms)):
        terms = sdotermsource.SdoTermSource.getAllTerms(suppressSourceLinks=True)

    if terms:
        log.info("Building %d term pages..." % len(terms))

    total_elapsed = 0
    for term_key in terms:
        total_elapsed += RenderAndWriteSingleTerm(term_key)

    log.info("%s terms generated in %0.4f seconds" % (len(terms), total_elapsed))
