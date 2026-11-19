#!/usr/bin/env python3
"""CLI and orchestrator for generating schema.org release and site doc files."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import functools
from functools import partial
import logging
from pathlib import Path

from schemaorg import constants
from schemaorg.graph_loader import GraphLoader
from schemaorg.layout import (
    Domain,
    InputLayout,
    NEXT_VERSION,
    OutputLayout,
    Releases,
)
from schemaorg.layout.releases import VersionRef
from schemaorg.model import Vocabulary, VocabularyLoader
from schemaorg.progress import LogProgressReporter
from schemaorg.renderers import (
    CountsRenderer,
    render_jsonld_tree,
    render_sitemap,
)
from schemaorg.tasks.export_release_files import (
    Artifact,
    ExportReleaseFilesTask,
    PROTOCOL_VARIANTS,
    export_release_unscoped,
    export_scoped,
    write_artifact,
)
from schemaorg.version import Version, VersionItem
import util.pretty_logger as pretty_logger

log: logging.Logger = logging.getLogger(__name__)


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
        Artifact("Context", docs_file("jsonldcontext.jsonld"), read_context, ()),
        Artifact("Context", docs_file("jsonldcontext.json"), read_context, ()),
        Artifact("Context", docs_file("jsonldcontext.json.txt"), read_context, ()),
        Artifact(
            "Tree", docs_file("tree.jsonld"), partial(render_jsonld_tree, vocab), ()
        ),
        Artifact("jsoncounts", docs_file("jsoncounts.json"), counts.json, ()),
        Artifact("jsonpcounts", docs_file("jsonpcounts.js"), counts.jsonp, ()),
        Artifact("Owl", docs_file("schemaorg.owl"), read_owl, ()),
        Artifact(
            "Sitemap",
            docs_file("sitemap.xml"),
            partial(render_sitemap, vocab, version),
            (),
        ),
    ]


def export_release_files(
    input_layout: InputLayout,
    output_layout: OutputLayout,
    version: VersionRef = NEXT_VERSION,
) -> None:
    """Loads the source graph, plans, and writes schema release files (9 for next, 35 for numbered)."""
    version_obj = Version(
        input_layout.file(Domain.ROOT, constants.VERSIONS_FILE)
    )
    target_version = version_obj.resolve(version)
    ExportReleaseFilesTask(
        input_layout=input_layout,
        output_layout=output_layout,
        version=target_version,
        progress=LogProgressReporter(logger=log, log_steps=True),
    ).run()


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
            all_graph = GraphLoader.load(ttl_files)
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
