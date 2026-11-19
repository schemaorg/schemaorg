"""Floating task that renders HTML definition pages for schema.org terms."""

from __future__ import annotations

from collections.abc import Sequence
import logging
from pathlib import Path
from typing import Any
import unicodedata

from schemaorg.layout import Domain, OutputLayout
from schemaorg.progress import ProgressReporter
from schemaorg.site_bundle import SiteBundle
from schemaorg.template_renderer import TemplateRenderer
from schemaorg.term_view import TermKind


def _is_all(token: str) -> bool:
    return token.strip().upper() == "ALL"


def term_output_path(output_layout: OutputLayout, term_id: str) -> Path:
    """Resolve the destination HTML file path for a term identifier."""
    if not term_id:
        raise ValueError("Empty term_id")
    first = term_id[0]
    if first.islower():
        sub_dir = "properties"
    elif first.isupper() or first.isdigit():
        sub_dir = "types"
    else:
        raise ValueError(f"Invalid term_id: '{term_id}'")
    return output_layout.file(
        Domain.TERMS, f"{sub_dir}/{first}/{term_id}.html"
    )


class RenderTermPagesTask:
    """Renders term HTML pages from a SiteBundle into an OutputLayout."""

    def __init__(
        self,
        bundle: SiteBundle,
        output_layout: OutputLayout,
        build_opts: Sequence[str],
        term_ids: Sequence[str],
        progress: ProgressReporter,
    ) -> None:
        self.bundle: SiteBundle = bundle
        self.output_layout: OutputLayout = output_layout
        self.build_opts: tuple[str, ...] = tuple(build_opts)
        self.term_ids: tuple[str, ...] = tuple(term_ids)
        self.progress: ProgressReporter = progress

    def _stats_badges(self, uri: str) -> list[dict[str, str]]:
        if not uri:
            return []
        cleaned = unicodedata.normalize("NFC", uri.strip())
        badges: list[dict[str, str]] = []
        for provider in self.bundle.stats_providers:
            if badge := provider.stats_map.get(cleaned):
                badges.append({
                    "provider_name": provider.name,
                    "badge": badge,
                    "date": provider.date,
                    "description": provider.description,
                })
        return badges

    def run(self) -> int:
        if not self.term_ids:
            return 0
        term_list = (
            [v.id for v in self.bundle.catalog.all_views()]
            if any(_is_all(t) for t in self.term_ids)
            else list(self.term_ids)
        )
        if not term_list:
            return 0

        renderer = TemplateRenderer(
            self.bundle.input_layout,
            self.bundle.target_version,
            self.build_opts,
        )
        template = renderer.get_template("terms/TermPage.j2")

        written = 0
        with self.progress.task(
            "Rendering term pages",
            total=len(term_list),
            unit="pages",
        ) as p:
            for term_id in term_list:
                p.step(term_id)
                term = self.bundle.catalog.get(term_id)
                if term is None:
                    p.log(f"No such term: {term_id}", logging.ERROR)
                    p.advance(1)
                    continue
                if term.termType == TermKind.REFERENCE:
                    p.advance(1)
                    continue

                try:
                    extra_vars: dict[str, Any] = {
                        "title": term.label,
                        "term": term,
                        "jsonldPayload": self.bundle.jsonld_index.render_for(
                            term
                        ),
                        "examples": self.bundle.examples.examplesForTerm(
                            term.id
                        ),
                        "stats_badges": self._stats_badges(term.uri),
                    }
                    html = renderer.render(template, extra_vars)
                    term_output_path(self.output_layout, term.id).write_text(
                        html, encoding="utf-8"
                    )
                    written += 1
                except Exception as exc:
                    exc.add_note(f"While building term_id {term_id}")
                    raise
                p.advance(1)

        return written
