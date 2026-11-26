from __future__ import annotations

from collections.abc import Iterable, Sequence
import datetime
import logging
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
from schemaorg.template_renderer import TemplateRenderer
from schemaorg.term_view import TermKind, TermView, TermViewCatalog
import SchemaExamples.schemaexamples as schemaexamples
import util.fileutils as fileutils
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
        term_docs_dir: str,
        build_opts: Sequence[str] = (),
        examples: schemaexamples.SchemaExamples | None = None,
        catalog: TermViewCatalog | None = None,
        jsonld_index: TermJsonLdIndex | None = None,
        template_renderer: TemplateRenderer | None = None,
    ) -> None:
        if template_renderer is not None and build_opts:
            raise ValueError(
                "Cannot pass both template_renderer and non-empty build_opts"
            )
        self.stats_providers = stats_providers
        self.term_docs_dir = term_docs_dir
        self.examples = examples
        self.catalog = catalog
        self.jsonld_index = jsonld_index
        self.template_renderer = template_renderer or TemplateRenderer(
            paths.DefaultInputLayout(),
            schema.target_version(),
            build_opts,
        )
        self.template = self.template_renderer.get_template(
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
            "docsdir": self.term_docs_dir,
            "term": term,
            "jsonldPayload": json,
            "examples": examples,
            "stats_badges": stats_badges,
        }
        return self.template_renderer.render(self.template, extra_vars)

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
                    self.examples = schemaexamples.SchemaExamples.from_layout(
                        paths.DefaultInputLayout()
                    )
                examples = self.examples.examplesForTerm(term.id)
                json_str = self.jsonld_index.render_for(term)
                pageout = self.termtemplateRender(term, examples, json_str)
                termFileName(term.id).write_text(pageout, encoding="utf-8")
            except Exception as e:
                e.add_note(f"Term definition: {term.id}")
                raise


def buildTerms(
    term_ids: Iterable[str],
    config: dict[str, Any] | None = None,
    catalog: TermViewCatalog | None = None,
    jsonld_index: TermJsonLdIndex | None = None,
) -> None:
    """Build the rendered version for a collection of terms."""
    tic = time.perf_counter()

    if config is None:
        config = {
            "stats_providers": stats.get_stats_providers(),
            "build_opts": schema.config.BUILDOPTS,
            "term_docs_dir": schema.constants.TERMDOCSDIR,
            "target_version": schema.config.TARGET_VERSION,
            "output_dir": schema.config.OUTPUTDIR,
        }

    orig_target = schema.config.TARGET_VERSION
    orig_output = schema.config.OUTPUTDIR
    try:
        if config.get("target_version") is not None:
            schema.config.TARGET_VERSION = config["target_version"]
        if config.get("output_dir") is not None:
            schema.config.OUTPUTDIR = config["output_dir"]

        release_file = config.get("release_file")
        if catalog is None or jsonld_index is None:
            catalog, jsonld_index = _load_bundle(
                Path(release_file).resolve()
                if release_file is not None
                else None
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
            examples = schemaexamples.SchemaExamples.from_layout(
                paths.DefaultInputLayout()
            )

        template_renderer = config.get("template_renderer")
        if template_renderer is not None and config.get("build_opts"):
            raise ValueError(
                "Cannot pass both template_renderer and non-empty build_opts"
            )
        if template_renderer is None:
            template_renderer = TemplateRenderer(
                paths.DefaultInputLayout(),
                schema.target_version(),
                config.get("build_opts", ()),
            )

        renderer = TermPageRenderer(
            stats_providers=config["stats_providers"],
            term_docs_dir=config["term_docs_dir"],
            examples=examples,
            catalog=catalog,
            jsonld_index=jsonld_index,
            template_renderer=template_renderer,
        )
        with pretty_logger.BlockLog(
            logger=log,
            message=f"Building {len(term_list)} term pages.",
        ):
            for term_id in term_list:
                try:
                    renderer.RenderAndWriteSingleTerm(term_id)
                except Exception as e:
                    e.add_note(f"While building term_id {term_id}")
                    raise
    finally:
        schema.config.TARGET_VERSION = orig_target
        schema.config.OUTPUTDIR = orig_output
    elapsed = datetime.timedelta(seconds=time.perf_counter() - tic)
    log.info("%d Terms generated in %s seconds", len(term_list), elapsed)
