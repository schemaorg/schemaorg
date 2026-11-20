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

from schemaorg.collaborators import CollaboratorRegistry
from schemaorg.graph_loader import GraphLoader
from schemaorg.jsonld_slice import TermJsonLdIndex
from schemaorg.layout import Issues, Releases
from schemaorg.layout.stats_layout import StatsProvider
from schemaorg.model import VocabularyLoader
from schemaorg.term_view import TermKind, TermView, TermViewCatalog
import SchemaExamples.schemaexamples as schemaexamples
import util.fileutils as fileutils
import util.jinja_render as jinja_render
import util.paths as paths
import util.pretty_logger as pretty_logger
import util.schema as schema
import util.stats as stats

log: logging.Logger = logging.getLogger(__name__)

# Prewarmed in parent before multiprocessing.Pool forks so workers share via COW.
_SHARED_CATALOG: TermViewCatalog | None = None
_SHARED_JSONLD: TermJsonLdIndex | None = None
_SHARED_EXAMPLES: schemaexamples.SchemaExamples | None = None
_SHARED_RELEASE_KEY: str | None = None


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


def _load_bundle(
    release_file: Path | None = None,
) -> tuple[TermViewCatalog, TermJsonLdIndex]:
    input_layout = paths.DefaultInputLayout()
    jsonld_file: Path | None = None
    if release_file is not None:
        ttl_files: Sequence[Path] = [release_file]
        candidate = release_file.with_suffix(".jsonld")
        if candidate.is_file():
            jsonld_file = candidate
    else:
        releases = Releases(input_layout, schema.VERSION)
        target = schema.target_version()
        rel_ttl = releases.file(target)
        if rel_ttl.is_file():
            ttl_files = [rel_ttl]
            candidate = releases.file(target, extension=".jsonld")
            if candidate.is_file():
                jsonld_file = candidate
        else:
            ttl_files = Issues(input_layout).get_ttl_files()

    graph = GraphLoader.load(ttl_files)
    vocab = VocabularyLoader(graph, version=schema.target_version()).load()
    collaborators = CollaboratorRegistry.from_layout(input_layout, vocab)
    catalog = TermViewCatalog.from_graph(graph, vocab, collaborators)
    jsonld_index = TermJsonLdIndex.from_graph(graph, jsonld_file=jsonld_file)
    return catalog, jsonld_index


class TermPageRenderer:
    """Encapsulates the rendering and file-writing operations for terms."""

    def __init__(
        self,
        stats_providers: Sequence[StatsProvider],
        build_opts: Sequence[str],
        term_docs_dir: str,
        examples: schemaexamples.SchemaExamples | None = None,
        catalog: TermViewCatalog | None = None,
        jsonld_index: TermJsonLdIndex | None = None,
    ) -> None:
        self.stats_providers = stats_providers
        self.build_opts = build_opts
        self.term_docs_dir = term_docs_dir
        self.examples = examples
        self.catalog = catalog
        self.jsonld_index = jsonld_index
        self.template = jinja_render.get_jinja_env().get_template(
            "terms/TermPage.j2"
        )

    def termtemplateRender(
        self,
        term: TermView,
        examples: Sequence[schemaexamples.Example],
        json: str,
    ) -> str:
        """Render the term with examples and associated JSON."""
        assert isinstance(term, TermView)
        stats_badges = []
        if term.uri:
            cleaned_uri = unicodedata.normalize("NFC", term.uri.strip())
            for provider in self.stats_providers:
                if badge := provider.stats_map.get(cleaned_uri):
                    stats_badges.append({
                        "provider_name": provider.name,
                        "badge": badge,
                        "date": provider.date,
                        "description": provider.description,
                    })
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
            if self.catalog is None or self.jsonld_index is None:
                self.catalog, self.jsonld_index = _load_bundle()
            term = self.catalog.get(term_key)
            if not term:
                log.error("No such term: %s", term_key)
                return
            if term.termType == TermKind.REFERENCE:
                return
            try:
                if self.examples is None:
                    self.examples = schemaexamples.SchemaExamples.from_default()
                examples = self.examples.examplesForTerm(term.id)
                json_str = self.jsonld_index.render_for(term)
                pageout = self.termtemplateRender(term, examples, json_str)
                termFileName(term.id).write_text(pageout, encoding="utf-8")
            except Exception as e:
                e.add_note(f"Term definition: {term.id}")
                raise


_WORKER_CONFIG_KEYS = frozenset({
    "target_version",
    "output_dir",
    "release_file",
})


