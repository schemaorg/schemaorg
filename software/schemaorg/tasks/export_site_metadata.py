"""Floating task that writes the 8 Domain.DOCS site metadata files."""

from __future__ import annotations

import functools
from functools import partial
from pathlib import Path

from schemaorg import constants
from schemaorg.layout import Domain, InputLayout, OutputLayout, Releases
from schemaorg.model import Vocabulary
from schemaorg.progress import ProgressReporter
from schemaorg.renderers import (
    CountsRenderer,
    render_jsonld_tree,
    render_sitemap,
)
from schemaorg.tasks.export_release_files import Artifact, write_artifact
from schemaorg.version import Version, VersionItem


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
        Artifact(
            "Context", docs_file("jsonldcontext.json.txt"), read_context, ()
        ),
        Artifact(
            "Tree",
            docs_file("tree.jsonld"),
            partial(render_jsonld_tree, vocab),
            (),
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


class ExportSiteMetadataTask:
    """Writes the 8 Domain.DOCS metadata files (context, tree, counts, owl, sitemap)."""

    def __init__(
        self,
        input_layout: InputLayout,
        output_layout: OutputLayout,
        version: VersionItem,
        vocab: Vocabulary,
        progress: ProgressReporter,
    ) -> None:
        self.input_layout: InputLayout = input_layout
        self.output_layout: OutputLayout = output_layout
        self.version: VersionItem = version
        self.vocab: Vocabulary = vocab
        self.progress: ProgressReporter = progress

    def run(self) -> list[Path]:
        version_obj = Version(
            self.input_layout.file(Domain.ROOT, constants.VERSIONS_FILE)
        )
        releases = Releases(self.input_layout, version_obj)
        artifacts = plan_site_docs(
            self.vocab, self.version, releases, self.output_layout
        )

        with self.progress.task(
            "Exporting site metadata files",
            total=len(artifacts),
            unit="files",
        ) as p:
            for artifact in artifacts:
                p.step(f"{artifact.name} ({artifact.path.name})")
                write_artifact(artifact)
                p.advance(1)

        return [a.path for a in artifacts]
