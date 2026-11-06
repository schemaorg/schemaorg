from __future__ import annotations

import collections
from collections.abc import Iterable, Sequence
import datetime
import logging
import multiprocessing
from pathlib import Path
import time
from typing import Any
import unicodedata

from schemaorg.layout.stats_layout import StatsProvider
import SchemaExamples.schemaexamples as schemaexamples
import SchemaTerms.sdoterm as sdoterm
import SchemaTerms.sdotermsource as sdotermsource
import util.fileutils as fileutils
import util.jinja_render as jinja_render
import util.paths as paths
import util.pretty_logger as pretty_logger
import util.schema as schema
import util.stats as stats

log: logging.Logger = logging.getLogger(__name__)


def termFileName(termid: str) -> Path:
    """Generate path for term page."""
    if not termid:
        raise ValueError("Empty term_id")
    first = termid[0]
    if first.islower():
        sub_dir = "properties"
    elif first.isupper() or first.isdigit():
        sub_dir = "types"
    else:
        raise ValueError(f"Invalid term_id: '{termid}'")

    return paths.DefaultOutputLayout().file(
        paths.Domain.TERMS, f"{sub_dir}/{first}/{termid}.html"
    )


class TermPageRenderer:
    """Encapsulates the rendering and file-writing operations for terms."""

    def __init__(
        self,
        stats_providers: Sequence[StatsProvider],
        build_opts: Sequence[str],
        term_docs_dir: str,
        examples: schemaexamples.SchemaExamples | None = None,
    ) -> None:
        self.stats_providers = stats_providers
        self.build_opts = build_opts
        self.term_docs_dir = term_docs_dir
        self.examples = examples
        self.template = jinja_render.get_jinja_env().get_template("terms/TermPage.j2")

    def termtemplateRender(
        self,
        term: sdoterm.SdoTerm,
        examples: Sequence[schemaexamples.Example],
        json: str,
    ) -> str:
        """Render the term with examples and associated JSON."""
        assert isinstance(term, sdoterm.SdoTerm)
        stats_badges = []
        if term.uri:
            cleaned_uri = unicodedata.normalize("NFC", term.uri.strip())
            for provider in self.stats_providers:
                if badge := provider.stats_map.get(cleaned_uri):
                    stats_badges.append(
                        {
                            "provider_name": provider.name,
                            "badge": badge,
                            "date": provider.date,
                            "description": provider.description,
                        }
                    )
        extra_vars: dict[str, Any] = {
            "title": term.label,
            "BUILDOPTS": self.build_opts,
            "docsdir": self.term_docs_dir,
            "term": term,
            "jsonldPayload": json,
            "examples": examples,
            "stats_badges": stats_badges,
        }
        return jinja_render.templateRender(
            extra_vars=extra_vars, template_instance=self.template
        )

    def RenderAndWriteSingleTerm(self, term_key: str) -> None:
        """Render a single term and write the result into a file."""
        with pretty_logger.BlockLog(
            logger=log,
            message=f"Generate term {term_key}",
            timing=True,
            displayStart=False,
        ):
            term = sdotermsource.SdoTermSource.getTerm(term_key, expanded=True)
            if not term:
                log.error("No such term: %s", term_key)
                return
            if term.termType == sdoterm.SdoTermType.REFERENCE:
                return
            try:
                if self.examples is None:
                    self.examples = schemaexamples.SchemaExamples.from_default()
                examples = self.examples.examplesForTerm(term.id)
                json_str = sdotermsource.SdoTermSource.getTermAsRdfString(
                    term.id, "json-ld", full=True
                )
                pageout = self.termtemplateRender(term, examples, json_str)
                termFileName(term.id).write_text(pageout, encoding="utf-8")
            except Exception as e:
                e.add_note(f"Term definition: {term}")
                raise


def _buildTermIds(args: tuple[tuple[int, list[str]], dict[str, Any]]) -> None:
    (shard, term_ids), config = args
    pretty_logger.MakeRootLogPretty(shard=shard)
    renderer = TermPageRenderer(**config)
    for term_id in term_ids:
        try:
            renderer.RenderAndWriteSingleTerm(term_id)
        except Exception as e:
            e.add_note(f"While building term_id {term_id}")
            raise


def buildTerms(
    term_ids: Iterable[str], config: dict[str, Any] | None = None
) -> None:
    """Build the rendered version for a collection of terms."""
    tic = time.perf_counter()
    raw_ids = list(term_ids)
    if any(fileutils.isAll(tid) for tid in raw_ids):
        log.info("Loading all term identifiers")
        term_list = [
            str(tid)
            for tid in sdotermsource.SdoTermSource.getAllTerms(
                suppressSourceLinks=True
            )
        ]
    else:
        term_list = raw_ids

    if not term_list:
        return

    if config is None:
        config = {
            "stats_providers": stats.get_stats_providers(),
            "build_opts": schema.config.BUILDOPTS,
            "term_docs_dir": schema.constants.TERMDOCSDIR,
        }
    if "examples" not in config:
        config = {
            **config,
            "examples": schemaexamples.SchemaExamples.from_default(),
        }

    shard_numbers = multiprocessing.cpu_count()
    with pretty_logger.BlockLog(
        logger=log,
        message=f"Building {len(term_list)} term pages with {shard_numbers} shards.",
    ):
        sharded_terms: dict[int, list[str]] = collections.defaultdict(list)
        for n, term_id in enumerate(term_list):
            sharded_terms[n % shard_numbers].append(term_id)

        tasks = [(item, config) for item in sharded_terms.items()]

        with multiprocessing.Pool() as pool:
            pool.map(_buildTermIds, tasks)
    elapsed = datetime.timedelta(seconds=time.perf_counter() - tic)
    log.info("%d Terms generated in %s seconds", len(term_list), elapsed)