def _init_worker(
    target_version: str | None = None,
    output_dir: str | None = None,
    release_file: str | Path | None = None,
) -> None:
    global _SHARED_CATALOG, _SHARED_JSONLD, _SHARED_RELEASE_KEY
    if target_version is not None:
        schema.config.TARGET_VERSION = target_version
    if output_dir is not None:
        schema.config.OUTPUTDIR = output_dir
    if release_file is not None:
        key = str(Path(release_file).resolve())
        if _SHARED_CATALOG is None or _SHARED_RELEASE_KEY != key:
            _SHARED_CATALOG, _SHARED_JSONLD = _load_bundle(Path(key))
            _SHARED_RELEASE_KEY = key


def _buildTermIds(args: tuple[tuple[int, list[str]], dict[str, Any]]) -> None:
    (shard, term_ids), config = args
    pretty_logger.MakeRootLogPretty(shard=shard)
    _init_worker(
        target_version=config.get("target_version"),
        output_dir=config.get("output_dir"),
        release_file=config.get("release_file"),
    )
    renderer_config = {
        k: v for k, v in config.items() if k not in _WORKER_CONFIG_KEYS
    }
    renderer_config.setdefault("catalog", _SHARED_CATALOG)
    renderer_config.setdefault("jsonld_index", _SHARED_JSONLD)
    if renderer_config.get("examples") is None and _SHARED_EXAMPLES is not None:
        renderer_config["examples"] = _SHARED_EXAMPLES
    renderer = TermPageRenderer(**renderer_config)
    for term_id in term_ids:
        try:
            renderer.RenderAndWriteSingleTerm(term_id)
        except Exception as e:
            e.add_note(f"While building term_id {term_id}")
            raise


def buildTerms(
    term_ids: Iterable[str],
    config: dict[str, Any] | None = None,
    catalog: TermViewCatalog | None = None,
    jsonld_index: TermJsonLdIndex | None = None,
) -> None:
    """Build the rendered version for a collection of terms."""
    global _SHARED_CATALOG, _SHARED_JSONLD, _SHARED_EXAMPLES, _SHARED_RELEASE_KEY
    tic = time.perf_counter()

    if config is None:
        config = {
            "stats_providers": stats.get_stats_providers(),
            "build_opts": schema.config.BUILDOPTS,
            "term_docs_dir": schema.constants.TERMDOCSDIR,
            "target_version": schema.config.TARGET_VERSION,
            "output_dir": schema.config.OUTPUTDIR,
        }

    release_file = config.get("release_file")
    release_key = (
        str(Path(release_file).resolve()) if release_file is not None else None
    )

    if catalog is None or jsonld_index is None:
        catalog, jsonld_index = _load_bundle(
            Path(release_key) if release_key else None
        )

    raw_ids = list(term_ids)
    if any(fileutils.isAll(tid) for tid in raw_ids):
        log.info("Loading all term identifiers")
        term_list = [v.id for v in catalog.all_views()]
    else:
        term_list = raw_ids

    if not term_list:
        return

    examples = config.get("examples")
    if examples is None:
        examples = schemaexamples.SchemaExamples.from_default()

    _SHARED_CATALOG = catalog
    _SHARED_JSONLD = jsonld_index
    _SHARED_EXAMPLES = examples
    _SHARED_RELEASE_KEY = release_key

    # Strip heavy objects from per-task IPC payload; workers read _SHARED_* via COW.
    light_config = {
        k: v
        for k, v in config.items()
        if k not in ("examples", "catalog", "jsonld_index")
    }

    shard_numbers = multiprocessing.cpu_count()
    with pretty_logger.BlockLog(
        logger=log,
        message=f"Building {len(term_list)} term pages with {shard_numbers} shards.",
    ):
        sharded_terms: dict[int, list[str]] = collections.defaultdict(list)
        for n, term_id in enumerate(term_list):
            sharded_terms[n % shard_numbers].append(term_id)

        tasks = [(item, light_config) for item in sharded_terms.items()]

        with multiprocessing.Pool(
            initializer=_init_worker,
            initargs=(
                light_config.get("target_version"),
                light_config.get("output_dir"),
                light_config.get("release_file"),
            ),
        ) as pool:
            pool.map(_buildTermIds, tasks)
    elapsed = datetime.timedelta(seconds=time.perf_counter() - tic)
    log.info("%d Terms generated in %s seconds", len(term_list), elapsed)
