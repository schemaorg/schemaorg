#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import collections
import datetime
import functools
import json
import logging
import multiprocessing
import re
import sys
import time
from pathlib import Path
from typing import List, Optional, Tuple, Dict, Any, Iterable, Sequence, Type

import jinja2

if Path.cwd() not in [Path(p).resolve() for p in sys.path]:
    sys.path.insert(1, str(Path.cwd()))

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
    """Generate filename for term page."""
    if not termid:
        raise ValueError("Empty termid")
    base_dir: Path = Path(schemaglobals.getOutputDir()) / "terms"
    sub_dir: str
    if termid[0].islower():
        sub_dir = "properties"
    elif termid[0].isupper() or termid[0].isdigit():
        sub_dir = "types"
    else:
        raise ValueError(f"Invalid termid: '{termid}'")

    return str(base_dir / sub_dir / termid[0] / f"{termid}.html")


TEMPLATE: jinja2.Template = jinga_render.GetJinga().get_template("terms/TermPage.j2")


@functools.lru_cache(maxsize=1)
def load_public_stats() -> Tuple[Dict[str, str], str]:
    """Load public stats O(1) lookup map mapping term URI/URL to domain bucket."""
    stats_files = sorted([f for f in Path("data/public_stats/google").glob("20*.json") if not f.name.startswith("summary_")])
    if not stats_files:
        return {}, ""
    latest_file = stats_files[-1]
    filename = latest_file.stem  # e.g., "2026_05"
    date_str = ""
    try:
        date_obj = datetime.datetime.strptime(filename, "%Y_%m")
        date_str = date_obj.strftime("%B %Y")
    except ValueError:
        pass

    try:
        with open(latest_file, "r", encoding="utf-8") as f:
            raw_data = json.load(f)
        res: Dict[str, str] = {}
        for item in raw_data:
            name = item.get("Name")
            bucket = item.get("Domain Bucket")
            if name and bucket:
                res[name] = bucket
                if name.startswith("http://"):
                    res["https://" + name[7:]] = bucket
                elif name.startswith("https://"):
                    res["http://" + name[8:]] = bucket
        return res, date_str
    except Exception as e:
        log.error(f"Failed to load public stats: {e}")
        return {}, date_str


def termtemplateRender(term: sdoterm.SdoTerm, examples: List[schemaexamples.Example], json: str) -> str:
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

    stats, stats_date = load_public_stats()
    extra_vars: Dict[str, Any] = {
        "title": term.label,
        "menu_sel": "Schemas",
        "home_page": "False",
        "BUILDOPTS": schemaglobals.BUILDOPTS,
        "docsdir": schemaglobals.TERMDOCSDIR,
        "term": term,
        "jsonldPayload": json,
        "examples": examples,
        "google_public_stats": stats,
        "google_public_stats_date": stats_date,
    }
    return jinga_render.templateRender(
        template_path=None, extra_vars=extra_vars, template_instance=TEMPLATE
    )


def RenderAndWriteSingleTerm(term_key: str) -> float:
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
            pageout: str = termtemplateRender(term, examples, json_str)
            outfile: Path = Path(termFileName(term.id))
            fileutils.checkFilePath(outfile.parent)
            outfile.write_text(pageout, encoding="utf8")
        except Exception as e:
            e.add_note(f"Term definition: {term}")
            raise
    return float(block.elapsed or 0.0)


def _buildTermIds(pair: Tuple[int, List[str]]) -> None:
    shard: int
    term_ids: List[str]
    shard, term_ids = pair
    pretty_logger.MakeRootLogPretty(shard=shard)
    term_id: str
    for term_id in term_ids:
        try:
            RenderAndWriteSingleTerm(term_id)
        except Exception as e:
            e.add_note(f"While building term_id {term_id}")
            raise


def buildTerms(term_ids: Iterable[str]) -> None:
    """Build the rendered version for a collection of terms."""
    tic: float = time.perf_counter()
    if any(fileutils.isAll(tid) for tid in term_ids):
        log.info("Loading all term identifiers")
        term_ids = sdotermsource.SdoTermSource.getAllTerms(suppressSourceLinks=True)  # type: ignore

    term_list: List[str] = list(term_ids)
    if not term_list:
        return

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

        with multiprocessing.Pool() as pool:
            pool.map(_buildTermIds, sharded_terms.items())
    elapsed: datetime.timedelta = datetime.timedelta(seconds=time.perf_counter() - tic)
    log.info(f"{len(term_list)} Terms generated in {elapsed} seconds")
