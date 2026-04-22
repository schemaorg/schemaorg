#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import standard python libraries

import json
import logging
import sys
from pathlib import Path
from collections import defaultdict
from typing import Any, Dict, List, Optional, Tuple, Union, Iterable, Set, Callable, Sequence

if Path.cwd() not in [Path(p).resolve() for p in sys.path]:
    sys.path.insert(1, str(Path.cwd()))

import software.scripts.buildtermlist as buildtermlist
import software.util.fileutils as fileutils
import software.util.jinga_render as jinga_render
import software.util.pretty_logger as pretty_logger
import software.util.schemaglobals as schemaglobals
import software.util.schemaversion as schemaversion
import software.util.textutils as textutils
from software.util.sort_dict import sort_dict

import software.SchemaTerms.sdotermsource as sdotermsource
import software.SchemaTerms.sdocollaborators as sdocollaborators
import software.SchemaTerms.sdoterm as sdoterm

log: logging.Logger = logging.getLogger(__name__)

STRCLASSVAL: Optional[str] = None

def docsTemplateRender(template: str, extra_vars: Optional[Dict[str, Any]] = None) -> str:
    tvars: Dict[str, Any] = {"BUILDOPTS": schemaglobals.BUILDOPTS, "docsdir": schemaglobals.DOCSDOCSDIR}
    if extra_vars:
        tvars.update(extra_vars)
    return jinga_render.templateRender(template, tvars)


def schemasPage(page: str) -> str:
    extra_vars: Dict[str, Any] = {
        "home_page": "False",
        "title": "Schemas",
        "termcounts": sdotermsource.SdoTermSource.termCounts(),
    }
    return docsTemplateRender("docs/Schemas.j2", extra_vars)


PAGE_CONFIGS: Dict[str, Tuple[str, str, str, str]] = {
    "PendingHome": ("Pending", "docs/PendingHome.j2", "pending", 'class="ext ext-pending"'),
    "AtticHome": ("Retired", "docs/AtticHome.j2", "attic", 'class="ext ext-attic"'),
    "AutoHome": ("Autotomotives", "docs/AutoHome.j2", "auto", 'class="ext"'),
    "BibHome": ("Bib", "docs/BibHome.j2", "bib", 'class="ext"'),
    "Health-lifesciHome": ("Health-lifesci", "docs/Health-lifesciHome.j2", "health-lifesci", 'class="ext"'),
    "MetaHome": ("Meta", "docs/MetaHome.j2", "meta", 'class="ext"'),
}

def homePage(page: str) -> str:
    global STRCLASSVAL
    title: str = schemaglobals.SITENAME
    template: str = "docs/Home.j2"
    filt: Optional[str] = None
    overrideclassval: Optional[str] = None

    config: Optional[Tuple[str, str, str, str]] = PAGE_CONFIGS.get(page)
    if config:
        title, template, filt, overrideclassval = config

    sectionterms: Dict[str, Dict[sdoterm.SdoTermType, List[sdoterm.SdoTerm]]] = {}
    termcount: int = 0
    if filt:
        all_terms: Sequence[Union[str, sdoterm.SdoTerm]] = sdotermsource.SdoTermSource.getAllTerms(layer=filt, expanded=True)
        terms: List[sdoterm.SdoTerm] = []
        t: Union[str, sdoterm.SdoTerm]
        for t in all_terms:
            if isinstance(t, sdoterm.SdoTerm):
                t.cat = ""  # type: ignore
                if filt == "pending":
                    s: str
                    for s in t.sources:
                        if "schemaorg/issue" in s:
                            t.cat = f"issue-{Path(s).name}"  # type: ignore
                            break
                terms.append(t)
        terms.sort(key=lambda u: (getattr(u, 'cat', ''), u.id))
        sectionterms, termcount = buildTermCatList(terms, checkCat=True)

    extra_vars: Dict[str, Any] = {
        "home_page": "True",
        "title": title,
        "termcount": termcount,
        "sectionterms": sectionterms,
    }
    STRCLASSVAL = overrideclassval
    ret: str = docsTemplateRender(template, extra_vars)
    STRCLASSVAL = None
    return ret


def buildTermCatList(terms: Iterable[sdoterm.SdoTerm], checkCat: bool = False) -> Tuple[Dict[str, Dict[sdoterm.SdoTermType, List[sdoterm.SdoTerm]]], int]:
    termcat: Dict[str, Dict[sdoterm.SdoTermType, List[sdoterm.SdoTerm]]] = defaultdict(lambda: defaultdict(list))
    termcount: int = 0
    t: sdoterm.SdoTerm
    for t in terms:
        if t.termType == sdoterm.SdoTermType.REFERENCE:
            continue
        cat: str = getattr(t, 'cat', '') if checkCat else ""
        termcat[cat][t.termType].append(t)
        termcount += 1

    return dict(sorted(termcat.items())), termcount


