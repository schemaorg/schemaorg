"""Floating task that renders dynamic documentation pages and termfind index."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
import logging
from pathlib import Path
from typing import Any

from schemaorg import constants
from schemaorg.layout import Domain, OutputLayout
from schemaorg.progress import ProgressReporter
from schemaorg.renderers import CountsRenderer
from schemaorg.site_bundle import SiteBundle
from schemaorg.tasks.export_term_list import format_term_lines
from schemaorg.template_renderer import TemplateRenderer
from schemaorg.term_view import TermKind, TermView, TermViewCatalog

_PAGE_CONFIGS: dict[str, tuple[str, str]] = {
    "Home": (constants.SITENAME, ""),
    "PendingHome": ("Pending", "pending"),
    "AtticHome": ("Retired", "attic"),
    "AutoHome": ("Automotive", "auto"),
    "BibHome": ("Bib", "bib"),
    "Health-lifesciHome": ("Health-lifesci", "health-lifesci"),
    "MetaHome": ("Meta", "meta"),
}

_PAGE_TARGETS: dict[str, tuple[Domain, str]] = {
    "Home": (Domain.DOCS, "home.html"),
    "PendingHome": (Domain.DOCS, "pending.home.html"),
    "AtticHome": (Domain.DOCS, "attic.home.html"),
    "AutoHome": (Domain.DOCS, "auto.home.html"),
    "BibHome": (Domain.DOCS, "bib.home.html"),
    "Health-lifesciHome": (Domain.DOCS, "health-lifesci.home.html"),
    "MetaHome": (Domain.DOCS, "meta.home.html"),
    "Schemas": (Domain.DOCS, "schemas.html"),
    "Full": (Domain.DOCS, "full.html"),
    "FullRelease": (Domain.DOCS, "fullrelease.html"),
    "TermFind": (Domain.DOCS_TERMFIND, "termlist.txt"),
}


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
        cat = _issue_category(term) if group_by_issue else ""
        buckets[cat][term.termType].append(term)
        termcount += 1
    return {
        cat: dict(by_type) for cat, by_type in sorted(buckets.items())
    }, termcount


@dataclass
class ListingNode:
    """Tree node representing a class, datatype, or enumeration in hierarchy pages."""

    id: str
    termType: TermKind
    retired: bool
    pending: bool
    title: str = ""
    repeat: bool = False
    subs: list[ListingNode] = field(default_factory=list)

    @classmethod
    def from_term(
        cls, term: TermView, title: str, visit_set: set[str]
    ) -> ListingNode:
        node = cls(
            id=term.label,
            termType=term.termType,
            retired=term.retired,
            pending=term.pending,
            title=title,
        )
        if node.id in visit_set:
            node.repeat = True
            return node
        visit_set.add(node.id)
        children: list[TermView] = []
        if term.termType == TermKind.ENUMERATION:
            children.extend(sorted(term.enumerationMembers, key=lambda t: t.id))
        children.extend(sorted(term.subs, key=lambda t: t.id))
        node.subs = [cls.from_term(child, "", visit_set) for child in children]
        return node


def _build_listing(
    cat: TermViewCatalog, root_id: str, title: str
) -> ListingNode:
    term = cat.get(root_id)
    if term is None:
        raise LookupError(f"No description for term {root_id}")
    return ListingNode.from_term(term, title, set())


@dataclass(frozen=True)
class RenderDocsPagesTask:
    """Renders dynamic documentation HTML pages and termlist.txt from a SiteBundle."""

    bundle: SiteBundle
    output_layout: OutputLayout
    build_opts: Sequence[str]
    page_names: Sequence[str]
    progress: ProgressReporter

    def _render_page(self, page: str, renderer: TemplateRenderer) -> str:
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
                _build_listing(cat, "Thing", "Types:"),
                _build_listing(cat, "DataType", "DataTypes:"),
            ]
            return renderer.render(
                "docs/Full.j2",
                {"title": "Full schema hierarchy", "listings": listings},
            )
        if page == "FullRelease":
            node_listings = [_build_listing(cat, "Thing", "Type hierarchy")]
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

        title, filt = _PAGE_CONFIGS[page]
        sectionterms: dict[str, dict[TermKind, list[TermView]]] = {}
        termcount = 0
        if filt:
            sectionterms, termcount = _build_term_cat_list(
                cat.all_views(layer=filt),
                group_by_issue=(filt == "pending"),
            )
        return renderer.render(
            f"docs/{page}.j2",
            {
                "title": title,
                "termcount": termcount,
                "sectionterms": sectionterms,
            },
        )

    def run(self) -> int:
        if not any(self.page_names):
            return 0
        requested = (
            sorted(_PAGE_TARGETS)
            if any(p.strip().upper() == "ALL" for p in self.page_names)
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
                target = _PAGE_TARGETS.get(page)
                if target is None:
                    p.log(
                        f"Unknown or missing page name: {page}",
                        logging.WARNING,
                    )
                    p.advance(1)
                    continue
                p.step(page)
                domain, filename = target
                content = self._render_page(page, renderer)
                self.output_layout.file(domain, filename).write_text(
                    content, encoding="utf-8"
                )
                written += 1
                p.advance(1)

        return written
