"""Floating task that renders dynamic documentation pages and termfind index."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence
import logging
from pathlib import Path
from typing import Any

from schemaorg import constants
from schemaorg.layout import Domain, OutputLayout
from schemaorg.progress import ProgressReporter, TaskProgress
from schemaorg.renderers import CountsRenderer
from schemaorg.site_bundle import SiteBundle
from schemaorg.tasks.export_term_list import format_term_lines
from schemaorg.template_renderer import TemplateRenderer
from schemaorg.term_view import TermKind, TermView, TermViewCatalog

_PAGE_CONFIGS: dict[str, tuple[str, str, str]] = {
    "PendingHome": ("Pending", "docs/PendingHome.j2", "pending"),
    "AtticHome": ("Retired", "docs/AtticHome.j2", "attic"),
    "AutoHome": ("Automotive", "docs/AutoHome.j2", "auto"),
    "BibHome": ("Bib", "docs/BibHome.j2", "bib"),
    "Health-lifesciHome": (
        "Health-lifesci",
        "docs/Health-lifesciHome.j2",
        "health-lifesci",
    ),
    "MetaHome": ("Meta", "docs/MetaHome.j2", "meta"),
}

_PAGE_TARGETS: dict[str, tuple[tuple[Domain, str], ...]] = {
    "Home": ((Domain.DOCS, "home.html"),),
    "PendingHome": ((Domain.DOCS, "pending.home.html"),),
    "AtticHome": ((Domain.DOCS, "attic.home.html"),),
    "AutoHome": ((Domain.DOCS, "auto.home.html"),),
    "BibHome": ((Domain.DOCS, "bib.home.html"),),
    "Health-lifesciHome": ((Domain.DOCS, "health-lifesci.home.html"),),
    "MetaHome": ((Domain.DOCS, "meta.home.html"),),
    "Schemas": ((Domain.DOCS, "schemas.html"),),
    "Full": ((Domain.DOCS, "full.html"),),
    "FullRelease": ((Domain.DOCS, "fullrelease.html"),),
    "TermFind": ((Domain.DOCS_TERMFIND, "termlist.txt"),),
}


def _is_all(token: str) -> bool:
    return token.strip().upper() == "ALL"


def _issue_category(term: TermView) -> str:
    for source in term.sources:
        if "schemaorg/issue" in source:
            return f"issue-{Path(source).name}"
    return ""


def _build_term_cat_list(
    terms: Iterable[TermView], group_by_issue: bool
) -> tuple[dict[str, dict[TermKind, list[TermView]]], int]:
    buckets: dict[str, dict[TermKind, list[TermView]]] = defaultdict(
        lambda: defaultdict(list)
    )
    termcount = 0
    for term in sorted(terms, key=lambda t: t.id):
        if term.termType == TermKind.REFERENCE:
            continue
        cat = _issue_category(term) if group_by_issue else ""
        buckets[cat][term.termType].append(term)
        termcount += 1
    return {
        cat: dict(by_type) for cat, by_type in sorted(buckets.items())
    }, termcount


class UnknownTermError(LookupError):
    """Raised when there is no definition for a given term."""


class ListingNode:
    """Tree node representing a class, datatype, or enumeration in hierarchy pages."""

    def __init__(
        self,
        term: str,
        catalog: TermViewCatalog,
        title: str,
        visit_set: set[str],
        progress: TaskProgress,
    ) -> None:
        termdesc = catalog.get(term)
        if not termdesc:
            raise UnknownTermError(f"No description for term {term}")
        self.repeat: bool = False
        self.subs: list[ListingNode] = []
        self.title: str = title
        self.id: str = termdesc.label
        self.termType: TermKind = termdesc.termType
        self.retired: bool = termdesc.retired
        self.pending: bool = termdesc.pending

        if self.id not in visit_set:
            visit_set.add(self.id)
            child_ids: list[str] = []
            if termdesc.termType == TermKind.ENUMERATION:
                child_ids.extend(sorted(termdesc.enumerationMembers.ids))
            child_ids.extend(sorted(termdesc.subs.ids))

            for child_id in child_ids:
                try:
                    self.subs.append(
                        ListingNode(
                            child_id, catalog, "", visit_set, progress
                        )
                    )
                except UnknownTermError as exc:
                    progress.log(
                        f"Error while building node {child_id} for {term}: {exc}",
                        logging.WARNING,
                    )
        else:
            self.repeat = True


class RenderDocsPagesTask:
    """Renders dynamic documentation HTML pages and termlist.txt from a SiteBundle."""

    def __init__(
        self,
        bundle: SiteBundle,
        output_layout: OutputLayout,
        build_opts: Sequence[str],
        page_names: Sequence[str],
        progress: ProgressReporter,
    ) -> None:
        self.bundle: SiteBundle = bundle
        self.output_layout: OutputLayout = output_layout
        self.build_opts: tuple[str, ...] = tuple(build_opts)
        self.page_names: tuple[str, ...] = tuple(page_names)
        self.progress: ProgressReporter = progress

    def _render_page(
        self,
        page: str,
        renderer: TemplateRenderer,
        progress: TaskProgress,
    ) -> str:
        cat = self.bundle.catalog
        target = self.bundle.target_version

        if page == "Schemas":
            counts = CountsRenderer(cat.vocab, target).counts
            return renderer.render(
                "docs/Schemas.j2",
                {"title": "Schemas", "termcounts": counts},
            )
        if page == "Full":
            listings = [
                ListingNode("Thing", cat, "Types:", set(), progress),
                ListingNode("DataType", cat, "DataTypes:", set(), progress),
            ]
            return renderer.render(
                f"docs/{page}.j2",
                {"title": "Full schema hierarchy", "listings": listings},
            )
        if page == "FullRelease":
            node_listings = [
                ListingNode("Thing", cat, "Type hierarchy", set(), progress)
            ]
            type_uris = (*cat.vocab.enum_values, *cat.vocab.types)
            types = sorted(cat.views(type_uris), key=lambda t: t.id)
            properties = sorted(
                cat.views(cat.vocab.properties), key=lambda t: t.id
            )
            extra_vars: dict[str, Any] = {
                "title": "Full Release Summary",
                "version": target.number(),
                "date": target.date() or "Unreleased",
                "listings": node_listings,
                "types": types,
                "properties": properties,
            }
            return renderer.render("docs/FullRelease.j2", extra_vars)
        if page == "TermFind":
            if "notermfinder" in self.build_opts:
                return ""
            return "".join(format_term_lines(cat, include_tags=True))

        title, template, filt = _PAGE_CONFIGS.get(
            page, (constants.SITENAME, "docs/Home.j2", "")
        )
        sectionterms: dict[str, dict[TermKind, list[TermView]]] = {}
        termcount = 0
        if filt:
            sectionterms, termcount = _build_term_cat_list(
                cat.all_views(layer=filt),
                group_by_issue=(filt == "pending"),
            )
        return renderer.render(
            template,
            {
                "title": title,
                "termcount": termcount,
                "sectionterms": sectionterms,
            },
        )

    def run(self) -> int:
        if not self.page_names:
            return 0
        requested = (
            sorted(_PAGE_TARGETS)
            if any(_is_all(p) for p in self.page_names)
            else list(self.page_names)
        )

        renderer = TemplateRenderer(
            self.bundle.input_layout,
            self.bundle.target_version,
            self.build_opts,
        )

        written = 0
        with self.progress.task(
            "Rendering documentation pages",
            total=len(requested),
            unit="pages",
        ) as p:
            for page in requested:
                targets = _PAGE_TARGETS.get(page)
                if targets is None:
                    p.log(
                        f"Unknown or missing page name: {page}",
                        logging.WARNING,
                    )
                    p.advance(1)
                    continue
                p.step(page)
                content = self._render_page(page, renderer, p)
                for domain, filename in targets:
                    self.output_layout.file(domain, filename).write_text(
                        content, encoding="utf-8"
                    )
                written += 1
                p.advance(1)

        return written
