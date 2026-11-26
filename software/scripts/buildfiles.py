#!/usr/bin/env python3
"""CLI and orchestrator for generating schema.org release and site doc files."""

from __future__ import annotations

import argparse
from collections.abc import Callable, Sequence
from dataclasses import dataclass
import functools
from functools import partial
import logging
from pathlib import Path

import rdflib
from schemaorg import constants
from schemaorg.graph_loader import GraphLoader, split_release_graphs
from schemaorg.layout import (
    Domain,
    InputLayout,
    Issues,
    NEXT_VERSION,
    OutputLayout,
    Protocol,
    Releases,
    Scope,
)
from schemaorg.layout.releases import VersionRef
from schemaorg.model import Vocabulary, VocabularyLoader
from schemaorg.renderers import (
    CountsRenderer,
    CsvRenderer,
    OwlRenderer,
    PostProcessor,
    RdfRenderer,
    ShapesRenderer,
    protocol_swap,
    render_examples,
    render_http_equivs,
    render_jsonld_context,
    render_jsonld_tree,
    render_sitemap,
)
from schemaorg.sdo_uri import SDO
from schemaorg.version import Version, VersionItem
import util.pretty_logger as pretty_logger

log: logging.Logger = logging.getLogger(__name__)


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
    """RDF and CSV release artifacts for one scope (no file I/O)."""
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
            functools.cache(partial(rdf.render, "nquads", SDO[version.number()])),
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
                version=version, protocol=protocol, scope=scope, extension=ext
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
    """Vocabulary-wide schema release artifacts (no file I/O)."""
    owl = OwlRenderer(graph, version)
    shapes = ShapesRenderer(graph)

    def rel_file(
        filename: str | None = None,
        protocol: str = "",
        scope: str = "",
        extension: str = "",
    ) -> Path:
        return releases.file(
            version=version,
            protocol=protocol,
            scope=scope,
            extension=extension,
            filename=filename,
        )

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


def plan_site_docs(
    vocab: Vocabulary,
    version: VersionItem,
    releases: Releases,
    output_layout: OutputLayout,
) -> list[Artifact]:
    """Website supporting files under Domain.DOCS (no file I/O yet)."""

    def docs_file(filename: str) -> Path:
        return output_layout.file(Domain.DOCS, filename)

    read_context = functools.cache(
        lambda: releases.file(
            version, filename="schemaorgcontext.jsonld"
        ).read_text(encoding="utf-8")
    )
    read_owl = lambda: releases.file(
        version, filename="schemaorg.owl"
    ).read_text(encoding="utf-8")
    counts = CountsRenderer(vocab, version)
    return [
        Artifact("Context", docs_file("jsonldcontext.jsonld"), read_context),
        Artifact("Context", docs_file("jsonldcontext.json"), read_context),
        Artifact("Context", docs_file("jsonldcontext.json.txt"), read_context),
        Artifact(
            "Tree", docs_file("tree.jsonld"), partial(render_jsonld_tree, vocab)
        ),
        Artifact("jsoncounts", docs_file("jsoncounts.json"), counts.json),
        Artifact("jsonpcounts", docs_file("jsonpcounts.js"), counts.jsonp),
        Artifact("Owl", docs_file("schemaorg.owl"), read_owl),
        Artifact(
            "Sitemap",
            docs_file("sitemap.xml"),
            partial(render_sitemap, vocab, version),
        ),
    ]


def export_release_files(
    input_layout: InputLayout,
    output_layout: OutputLayout,
    version: VersionRef = NEXT_VERSION,
) -> None:
    """Loads the source graph, plans, and writes schema release files (9 for next, 35 for numbered)."""
    version_obj = Version(input_layout.file(Domain.ROOT, constants.VERSIONS_FILE))
    target_version = version_obj.resolve(version)
    releases = Releases(output_layout, version_obj)
    issues = Issues(input_layout)

    with pretty_logger.BlockLog(message="Loading source graph", logger=log):
        source_graph = GraphLoader().load(issues.get_ttl_files())
    with pretty_logger.BlockLog(message="Preparing export graphs", logger=log):
        all_graph, current_graph = split_release_graphs(source_graph)
        vocab = VocabularyLoader(all_graph, version=target_version).load()

    csv = CsvRenderer(vocab)
    artifacts = [
        *export_scoped(Scope.ALL, all_graph, csv, target_version, releases),
        *export_scoped(Scope.CURRENT, current_graph, csv, target_version, releases),
        *export_release_unscoped(
            all_graph, vocab, target_version, releases, issues.get_example_files()
        ),
    ]
    expected_paths = {a.path for a in artifacts}
    target_dir = releases.dir(target_version)
    if target_dir.is_dir():
        for existing in target_dir.iterdir():
            if existing.is_file() and existing not in expected_paths:
                existing.unlink()

    for artifact in artifacts:
        with pretty_logger.BlockLog(
            message=f"Exporting {artifact.name}: {artifact.path}", logger=log
        ):
            write_artifact(artifact)


def export_site_docs(
    input_layout: InputLayout,
    output_layout: OutputLayout,
    version: VersionRef = NEXT_VERSION,
    vocab: Vocabulary | None = None,
) -> None:
    """Loads the target release (unless vocab is supplied) and writes Domain.DOCS site files."""
    version_obj = Version(input_layout.file(Domain.ROOT, constants.VERSIONS_FILE))
    target_version = version_obj.resolve(version)
    releases = Releases(input_layout, version_obj)

    if vocab is None:
        ttl_files = releases.get_ttl_files(target_version)
        with pretty_logger.BlockLog(
            message=f"Loading release graph for {target_version}", logger=log
        ):
            all_graph = GraphLoader().load(ttl_files)
            vocab = VocabularyLoader(all_graph, version=target_version).load()

    for artifact in plan_site_docs(
        vocab, target_version, releases, output_layout
    ):
        with pretty_logger.BlockLog(
            message=f"Exporting {artifact.name}: {artifact.path}", logger=log
        ):
            write_artifact(artifact)


def main(argv: Sequence[str] | None = None) -> None:
    logging.basicConfig(level=logging.INFO)

    parser = argparse.ArgumentParser(
        description="Generate all vocabulary/schema release files."
    )
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=constants.PROJECT_ROOT,
        help="Root directory of the schema.org input layout.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=constants.PROJECT_ROOT / "data",
        help="Root directory containing the releases/ output directory.",
    )
    parser.add_argument(
        "--version",
        default=NEXT_VERSION,
        help="Target release version ('next', 'latest', or declared X.Y).",
    )

    args = parser.parse_args(argv)
    export_release_files(
        InputLayout(args.input_dir),
        OutputLayout(args.output_dir),
        version=args.version,
    )


if __name__ == "__main__":
    main()
