#!/usr/bin/env python3
"""CLI and compatibility shell for schema.org release and site metadata exports."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
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
from schemaorg.tasks.export_release_files import (
    ExportReleaseFilesTask,
    write_artifacts,
)
from schemaorg.tasks.export_site_metadata import plan_site_docs
from schemaorg.version import Version

log: logging.Logger = logging.getLogger(__name__)


def export_release_files(
    input_layout: InputLayout,
    output_layout: OutputLayout,
    version: VersionRef = NEXT_VERSION,
) -> None:
    """Load the source graph and write schema release files (9 for next, 35 for numbered)."""
    # shortcut: compatibility wrapper for legacy callers (double-parses
    # versions.json with ExportReleaseFilesTask); slated for removal once
    # buildsite.py and tests call ExportReleaseFilesTask directly.
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
    """Write the 8 Domain.DOCS site metadata files."""
    # shortcut: temporary compatibility bridge for buildsite.py; slated for
    # removal once buildsite.py switches to ExportSiteMetadataTask(bundle=...).
    version_obj = Version(
        input_layout.file(Domain.ROOT, constants.VERSIONS_FILE)
    )
    target_version = version_obj.resolve(version)
    releases = Releases(input_layout, version_obj)
    if vocab is None:
        all_graph = GraphLoader.load(releases.get_ttl_files(target_version))
        vocab = VocabularyLoader(all_graph, version=target_version).load()

    artifacts = plan_site_docs(
        vocab, target_version, releases.dir(target_version), output_layout
    )
    write_artifacts(
        artifacts,
        LogProgressReporter(logger=log, log_steps=True),
        "Exporting site metadata files",
    )


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
