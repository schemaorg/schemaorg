"""Immutable read-only data bundle loaded once for Stage 2 site tasks."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import rdflib

from schemaorg import constants
from schemaorg.collaborators import CollaboratorRegistry
from schemaorg.graph_loader import GraphLoader
from schemaorg.jsonld_slice import TermJsonLdIndex
from schemaorg.layout import (
    Domain,
    InputLayout,
    OutputLayout,
    Releases,
    StatsLayout,
    StatsProvider,
)
from schemaorg.model import Vocabulary, VocabularyLoader
from schemaorg.progress import ProgressReporter
from schemaorg.term_view import TermViewCatalog
from schemaorg.version import Version, VersionItem
from SchemaExamples.schemaexamples import SchemaExamples


@dataclass(frozen=True)
class SiteBundle:
    """All read-only inputs shared across site-rendering tasks."""

    input_layout: InputLayout
    target_version: VersionItem
    current_version: VersionItem
    release_file: Path
    graph: rdflib.Graph
    vocab: Vocabulary
    collaborators: CollaboratorRegistry
    catalog: TermViewCatalog
    jsonld_index: TermJsonLdIndex
    examples: SchemaExamples
    stats_providers: tuple[StatsProvider, ...]

    @classmethod
    def from_release(
        cls,
        input_layout: InputLayout,
        releases_layout: InputLayout | OutputLayout,
        target_version: VersionItem,
        progress: ProgressReporter,
    ) -> SiteBundle:
        version_registry = Version(
            input_layout.file(Domain.ROOT, constants.VERSIONS_FILE)
        )
        current_version = version_registry.current()
        releases = Releases(releases_layout, version_registry)
        release_file = releases.file(target_version)
        if not release_file.is_file():
            raise FileNotFoundError(
                f"Release file not found: {release_file}. "
                "Please run --buildrelease first."
            )
        release_jsonld = releases.file(target_version, extension=".jsonld")

        with progress.task(
            f"Loading site bundle ({target_version.number()})",
            total=6,
            unit="steps",
        ) as p:
            p.step("release graph")
            graph = GraphLoader.load([release_file])
            p.advance(1)

            p.step("vocabulary")
            vocab = VocabularyLoader(graph, version=target_version).load()
            p.advance(1)

            p.step("collaborators")
            collaborators = CollaboratorRegistry.from_layout(
                input_layout, vocab
            )
            catalog = TermViewCatalog.from_graph(graph, vocab, collaborators)
            p.advance(1)

            p.step("json-ld slices")
            jsonld_index = TermJsonLdIndex.from_graph(
                graph,
                jsonld_file=release_jsonld if release_jsonld.is_file() else None,
            )
            p.advance(1)

            p.step("examples")
            examples = SchemaExamples.from_layout(input_layout)
            p.advance(1)

            p.step("usage stats")
            stats_providers = tuple(StatsLayout(input_layout).get_stats())
            p.advance(1)

        return cls(
            input_layout=input_layout,
            target_version=target_version,
            current_version=current_version,
            release_file=release_file,
            graph=graph,
            vocab=vocab,
            collaborators=collaborators,
            catalog=catalog,
            jsonld_index=jsonld_index,
            examples=examples,
            stats_providers=stats_providers,
        )