class UnknownTermError(LookupError):
    """Raised when there is no definition for a given term."""


class listingNode:
    def __init__(self, term: str, depth: int = 0, title: str = "", parent: Optional["listingNode"] = None, visit_set: Optional[Set[str]] = None) -> None:
        termdesc: Optional[sdoterm.SdoTerm] = sdotermsource.SdoTermSource.getTerm(term)
        if not termdesc:
            raise UnknownTermError(f"No description for term {term}")
        visit_set = visit_set if visit_set is not None else set()
        self.repeat: bool = False
        self.subs: List[listingNode] = []
        self.parent: Optional[listingNode] = parent
        self.title: str = title
        self.id: str = termdesc.label
        self.termType: sdoterm.SdoTermType = termdesc.termType
        self.depth: int = depth
        self.retired: bool = termdesc.retired
        self.pending: bool = termdesc.pending

        if self.id not in visit_set:
            visit_set.add(self.id)
            child_ids: List[str] = []
            if termdesc.termType == sdoterm.SdoTermType.ENUMERATION:
                child_ids.extend(sorted(termdesc.enumerationMembers.ids))
            child_ids.extend(sorted(termdesc.subs.ids))

            child_id: str
            for child_id in child_ids:
                try:
                    self.subs.append(listingNode(child_id, depth=depth + 1, parent=self, visit_set=visit_set))
                except UnknownTermError as e:
                    log.warning(f"Error while building node {child_id} for {term}: {e}")
        else:
            self.repeat = True


def jsonldtree(page: str) -> str:
    context: Dict[str, Any] = {
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "schema": "https://schema.org",
        "rdfs:subClassOf": {"@type": "@id"},
        "description": "rdfs:comment",
        "children": {"@reverse": "rdfs:subClassOf"}
    }
    data: Dict[str, Any] = _jsonldtree("Thing", visitset=set(), term={"@context": context})
    return json.dumps(sort_dict(data), indent=2)


