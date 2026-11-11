from __future__ import annotations

from collections import defaultdict
from collections.abc import Callable, Iterable, Iterator
import json
import logging
from pathlib import Path
from typing import Any

from schemaorg.layout import Releases
from schemaorg.sdo_uri import SCHEMA_URL
import SchemaTerms.sdocollaborators as sdocollaborators
import SchemaTerms.sdoterm as sdoterm
import SchemaTerms.sdotermsource as sdotermsource
import util.fileutils as fileutils
import util.jinja_render as jinja_render
import util.paths as paths
import util.pretty_logger as pretty_logger
import util.schema as schema
from util.sort_dict import sort_dict
import util.textutils as textutils

log: logging.Logger = logging.getLogger(__name__)


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


def schemasPage(_page: str = "") -> str:
    extra_vars: dict[str, Any] = {
        "title": "Schemas",
        "termcounts": sdotermsource.SdoTermSource.termCounts(),
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


def _issue_category(term: sdoterm.SdoTerm) -> str:
    for source in term.sources:
        if "schemaorg/issue" in source:
            return f"issue-{Path(source).name}"
    return ""


def homePage(page: str) -> str:
    title, template, filt = PAGE_CONFIGS.get(
        page, (schema.constants.SITENAME, "docs/Home.j2", "")
    )

    sectionterms: dict[str, dict[sdoterm.SdoTermType, list[sdoterm.SdoTerm]]] = {}
    termcount = 0
    if filt:
        all_terms = sdotermsource.SdoTermSource.getAllTerms(
            layer=filt, expanded=True
        )
        terms = [t for t in all_terms if isinstance(t, sdoterm.SdoTerm)]
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
    terms: Iterable[sdoterm.SdoTerm], group_by_issue: bool = False
) -> tuple[dict[str, dict[sdoterm.SdoTermType, list[sdoterm.SdoTerm]]], int]:
    buckets: dict[str, dict[sdoterm.SdoTermType, list[sdoterm.SdoTerm]]] = (
        defaultdict(lambda: defaultdict(list))
    )
    termcount = 0
    for term in sorted(terms, key=lambda t: t.id):
        if term.termType == sdoterm.SdoTermType.REFERENCE:
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
        title: str = "",
        visit_set: set[str] | None = None,
    ) -> None:
        termdesc = sdotermsource.SdoTermSource.getTerm(term)
        if not termdesc:
            raise UnknownTermError(f"No description for term {term}")
        visit_set = visit_set if visit_set is not None else set()
        self.repeat: bool = False
        self.subs: list[listingNode] = []
        self.title: str = title
        self.id: str = termdesc.label
        self.termType: sdoterm.SdoTermType = termdesc.termType
        self.retired: bool = termdesc.retired
        self.pending: bool = termdesc.pending

        if self.id not in visit_set:
            visit_set.add(self.id)
            child_ids: list[str] = []
            if termdesc.termType == sdoterm.SdoTermType.ENUMERATION:
                assert isinstance(termdesc, sdoterm.SdoEnumeration)
                child_ids.extend(sorted(termdesc.enumerationMembers.ids))
            child_ids.extend(sorted(termdesc.subs.ids))

            for child_id in child_ids:
                try:
                    self.subs.append(listingNode(child_id, visit_set=visit_set))
                except UnknownTermError as e:
                    log.warning("Error while building node %s for %s: %s", child_id, term, e)
        else:
            self.repeat = True


def jsonldtree(page: str | None = None) -> str:
    del page
    context: dict[str, Any] = {
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        # Legacy output: no trailing slash.
        "schema": SCHEMA_URL._replace(path="").geturl(),
        "rdfs:subClassOf": {"@type": "@id"},
        "description": "rdfs:comment",
        "children": {"@reverse": "rdfs:subClassOf"},
    }
    data = _jsonldtree("Thing", visitset=set(), term={"@context": context})
    return json.dumps(sort_dict(data), indent=3)


def _jsonldtree(
    tid: str, visitset: set[str], term: dict[str, Any] | None = None
) -> dict[str, Any]:
    try:
        termdesc = sdotermsource.SdoTermSource.getTerm(tid)
        if not termdesc:
            raise UnknownTermError(f"No description for term {tid}")

        term_dict: dict[str, Any] = term if term is not None else {}
        term_dict.update(
            {
                "@type": "rdfs:Class",
                "@id": f"schema:{termdesc.id}",
                "name": termdesc.label,
                "description": textutils.ShortenOnSentence(
                    textutils.StripHtmlTags(termdesc.comment)
                ),
            }
        )

        if termdesc.supers:
            sups = [f"schema:{sup}" for sup in termdesc.supers.ids]
            term_dict["rdfs:subClassOf"] = sups[0] if len(sups) == 1 else sups

        if termdesc.pending:
            term_dict["pending"] = True
        if termdesc.retired:
            term_dict["attic"] = True

        if tid not in visitset:
            visitset.add(tid)
            if termdesc.subs:
                subs: list[dict[str, Any]] = []
                for sub in termdesc.subs.ids:
                    try:
                        subs.append(_jsonldtree(tid=sub, visitset=visitset))
                    except UnknownTermError as e:
                        log.warning("Error while building listing node for %s: %s", sub, e)
                term_dict["children"] = subs
        return term_dict
    except Exception as e:
        e.add_note(f"while building JSON tree for id:{tid}-{term}")
        raise


