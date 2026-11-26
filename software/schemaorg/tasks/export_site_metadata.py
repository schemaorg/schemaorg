"""Floating task that writes the 8 Domain.DOCS site metadata files."""

from __future__ import annotations

from dataclasses import dataclass
import functools
from functools import partial
from pathlib import Path

from schemaorg.layout import Domain, OutputLayout
from schemaorg.model import Vocabulary
from schemaorg.progress import ProgressReporter
from schemaorg.renderers import (
    CountsRenderer,
    render_jsonld_tree,
    render_sitemap,
)
from schemaorg.site_bundle import SiteBundle
from schemaorg.tasks.export_release_files import Artifact, write_artifact
from schemaorg.version import VersionItem

_REQUIRED_RELEASE_FILES: tuple[str, ...] = (
    "schemaorgcontext.jsonld",
    "schemaorg.owl",
)


def plan_site_docs(
    vocab: Vocabulary,
    version: VersionItem,
    release_dir: Path,
    output_layout: OutputLayout,
) -> list[Artifact]:
    """Website supporting files under Domain.DOCS."""

    def docs_file(filename: str) -> Path:
        return output_layout.file(Domain.DOCS, filename)

    read_context = functools.cache(
        partial(
            (release_dir / "schemaorgcontext.jsonld").read_text,
            encoding="utf-8",
        )
    )
    read_owl = partial(
        (release_dir / "schemaorg.owl").read_text, encoding="utf-8"
    )
    counts = CountsRenderer(vocab, version)
    return [
        Artifact("Context", docs_file("jsonldcontext.jsonld"), read_context),
        Artifact("Context", docs_file("jsonldcontext.json"), read_context),
        Artifact("Context", docs_file("jsonldcontext.json.txt"), read_context),
        Artifact(
            "Tree",
            docs_file("tree.jsonld"),
            partial(render_jsonld_tree, vocab),
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


@dataclass(frozen=True)
class ExportSiteMetadataTask:
    """Writes the 8 Domain.DOCS metadata files (context, tree, counts, owl, sitemap)."""

    bundle: SiteBundle
    output_layout: OutputLayout
    progress: ProgressReporter

    def run(self) -> list[Path]:
        release_dir = self.bundle.release_file.parent
        for filename in _REQUIRED_RELEASE_FILES:
            required = release_dir / filename
            if not required.is_file():
                raise FileNotFoundError(
                    f"Release file not found: {required}. "
                    "Generate release files first."
                )

        artifacts = plan_site_docs(
            self.bundle.vocab,
            self.bundle.target_version,
            release_dir,
            self.output_layout,
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