def _jsonldtree(tid: str, visitset: Set[str], term: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    try:
        termdesc: Optional[sdoterm.SdoTerm] = sdotermsource.SdoTermSource.getTerm(tid)
        if not termdesc:
            raise UnknownTermError(f"No description for term {tid}")

        term_dict: Dict[str, Any] = term if term is not None else {}
        term_dict.update({
            "@type": "rdfs:Class",
            "@id": f"schema:{termdesc.id}",
            "name": termdesc.label,
            "description": textutils.ShortenOnSentence(textutils.StripHtmlTags(termdesc.comment))
        })

        if termdesc.supers:
            sups: List[str] = [f"schema:{sup}" for sup in termdesc.supers.ids]
            term_dict["rdfs:subClassOf"] = sups[0] if len(sups) == 1 else sups

        if termdesc.pending:
            term_dict["pending"] = True
        if termdesc.retired:
            term_dict["attic"] = True

        if tid not in visitset:
            visitset.add(tid)
            if termdesc.subs:
                subs: List[Dict[str, Any]] = []
                sub: str
                for sub in termdesc.subs.ids:
                    try:
                        subs.append(_jsonldtree(tid=sub, visitset=visitset))
                    except UnknownTermError as e:
                        log.warning(f"Error while building listing node for {sub}: {e}")
                term_dict["children"] = subs
        return term_dict
    except Exception as e:
        e.add_note(f"while building JSON tree for id:{tid}-{term}")
        raise


listings: Optional[List[listingNode]] = None


def fullPage(page: str) -> str:
    global listings
    if not listings:
        listings = [
            listingNode("Thing", title="Types:"),
            listingNode("DataType", title="DataTypes:")
        ]
    extra_vars: Dict[str, Any] = {
        "home_page": "False",
        "title": "Full schema hierarchy",
        "listings": listings,
    }

    return docsTemplateRender(f"docs/{page}.j2", extra_vars)


def fullReleasePage(page: str) -> str:
    node_listings: List[listingNode] = [listingNode("Thing", title="Type hierarchy")]

    all_enum_vals: Sequence[Union[str, sdoterm.SdoTerm]] = sdotermsource.SdoTermSource.getAllEnumerationvalues(expanded=True)
    all_types: Sequence[Union[str, sdoterm.SdoTerm]] = sdotermsource.SdoTermSource.getAllTypes(expanded=True)

    types: List[sdoterm.SdoTerm] = [t for t in list(all_enum_vals) + list(all_types) if isinstance(t, sdoterm.SdoTerm)]
    types = sorted(sdotermsource.SdoTermSource.expandTerms(types), key=lambda t: t.id)

    all_props: Sequence[Union[str, sdoterm.SdoTerm]] = sdotermsource.SdoTermSource.getAllProperties(expanded=True)
    properties: List[sdoterm.SdoTerm] = [p for p in all_props if isinstance(p, sdoterm.SdoTerm)]

    extra_vars: Dict[str, Any] = {
        "home_page": "False",
        "title": "Full Release Summary",
        "version": schemaversion.getVersion(),
        "date": schemaversion.getCurrentVersionDate(),
        "listings": node_listings,
        "types": types,
        "properties": sorted(properties, key=lambda t: t.id),
    }
    return docsTemplateRender("docs/FullRelease.j2", extra_vars)


def collabs(page: str) -> str:
    colls: List[sdocollaborators.collaborator] = sorted(sdocollaborators.collaborator.collaborators(), key=lambda t: t.title or "")

    coll: sdocollaborators.collaborator
    for coll in colls:
        createCollab(coll)

    extra_vars: Dict[str, Any] = {"collaborators": colls, "title": "Collaborators"}
    return docsTemplateRender("docs/Collabs.j2", extra_vars)


def createCollab(coll: sdocollaborators.collaborator) -> None:
    terms: Dict[str, Dict[sdoterm.SdoTermType, List[sdoterm.SdoTerm]]] = {}
    termcount: int = 0
    if coll.contributor:
        terms, termcount = buildTermCatList(coll.getTerms())

    extra_vars: Dict[str, Any] = {
        "coll": coll,
        "title": coll.title,
        "contributor": coll.contributor,
        "terms": terms,
        "termcount": termcount,
    }

    content: str = docsTemplateRender("docs/Collab.j2", extra_vars)
    filename: str = fileutils.ensureAbsolutePath(
        output_dir=schemaglobals.OUTPUTDIR,
        relative_path=str(Path("docs/collab") / f"{coll.ref}.html"),
    )
    Path(filename).write_text(content, encoding="utf8")
    log.info(f"Created {filename}")


def termfind(file: str) -> str:
    if not schemaglobals.hasOpt("notermfinder"):
        log.info("Building term list")
        return "".join(buildtermlist.generateTerms(tags=True))
    return ""


PAGELIST: Dict[str, Tuple[Callable[[str], str], List[str]]] = {
    "Home": (homePage, ["docs/home.html"]),
    "PendingHome": (homePage, ["docs/pending.home.html"]),
    "AtticHome": (homePage, ["docs/attic.home.html"]),
    "AutoHome": (homePage, ["docs/auto.home.html"]),
    "BibHome": (homePage, ["docs/bib.home.html"]),
    "Health-lifesciHome": (homePage, ["docs/health-lifesci.home.html"]),
    "MetaHome": (homePage, ["docs/meta.home.html"]),
    "Schemas": (schemasPage, ["docs/schemas.html"]),
    "Full": (fullPage, ["docs/full.html"]),
    "FullOrig": (fullPage, ["docs/full.orig.html"]),
    "FullRelease": (
        fullReleasePage,
        [
            "docs/fullrelease.html",
            f"releases/{schemaversion.getVersion()}/schema-all.html",
        ],
    ),
    "TermFind": (termfind, ["docs/termfind/termlist.txt"]),
    "Tree": (jsonldtree, ["docs/tree.jsonld"]),
}


def buildDocs(pages: Iterable[str]) -> None:
    process_pages: List[str] = sorted(PAGELIST.keys()) if any(fileutils.isAll(p) for p in pages) else list(pages)

    page: str
    for page in process_pages:
        if entry := PAGELIST.get(page):
            func: Callable[[str], str]
            filenames: List[str]
            func, filenames = entry
            with pretty_logger.BlockLog(logger=log, message=f"Generating page {page}"):
                content: str = func(page)
                relative_path: str
                for relative_path in filenames:
                    filename: str = fileutils.ensureAbsolutePath(
                        output_dir=schemaglobals.OUTPUTDIR, relative_path=relative_path
                    )
                    Path(filename).write_text(content, encoding="utf8")
        else:
            log.warning(f"Unknown or missing page name: {page}")