listings: list[listingNode] | None = None


def fullPage(page: str) -> str:
    global listings
    if listings is None:
        listings = [
            listingNode("Thing", title="Types:"),
            listingNode("DataType", title="DataTypes:"),
        ]
    extra_vars: dict[str, Any] = {
        "title": "Full schema hierarchy",
        "listings": listings,
    }
    return docsTemplateRender(f"docs/{page}.j2", extra_vars)


def fullReleasePage(_page: str = "") -> str:
    node_listings = [listingNode("Thing", title="Type hierarchy")]

    all_enum_vals = sdotermsource.SdoTermSource.getAllEnumerationvalues(expanded=True)
    all_types = sdotermsource.SdoTermSource.getAllTypes(expanded=True)

    types = [
        t for t in (*all_enum_vals, *all_types) if isinstance(t, sdoterm.SdoTerm)
    ]
    types = sorted(
        sdotermsource.SdoTermSource.expandTerms(types), key=lambda t: t.id
    )

    all_props = sdotermsource.SdoTermSource.getAllProperties(expanded=True)
    properties = sorted(
        sdotermsource.SdoTermSource.expandTerms(
            [p for p in all_props if isinstance(p, sdoterm.SdoTerm)], depth=1
        ),
        key=lambda t: t.id,
    )

    current = schema.VERSION.current()
    extra_vars: dict[str, Any] = {
        "title": "Full Release Summary",
        "version": current.number(),
        "date": current.date(),
        "listings": node_listings,
        "types": types,
        "properties": properties,
    }
    return docsTemplateRender("docs/FullRelease.j2", extra_vars)


def collabs(_page: str = "") -> str:
    colls = sorted(
        sdocollaborators.collaborator.collaborators(), key=lambda t: t.title or ""
    )

    for coll in colls:
        createCollab(coll)

    extra_vars: dict[str, Any] = {"collaborators": colls, "title": "Collaborators"}
    return docsTemplateRender("docs/Collabs.j2", extra_vars)


def createCollab(coll: sdocollaborators.collaborator) -> None:
    terms: dict[str, dict[sdoterm.SdoTermType, list[sdoterm.SdoTerm]]] = {}
    termcount = 0
    if coll.contributor:
        terms, termcount = buildTermCatList(coll.getTerms())

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


_TERM_TAGS: dict[sdoterm.SdoTermType, str] = {
    sdoterm.SdoTermType.PROPERTY: " p",
    sdoterm.SdoTermType.TYPE: " t",
    sdoterm.SdoTermType.DATATYPE: " d",
    sdoterm.SdoTermType.ENUMERATION: " e",
    sdoterm.SdoTermType.ENUMERATIONVALUE: " v",
}


def generate_terms(tags: bool = False) -> Iterator[str]:
    for term in sdotermsource.SdoTermSource.getAllTerms(expanded=True):
        if not isinstance(term, sdoterm.SdoTerm):
            continue
        label = _TERM_TAGS.get(term.termType, "") if tags else ""
        yield f"{term.id}{label}\n"


def termfind(_page: str = "") -> str:
    if not schema.hasOpt("notermfinder"):
        log.info("Building term list")
        return "".join(generate_terms(tags=True))
    return ""


PAGELIST: dict[str, tuple[Callable[[str], str], list[tuple[paths.Domain, str]]]] = {
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
    "FullOrig": (fullPage, [(paths.Domain.DOCS, "full.orig.html")]),
    "FullRelease": (
        fullReleasePage,
        [
            (paths.Domain.DOCS, "fullrelease.html"),
            (paths.Domain.RELEASE, "schema-all.html"),
        ],
    ),
    "TermFind": (termfind, [(paths.Domain.DOCS_TERMFIND, "termlist.txt")]),
}


def buildDocs(pages: Iterable[str]) -> None:
    page_list = list(pages)
    process_pages = (
        sorted(PAGELIST)
        if any(fileutils.isAll(p) for p in page_list)
        else page_list
    )

    output_layout = paths.DefaultOutputLayout()
    releases = Releases(output_layout, schema.VERSION)

    for page in process_pages:
        if entry := PAGELIST.get(page):
            func, targets = entry
            with pretty_logger.BlockLog(
                logger=log, message=f"Generating page {page}"
            ):
                content = func(page)
                for domain, filename in targets:
                    if domain == paths.Domain.RELEASE:
                        out_path = releases.file(filename=filename)
                    else:
                        out_path = output_layout.file(domain, filename)
                    out_path.write_text(content, encoding="utf-8")
        else:
            log.warning("Unknown or missing page name: %s", page)
