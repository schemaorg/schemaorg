"""Floating task that generates schema.org release artifacts."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass
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
    """One output file: its renderer, destination, and optional post-processor."""

    name: str
    path: Path
    render: Callable[[], str]
    post: PostProcessor | None = None

    def write(self, rendered: str | None = None) -> None:
        content = self.render() if rendered is None else rendered
        if self.post is not None:
            content = self.post(content)
        self.path.write_text(content, encoding="utf-8")


def write_artifacts(
    artifacts: Sequence[Artifact],
    progress: ProgressReporter,
    description: str,
) -> list[Path]:
    """Write artifacts with progress, rendering each shared callable once."""
    grouped: dict[int, list[Artifact]] = {}
    for artifact in artifacts:
        grouped.setdefault(id(artifact.render), []).append(artifact)

    with progress.task(description, total=len(artifacts), unit="files") as p:
        for group in grouped.values():
            rendered = group[0].render()
            for artifact in group:
                p.step(f"{artifact.name} ({artifact.path.name})")
                artifact.write(rendered)
                p.advance(1)
    return [a.path for a in artifacts]


# Each (https, http) file pair shares one render; only post-processing differs.
_PROTOCOL_VARIANTS: tuple[tuple[Protocol, PostProcessor | None], ...] = (
    (Protocol.HTTPS, None),
    (Protocol.HTTP, protocol_swap()),
)


def plan_scoped(
    scope: Scope,
    graph: rdflib.Graph,
    csv: CsvRenderer,
    version: VersionItem,
    releases: Releases,
) -> list[Artifact]:
    """Plan RDF and CSV release artifacts for one scope."""
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
        ("RDFExport.json-ld", ".jsonld", partial(rdf.render, "json-ld")),
        (
            "RDFExport.nquads",
            ".nq",
            partial(rdf.render, "nquads", SDO[version.number()]),
        ),
        ("RDFExport.nt", ".nt", partial(rdf.render, "nt")),
        ("RDFExport.rdf", ".rdf", partial(rdf.render, "rdf")),
        ("RDFExport.turtle", ".ttl", partial(rdf.render, "turtle")),
        ("CSVExports", "-types.csv", partial(csv.types, include_retired)),
        (
            "CSVExports",
            "-properties.csv",
            partial(csv.properties, include_retired),
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
            post,
        )
        for name, ext, render in scoped_renders
        for protocol, post in _PROTOCOL_VARIANTS
    ]


def plan_release_unscoped(
    graph: rdflib.Graph,
    vocab: Vocabulary,
    version: VersionItem,
    releases: Releases,
    example_files: Sequence[Path],
) -> list[Artifact]:
    """Plan vocabulary-wide schema release artifacts."""
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
            total=3,
            unit="steps",
        ) as p:
            p.step("parsing Turtle files")
            source_graph = GraphLoader.load(issues.get_ttl_files())
            p.advance(1)
            p.step("preparing export graphs")
            all_graph, current_graph = split_release_graphs(source_graph)
            p.advance(1)
            p.step("loading vocabulary")
            vocab = VocabularyLoader(all_graph, version=version).load()
            p.advance(1)

        csv = CsvRenderer(vocab)
        artifacts = [
            *plan_scoped(Scope.ALL, all_graph, csv, version, releases),
            *plan_scoped(Scope.CURRENT, current_graph, csv, version, releases),
            *plan_release_unscoped(
                all_graph,
                vocab,
                version,
                releases,
                issues.get_example_files(),
            ),
        ]

        written = write_artifacts(
            artifacts,
            self.progress,
            f"Exporting release files ({version.number()})",
        )

        expected_paths = set(written)
        for existing in releases.dir(version).iterdir():
            if existing.is_file() and existing not in expected_paths:
                existing.unlink()

        return written
