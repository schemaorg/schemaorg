from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable, Iterator
import logging
from pathlib import Path
from typing import Any

from schemaorg.collaborators import Collaborator, CollaboratorRegistry
from schemaorg.graph_loader import GraphLoader
from schemaorg.layout import Issues, Releases
from schemaorg.model import VocabularyLoader
from schemaorg.renderers import CountsRenderer
from schemaorg.term_view import TermKind, TermView, TermViewCatalog
import util.fileutils as fileutils
import util.jinja_render as jinja_render
import util.paths as paths
import util.pretty_logger as pretty_logger
import util.schema as schema

log: logging.Logger = logging.getLogger(__name__)


def _default_catalog() -> TermViewCatalog:
    input_layout = paths.DefaultInputLayout()
    releases = Releases(input_layout, schema.VERSION)
    rel_ttl = releases.file(schema.target_version())
    ttl_files = (
        [rel_ttl]
        if rel_ttl.is_file()
        else Issues(input_layout).get_ttl_files()
    )
    graph = GraphLoader.load(ttl_files)
    vocab = VocabularyLoader(graph, version=schema.target_version()).load()
    collaborators = CollaboratorRegistry.from_layout(input_layout, vocab)
    return TermViewCatalog.from_graph(graph, vocab, collaborators)


def docsTemplateRender(
    template: str, extra_vars: dict[str, Any] | None = None
) -> str:
    tvars: dict[str, Any] = {
        "BUILDOPTS": schema.config.BUILDOPTS,
        "docsdir": schema.constants.DOCSDOCSDIR,
    }
    if extra_vars:
        tvars.update(extra_vars)
    return jinja_render.templateRender(template, tvars)


def schemasPage(_page: str = "", catalog: TermViewCatalog | None = None) -> str:
    cat = catalog or _default_catalog()
    counts = CountsRenderer(cat.vocab, schema.target_version()).counts
    extra_vars: dict[str, Any] = {
        "title": "Schemas",
        "termcounts": counts,
    }
    return docsTemplateRender("docs/Schemas.j2", extra_vars)


