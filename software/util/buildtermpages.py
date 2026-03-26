#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import standard python libraries

import collections
import datetime
import logging
import multiprocessing
import os
import re
import sys
import time
import typing
from typing import List, Optional, Tuple, Dict, Any, Iterable

import jinja2

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software
import software.util.schemaglobals as schemaglobals
import software.util.fileutils as fileutils
import software.util.pretty_logger as pretty_logger
import software.util.jinga_render as jinga_render


import software.SchemaTerms.sdotermsource as sdotermsource
import software.SchemaTerms.sdoterm as sdoterm
import software.SchemaExamples.schemaexamples as schemaexamples


log: logging.Logger = logging.getLogger(__name__)


def termFileName(termid: str) -> str:
    """Generate filename for term page.

    Parameters:
      termid (str): term identifier.
    Returns:
      File path the term page should be generated at.
    """
    path_components: List[str] = [schemaglobals.getOutputDir(), "terms"]
    if re.match("^[a-z].*", termid):
        path_components.append("properties")
    elif re.match("^[0-9A-Z].*", termid):
        path_components.append("types")
    else:
        raise ValueError("Invalid terminid: '" + termid + "'")
    path_components.append(termid[0])
    directory: str = os.path.join(*path_components)
    fileutils.checkFilePath(directory)
    filename: str = termid + ".html"
    return os.path.join(directory, filename)


# This template will be used ~2800 times, so we reuse it.
TEMPLATE: jinja2.Template = jinga_render.GetJinga().get_template("terms/TermPage.j2")


def termtemplateRender(term: sdoterm.SdoTerm, examples: List[schemaexamples.Example], json: str) -> str:
    """Render the term with examples and associated JSON.

    Parameters:
      term (sdoterm.SdoTerm): term to generate the page for
      examples (schemaexamples.Example): collection of examples for the term.
    Returns:
      string with the generate web-page.
    """
    assert isinstance(term, sdoterm.SdoTerm)
    for ex in examples:
        exselect: List[str] = ["", "", "", ""]
        if ex.hasHtml():
            exselect[0] = "selected"
        elif ex.hasMicrodata():
            exselect[1] = "selected"
        elif ex.hasRdfa():
            exselect[2] = "selected"
        elif ex.hasJsonld():
            exselect[3] = "selected"
        ex.exselect = exselect

    extra_vars: Dict[str, Any] = {
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


def RenderAndWriteSingleTerm(term_key: str) -> float:
    """Renders a single term and write the result into a file.

    Parameters:
      term_key (str): key for the term.
    """

    with pretty_logger.BlockLog(
        logger=log, message=f"Generate term {term_key}", timing=True, displayStart=False
    ) as block:
        term: Optional[sdoterm.SdoTerm] = sdotermsource.SdoTermSource.getTerm(term_key, expanded=True)
        if not term:
            log.error(f"No such term: {term_key}")
            return 0
        if (
            term.termType == sdoterm.SdoTermType.REFERENCE
        ):  # Don't create pages for reference types
            return 0
        try:
          examples: List[schemaexamples.Example] = schemaexamples.SchemaExamples.examplesForTerm(term.id)
          json_str: str = sdotermsource.SdoTermSource.getTermAsRdfString(
              term.id, "json-ld", full=True
          )
          pageout: str = termtemplateRender(term, examples, json_str)
          with open(termFileName(term.id), "w", encoding="utf8") as outfile:
              outfile.write(pageout)
        except Exception as e:
            e.add_note(f"Term definition: {term}")
            raise
    return block.elapsed


def _buildTermIds(pair: Tuple[int, List[str]]) -> None:
    shard, term_ids = pair
    pretty_logger.MakeRootLogPretty(shard=shard)
    for term_id in term_ids:
        try:
            RenderAndWriteSingleTerm(term_id)
        except Exception as e:
            e.add_note(f"While building term_id {term_id}")
            raise


def buildTerms(term_ids: Iterable[str]) -> None:
    """Build the rendered version for a collection of terms.

    As this is rather CPU intensive, we shard the work into as many processes
    as there are CPUs.
    """

    tic: float = time.perf_counter()
    if any(filter(fileutils.isAll, term_ids)):
        log.info("Loading all term identifiers")
        term_ids = sdotermsource.SdoTermSource.getAllTerms(suppressSourceLinks=True)

    if not term_ids:
        return

    shard_numbers: int = multiprocessing.cpu_count()
    with pretty_logger.BlockLog(
        logger=log,
        message=f"Building {len(list(term_ids))} term pages with {shard_numbers} shards.",
    ):
        sharded_terms: Dict[int, List[str]] = collections.defaultdict(list)
        for n, term_id in enumerate(term_ids):
            sharded_terms[n % shard_numbers].append(term_id)

        with multiprocessing.Pool() as pool:
            pool.map(_buildTermIds, sharded_terms.items())
    elapsed: datetime.timedelta = datetime.timedelta(seconds=time.perf_counter() - tic)
    log.info(f"{len(list(term_ids))} Terms generated in {elapsed} seconds")
