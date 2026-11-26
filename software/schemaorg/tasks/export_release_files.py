"""Floating task that generates schema.org release artifacts."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
import functools
from functools import partial
from pathlib import Path

import rdflib

from schemaorg import constants
from schemaorg.graph_loader import GraphLoader, split_release_graphs
from schemaorg.layout import (
    Domain,
    InputLayout,
    Issues,
    OutputLayout,
    Protocol,
    Releases,
    Scope,
)
from schemaorg.model import Vocabulary, VocabularyLoader
from schemaorg.progress import ProgressReporter
from schemaorg.renderers import (
    CsvRenderer,
    OwlRenderer,
    PostProcessor,
    RdfRenderer,
    ShapesRenderer,
    protocol_swap,
    render_examples,
    render_http_equivs,
    render_jsonld_context,
)
from schemaorg.sdo_uri import SDO
from schemaorg.version import Version, VersionItem


@dataclass(frozen=True)
class Artifact:
    """One output file: its renderer, destination, and text post-processors."""

    name: str
    path: Path
    render: Callable[[], str]
    post: tuple[PostProcessor, ...] = ()


def write_artifact(artifact: Artifact) -> None:
    content = artifact.render()
    for step in artifact.post:
        content = step(content)
    artifact.path.write_text(content, encoding="utf-8")


# Each (https, http) file pair shares one render; only post-processing differs.
PROTOCOL_VARIANTS: tuple[tuple[Protocol, tuple[PostProcessor, ...]], ...] = (
    (Protocol.HTTPS, ()),
    (Protocol.HTTP, (protocol_swap(),)),
)


def export_scoped(
    scope: Scope,
    graph: rdflib.Graph,
    csv: CsvRenderer,
    version: VersionItem,
    releases: Releases,
) -> list[Artifact]:
    """RDF and CSV release artifacts for one scope."""
    rdf = RdfRenderer(graph)
    if version.is_next():
        return [
            Artifact(
                "RDFExport.turtle",
                releases.file(
                    version=version,
                    protocol=Protocol.HTTPS,
                    scope=scope,
                    extension=".ttl",
                ),
                partial(rdf.render, "turtle"),
            )
        ]
    include_retired = scope == Scope.ALL
    scoped_renders: tuple[tuple[str, str, Callable[[], str]], ...] = (
        (
            "RDFExport.json-ld",
            ".jsonld",
            functools.cache(partial(rdf.render, "json-ld")),
        ),
        (
            "RDFExport.nquads",
            ".nq",
            functools.cache(
                partial(rdf.render, "nquads", SDO[version.number()])
            ),
        ),
        ("RDFExport.nt", ".nt", functools.cache(partial(rdf.render, "nt"))),
        ("RDFExport.rdf", ".rdf", functools.cache(partial(rdf.render, "rdf"))),
        (
            "RDFExport.turtle",
            ".ttl",
            functools.cache(partial(rdf.render, "turtle")),
        ),
        (
            "CSVExports",
            "-types.csv",
            functools.cache(partial(csv.types, include_retired)),
        ),
        (
            "CSVExports",
            "-properties.csv",
            functools.cache(partial(csv.properties, include_retired)),
        ),
    )
    return [
        Artifact(
            name,
            releases.file(
                version=version,
                protocol=protocol,
                scope=scope,
                extension=ext,
            ),
            render,
            finisher,
        )
        for protocol, finisher in PROTOCOL_VARIANTS
        for name, ext, render in scoped_renders
    ]


def export_release_unscoped(
    graph: rdflib.Graph,
    vocab: Vocabulary,
    version: VersionItem,
    releases: Releases,
    example_files: Sequence[Path],
) -> list[Artifact]:
    """Vocabulary-wide schema release artifacts."""
    owl = OwlRenderer(graph, version)
    shapes = ShapesRenderer(graph)
    rel_file = partial(releases.file, version=version, protocol="")

    return [
        Artifact(
            "Context",
            rel_file(filename="schemaorgcontext.jsonld"),
            partial(render_jsonld_context, graph, vocab),
        ),
        Artifact("Owl", rel_file(filename="schemaorg.owl"), owl.render),
        Artifact(
            "Httpequivs",
            rel_file(filename="httpequivs.ttl"),
            partial(render_http_equivs, vocab),
        ),
        Artifact(
            "Shex_Shacl",
            rel_file(scope="shapes", extension=".shexj"),
            shapes.shex,
        ),
        Artifact(
            "Shex_Shacl",
            rel_file(scope="shapes", extension=".shacl"),
            shapes.shacl,
        ),
        Artifact(
            "Shex_Shacl",
            rel_file(scope="subclasses", extension=".shacl"),
            shapes.subclasses,
        ),
        Artifact(
            "Examples",
            rel_file(filename="schemaorg-all-examples.txt"),
            partial(render_examples, example_files),
        ),
    ]


@dataclass(frozen=True)
class ExportReleaseFilesTask:
    """Loads source TTL/example files and writes schema release artifacts (9 for next, 35 for numbered)."""

    input_layout: InputLayout
    output_layout: OutputLayout
    version: VersionItem
    progress: ProgressReporter

    def run(self) -> list[Path]:
        version_obj = Version(
            self.input_layout.file(Domain.ROOT, constants.VERSIONS_FILE)
        )
        releases = Releases(self.output_layout, version_obj)
        version = releases.resolve(self.version)
        issues = Issues(self.input_layout)

        with self.progress.task(
            f"Loading source graph ({version.number()})",
            total=None,
            unit="steps",
        ) as p:
            p.step("parsing Turtle files")
            source_graph = GraphLoader.load(issues.get_ttl_files())
            p.step("preparing export graphs")
            all_graph, current_graph = split_release_graphs(source_graph)
            vocab = VocabularyLoader(all_graph, version=version).load()

        csv = CsvRenderer(vocab)
        artifacts = [
            *export_scoped(Scope.ALL, all_graph, csv, version, releases),
            *export_scoped(Scope.CURRENT, current_graph, csv, version, releases),
            *export_release_unscoped(
                all_graph,
                vocab,
                version,
                releases,
                issues.get_example_files(),
            ),
        ]

        with self.progress.task(
            f"Exporting release files ({version.number()})",
            total=len(artifacts),
            unit="files",
        ) as p:
            for artifact in artifacts:
                p.step(f"{artifact.name} ({artifact.path.name})")
                write_artifact(artifact)
                p.advance(1)

        expected_paths = {a.path for a in artifacts}
        target_dir = releases.dir(version)
        if target_dir.is_dir():
            for existing in target_dir.iterdir():
                if existing.is_file() and existing not in expected_paths:
                    existing.unlink()

        return [a.path for a in artifacts]