PAGE_CONFIGS: dict[str, tuple[str, str, str]] = {
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


def _issue_category(term: TermView) -> str:
    for source in term.sources:
        if "schemaorg/issue" in source:
            return f"issue-{Path(source).name}"
    return ""


def homePage(page: str, catalog: TermViewCatalog | None = None) -> str:
    title, template, filt = PAGE_CONFIGS.get(
        page, (schema.constants.SITENAME, "docs/Home.j2", "")
    )

    sectionterms: dict[str, dict[TermKind, list[TermView]]] = {}
    termcount = 0
    if filt:
        cat = catalog or _default_catalog()
        terms = cat.all_views(layer=filt)
        sectionterms, termcount = buildTermCatList(
            terms, group_by_issue=(filt == "pending")
        )

    extra_vars: dict[str, Any] = {
        "title": title,
        "termcount": termcount,
        "sectionterms": sectionterms,
    }
    return docsTemplateRender(template, extra_vars)


def buildTermCatList(
    terms: Iterable[TermView], group_by_issue: bool = False
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

    return {cat: dict(by_type) for cat, by_type in sorted(buckets.items())}, termcount


class UnknownTermError(LookupError):
    """Raised when there is no definition for a given term."""


class listingNode:
    def __init__(
        self,
        term: str,
        catalog: TermViewCatalog,
        title: str = "",
        visit_set: set[str] | None = None,
    ) -> None:
        termdesc = catalog.get(term)
        if not termdesc:
            raise UnknownTermError(f"No description for term {term}")
        visit_set = visit_set if visit_set is not None else set()
        self.repeat: bool = False
        self.subs: list[listingNode] = []
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
                        listingNode(child_id, catalog, visit_set=visit_set)
                    )
                except UnknownTermError as e:
                    log.warning(
                        "Error while building node %s for %s: %s",
                        child_id,
                        term,
                        e,
                    )
        else:
            self.repeat = True


def fullPage(page: str, catalog: TermViewCatalog | None = None) -> str:
    cat = catalog or _default_catalog()
    listings = [
        listingNode("Thing", cat, title="Types:"),
        listingNode("DataType", cat, title="DataTypes:"),
    ]
    extra_vars: dict[str, Any] = {
        "title": "Full schema hierarchy",
        "listings": listings,
    }
    return docsTemplateRender(f"docs/{page}.j2", extra_vars)


def fullReleasePage(
    _page: str = "", catalog: TermViewCatalog | None = None
) -> str:
    cat = catalog or _default_catalog()
    node_listings = [listingNode("Thing", cat, title="Type hierarchy")]

    type_uris = (*cat.vocab.enum_values, *cat.vocab.types)
    types = sorted(cat.views(type_uris), key=lambda t: t.id)
    properties = sorted(cat.views(cat.vocab.properties), key=lambda t: t.id)

    target = schema.target_version()
    extra_vars: dict[str, Any] = {
        "title": "Full Release Summary",
        "version": target.number(),
        "date": target.date() or "Unreleased",
        "listings": node_listings,
        "types": types,
        "properties": properties,
    }
    return docsTemplateRender("docs/FullRelease.j2", extra_vars)


def collabs(_page: str = "", catalog: TermViewCatalog | None = None) -> str:
    cat = catalog or _default_catalog()
    registry = cat.collaborators or CollaboratorRegistry.from_layout(
        paths.DefaultInputLayout(), cat.vocab
    )
    colls = sorted(registry.all(), key=lambda c: c.title or "")

    for coll in colls:
        createCollab(coll, cat, registry)

    extra_vars: dict[str, Any] = {
        "collaborators": colls,
        "title": "Collaborators",
    }
    return docsTemplateRender("docs/Collabs.j2", extra_vars)


def createCollab(
    coll: Collaborator,
    catalog: TermViewCatalog,
    registry: CollaboratorRegistry,
) -> None:
    terms: dict[str, dict[TermKind, list[TermView]]] = {}
    termcount = 0
    if coll.contributor:
        ack_views = catalog.views(registry.term_uris(coll.ref))
        terms, termcount = buildTermCatList(ack_views)

    extra_vars: dict[str, Any] = {
        "coll": coll,
        "title": coll.title,
        "contributor": coll.contributor,
        "terms": terms,
        "termcount": termcount,
    }

    content = docsTemplateRender("docs/Collab.j2", extra_vars)
    filename = paths.DefaultOutputLayout().file(
        paths.Domain.DOCS_COLLAB, f"{coll.ref}.html"
    )
    filename.write_text(content, encoding="utf-8")
    log.info("Created %s", filename)


_TERM_TAGS: dict[TermKind, str] = {
    TermKind.PROPERTY: " p",
    TermKind.TYPE: " t",
    TermKind.DATATYPE: " d",
    TermKind.ENUMERATION: " e",
    TermKind.ENUMERATIONVALUE: " v",
}


def generate_terms(
    tags: bool = False, catalog: TermViewCatalog | None = None
) -> Iterator[str]:
    cat = catalog or _default_catalog()
    for term in cat.all_views():
        label = _TERM_TAGS.get(term.termType, "") if tags else ""
        yield f"{term.id}{label}\n"


def termfind(_page: str = "", catalog: TermViewCatalog | None = None) -> str:
    if not schema.hasOpt("notermfinder"):
        log.info("Building term list")
        return "".join(generate_terms(tags=True, catalog=catalog))
    return ""


PAGELIST: dict[
    str,
    tuple[
        Callable[..., str],
        list[tuple[paths.Domain, str]],
    ],
] = {
    "Home": (homePage, [(paths.Domain.DOCS, "home.html")]),
    "PendingHome": (homePage, [(paths.Domain.DOCS, "pending.home.html")]),
    "AtticHome": (homePage, [(paths.Domain.DOCS, "attic.home.html")]),
    "AutoHome": (homePage, [(paths.Domain.DOCS, "auto.home.html")]),
    "BibHome": (homePage, [(paths.Domain.DOCS, "bib.home.html")]),
    "Health-lifesciHome": (
        homePage,
        [(paths.Domain.DOCS, "health-lifesci.home.html")],
    ),
    "MetaHome": (homePage, [(paths.Domain.DOCS, "meta.home.html")]),
    "Schemas": (schemasPage, [(paths.Domain.DOCS, "schemas.html")]),
    "Full": (fullPage, [(paths.Domain.DOCS, "full.html")]),
    "FullRelease": (
        fullReleasePage,
        [(paths.Domain.DOCS, "fullrelease.html")],
    ),
    "TermFind": (termfind, [(paths.Domain.DOCS_TERMFIND, "termlist.txt")]),
}


def buildDocs(
    pages: Iterable[str], catalog: TermViewCatalog | None = None
) -> None:
    page_list = list(pages)
    if not page_list:
        return
    process_pages = (
        sorted(PAGELIST)
        if any(fileutils.isAll(p) for p in page_list)
        else page_list
    )

    cat = catalog or _default_catalog()
    output_layout = paths.DefaultOutputLayout()

    for page in process_pages:
        if entry := PAGELIST.get(page):
            func, targets = entry
            with pretty_logger.BlockLog(
                logger=log, message=f"Generating page {page}"
            ):
                content = func(page, catalog=cat)
                for domain, filename in targets:
                    output_layout.file(domain, filename).write_text(
                        content, encoding="utf-8"
                    )
        else:
            log.warning("Unknown or missing page name: %s", page)
