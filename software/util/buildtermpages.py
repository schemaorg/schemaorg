#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import collections
import datetime
import logging
import multiprocessing
import os
from pathlib import Path
import re
import sys
import time
import unicodedata
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Type

import jinja2

import software

import SchemaExamples.schemaexamples as schemaexamples
import SchemaTerms.sdoterm as sdoterm
import SchemaTerms.sdotermsource as sdotermsource
import util.fileutils as fileutils
import util.jinga_render as jinga_render
import util.paths as paths
import util.pretty_logger as pretty_logger
import util.schema as schema
import util.stats as stats


log: logging.Logger = logging.getLogger(__name__)



def termFileName(termid: str) -> str:
    """Generate filename for term page."""
    if not termid:
        raise ValueError("Empty term_id")
    c: str = termid[0]
    sub_dir: str
    if c.islower():
        sub_dir = "properties"
    elif c.isupper() or c.isdigit():
        sub_dir = "types"
    else:
        raise ValueError(f"Invalid term_id: '{termid}'")

    return str(paths.DefaultOutputLayout().domain_file(paths.Domain.TERMS, f"{sub_dir}/{c}/{termid}.html"))


class TermPageRenderer:
    """Encapsulates the rendering and file-writing operations for terms."""

    def __init__(
        self,
        stats_providers: list,
        build_opts: List[str],
        term_docs_dir: str,
    ):
        self.stats_providers = stats_providers
        self.build_opts = build_opts
        self.term_docs_dir = term_docs_dir
        self.template = jinga_render.GetJinga().get_template("terms/TermPage.j2")

    def termtemplateRender(
        self,
        term: sdoterm.SdoTerm,
        examples: List[schemaexamples.Example],
        json: str,
    ) -> str:
        """Render the term with examples and associated JSON."""
        assert isinstance(term, sdoterm.SdoTerm)
        ex: schemaexamples.Example
        for ex in examples:
            exselect: List[str] = [""] * 4
            if ex.hasHtml():
                exselect[0] = "selected"
            elif ex.hasMicrodata():
                exselect[1] = "selected"
            elif ex.hasRdfa():
                exselect[2] = "selected"
            elif ex.hasJsonld():
                exselect[3] = "selected"
            ex.exselect = exselect  # type: ignore
        stats_badges = []
        if term and term.uri:
            cleaned_uri = unicodedata.normalize("NFC", term.uri.strip())
            for provider in self.stats_providers:
                stats_map = provider.stats_map
                badge = stats_map.get(cleaned_uri)
                if badge:
                    stats_badges.append({
                        "provider_name": provider.name,
                        "badge": badge,
                        "date": provider.date,
                        "description": provider.description
                    })
        extra_vars: Dict[str, Any] = {
            "title": term.label,
            "menu_sel": "Schemas",
            "home_page": "False",
            "BUILDOPTS": self.build_opts,
            "docsdir": self.term_docs_dir,
            "term": term,
            "jsonldPayload": json,
            "examples": examples,
            "stats_badges": stats_badges,
        }
        return jinga_render.templateRender(
            template_path=None, extra_vars=extra_vars, template_instance=self.template
        )

    def RenderAndWriteSingleTerm(self, term_key: str) -> float:
        """Renders a single term and write the result into a file."""
        block: pretty_logger.BlockLog
        with pretty_logger.BlockLog(
            logger=log, message=f"Generate term {term_key}", timing=True, displayStart=False
        ) as block:
            term: Optional[sdoterm.SdoTerm] = sdotermsource.SdoTermSource.getTerm(term_key, expanded=True)
            if not term:
                log.error(f"No such term: {term_key}")
                return 0.0
            if term.termType == sdoterm.SdoTermType.REFERENCE:
                return 0.0
            try:
                examples: List[schemaexamples.Example] = schemaexamples.SchemaExamples.examplesForTerm(term.id)
                json_str: str = sdotermsource.SdoTermSource.getTermAsRdfString(term.id, "json-ld", full=True)
                pageout: str = self.termtemplateRender(term, examples, json_str)
                outfile: Path = Path(termFileName(term.id))
                fileutils.checkFilePath(outfile.parent)
                outfile.write_text(pageout)
            except Exception as e:
                e.add_note(f"Term definition: {term}")
                raise
        return float(block.elapsed or 0.0)


def _buildTermIds(args: Tuple[Tuple[int, List[str]], Dict[str, Any]]) -> None:
    shard_pair, config = args
    shard, term_ids = shard_pair
    pretty_logger.MakeRootLogPretty(shard=shard)
    renderer = TermPageRenderer(**config)
    term_id: str
    for term_id in term_ids:
        try:
            renderer.RenderAndWriteSingleTerm(term_id)
        except Exception as e:
            e.add_note(f"While building term_id {term_id}")
            raise


def buildTerms(term_ids: Iterable[str], config: Optional[Dict[str, Any]] = None) -> None:
    """Build the rendered version for a collection of terms."""
    tic: float = time.perf_counter()
    if any(fileutils.isAll(tid) for tid in term_ids):
        log.info("Loading all term identifiers")
        term_ids = sdotermsource.SdoTermSource.getAllTerms(suppressSourceLinks=True)  # type: ignore

    term_list: List[str] = list(term_ids)
    if not term_list:
        return

    if config is None:
        config = {
            "stats_providers": stats.get_stats_providers(),
            "build_opts": schema.config.BUILDOPTS,
            "term_docs_dir": schema.constants.TERMDOCSDIR,
        }

    shard_numbers: int = multiprocessing.cpu_count()
    with pretty_logger.BlockLog(
        logger=log,
        message=f"Building {len(term_list)} term pages with {shard_numbers} shards.",
    ):
        sharded_terms: Dict[int, List[str]] = collections.defaultdict(list)
        n: int
        term_id: str
        for n, term_id in enumerate(term_list):
            sharded_terms[n % shard_numbers].append(term_id)

        tasks = [(item, config) for item in sharded_terms.items()]

        with multiprocessing.Pool() as pool:
            pool.map(_buildTermIds, tasks)
    elapsed: datetime.timedelta = datetime.timedelta(seconds=time.perf_counter() - tic)
    log.info(f"{len(term_list)} Terms generated in {elapsed} seconds")
