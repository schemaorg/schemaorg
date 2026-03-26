#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import standard python libraries

import json
import logging
import os
import sys
import typing
from typing import Any, Dict, List, Optional, Tuple, Union, Iterable, Sequence, Set, Callable

# Import schema.org libraries
if os.getcwd() not in sys.path:
    sys.path.insert(1, os.getcwd())

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


def homePage(page: str) -> str:
    global STRCLASSVAL
    title: str = schemaglobals.SITENAME
    template: str = "docs/Home.j2"
    filt: Optional[str] = None
    overrideclassval: Optional[str] = None
    if page == "PendingHome":
        title = "Pending"
        template = "docs/PendingHome.j2"
        filt = "pending"
        overrideclassval = 'class="ext ext-pending"'
    elif page == "AtticHome":
        title = "Retired"
        template = "docs/AtticHome.j2"
        filt = "attic"
        overrideclassval = 'class="ext ext-attic"'
    elif page == "AutoHome":
        title = "Autotomotives"
        template = "docs/AutoHome.j2"
        filt = "auto"
        overrideclassval = 'class="ext"'
    elif page == "BibHome":
        title = "Bib"
        template = "docs/BibHome.j2"
        filt = "bib"
        overrideclassval = 'class="ext"'
    elif page == "Health-lifesciHome":
        title = "Health-lifesci"
        template = "docs/Health-lifesciHome.j2"
        filt = "health-lifesci"
        overrideclassval = 'class="ext"'
    elif page == "MetaHome":
        title = "Meta"
        template = "docs/MetaHome.j2"
        filt = "meta"
        overrideclassval = 'class="ext"'
    
    sectionterms: Dict[str, Dict[sdoterm.SdoTermType, List[sdoterm.SdoTerm]]] = {}
    termcount: int = 0
    if filt:
        all_terms = sdotermsource.SdoTermSource.getAllTerms(layer=filt, expanded=True)
        terms: List[sdoterm.SdoTerm] = []
        for t in all_terms:
            if isinstance(t, sdoterm.SdoTerm):
                t.cat = ""
                if filt == "pending":
                    for s in t.sources:
                        if "schemaorg/issue" in s:
                            t.cat = "issue-" + os.path.basename(s)
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
    first: bool = True
    cat: Optional[str] = None
    termcat: Dict[str, Dict[sdoterm.SdoTermType, List[sdoterm.SdoTerm]]] = {}
    termcount: int = 0
    ttypes: Dict[sdoterm.SdoTermType, List[sdoterm.SdoTerm]] = {}
    for t in terms:
        if checkCat:
            tcat: str = getattr(t, 'cat', '')
        else:
            tcat = ""
        if first or tcat != cat:
            first = False
            cat = tcat
            ttypes = {}
            termcat[cat] = ttypes
            ttypes[sdoterm.SdoTermType.TYPE] = []
            ttypes[sdoterm.SdoTermType.PROPERTY] = []
            ttypes[sdoterm.SdoTermType.DATATYPE] = []
            ttypes[sdoterm.SdoTermType.ENUMERATION] = []
            ttypes[sdoterm.SdoTermType.ENUMERATIONVALUE] = []
        if t.termType == sdoterm.SdoTermType.REFERENCE:
            continue
        ttypes[t.termType].append(t)
        termcount += 1

    sorted_termcat: Dict[str, Dict[sdoterm.SdoTermType, List[sdoterm.SdoTerm]]] = dict(sorted(termcat.items()))
    return sorted_termcat, termcount


class UnknownTermError(LookupError):
    """Raised when there is no definition for a given term."""


class listingNode:
    def __init__(self, term: str, depth: int = 0, title: str = "", parent: Optional["listingNode"] = None, visit_set: Optional[Set[str]] = None) -> None:
        termdesc = sdotermsource.SdoTermSource.getTerm(term)
        if not termdesc:
            raise UnknownTermError(f"No description for term {term}")
        visit_set = visit_set or set()
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
            if termdesc.termType == sdoterm.SdoTermType.ENUMERATION:
                for enum in sorted(termdesc.enumerationMembers.ids):
                    try:
                        self.subs.append(
                            listingNode(
                                enum, depth=depth + 1, parent=self, visit_set=visit_set
                            )
                        )
                    except UnknownTermError as e:
                        log.warning(
                            f"Error while building enumeration node {enum} for {term}: {e}"
                        )
            for sub in sorted(termdesc.subs.ids):
                try:
                    self.subs.append(
                        listingNode(
                            sub, depth=depth + 1, parent=self, visit_set=visit_set
                        )
                    )
                except UnknownTermError as e:
                    log.warning(
                        f"Error while building child node {sub} for {term}: {e}"
                    )
        else:  # Visited this node before so don't parse children
            self.repeat = True


def jsonldtree(page: str) -> str:
    term: Dict[str, Any] = {}
    context: Dict[str, Any] = {}
    context["rdfs"] = "http://www.w3.org/2000/01/rdf-schema#"
    context["schema"] = "https://schema.org"
    context["rdfs:subClassOf"] = {"@type": "@id"}
    context["description"] = "rdfs:comment"
    context["children"] = {"@reverse": "rdfs:subClassOf"}
    term["@context"] = context
    data: Dict[str, Any] = _jsonldtree("Thing", visitset=set(), term=term)
    return json.dumps(sort_dict(data), indent=2)


def _jsonldtree(tid: str, visitset: Set[str], term: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    try:
        termdesc = sdotermsource.SdoTermSource.getTerm(tid)
        if not termdesc:
            raise UnknownTermError(f"No description for term {tid}")
        if term is None:
            term = {}
        term["@type"] = "rdfs:Class"
        term["@id"] = "schema:" + termdesc.id
        term["name"] = termdesc.label
        if termdesc.supers:
            sups: List[str] = ["schema:" + sup for sup in termdesc.supers.ids]
            if len(sups) == 1:
                term["rdfs:subClassOf"] = sups[0]
            else:
                term["rdfs:subClassOf"] = sups
        term["description"] = textutils.ShortenOnSentence(
            textutils.StripHtmlTags(termdesc.comment)
        )
        if termdesc.pending:
            term["pending"] = True
        if termdesc.retired:
            term["attic"] = True
        if tid not in visitset:
            visitset.add(tid)
            if termdesc.subs:
                subs: List[Dict[str, Any]] = []
                for sub in termdesc.subs.ids:
                    try:
                        subs.append(_jsonldtree(tid=sub, visitset=visitset))
                    except UnknownTermError as e:
                        log.warning(
                            f"Error while building listing node for {sub}: {e}"
                        )
                term["children"] = subs
        return term
    except Exception as e:
        e.add_note(f"while building JSON tree for id:{tid}-{term}")
        raise


listings: Optional[List[listingNode]] = None


def fullPage(page: str) -> str:
    global listings
    if not listings:
        listings = []
        listings.append(listingNode("Thing", title="Types:"))
        listings.append(listingNode("DataType", title="DataTypes:"))
    extra_vars: Dict[str, Any] = {
        "home_page": "False",
        "title": "Full schema hierarchy",
        "listings": listings,
    }

    return docsTemplateRender("docs/%s.j2" % page, extra_vars)


def fullReleasePage(page: str) -> str:
    node_listings: List[listingNode] = []
    node_listings.append(listingNode("Thing", title="Type hierarchy"))
    
    all_enum_vals = sdotermsource.SdoTermSource.getAllEnumerationvalues(expanded=True)
    all_types = sdotermsource.SdoTermSource.getAllTypes(expanded=True)
    
    types: List[sdoterm.SdoTerm] = []
    for t in all_enum_vals + all_types:
        if isinstance(t, sdoterm.SdoTerm):
            types.append(t)
            
    types = sdotermsource.SdoTermSource.expandTerms(types)
    types = sorted(types, key=lambda t: t.id)
    
    all_props = sdotermsource.SdoTermSource.getAllProperties(expanded=True)
    properties: List[sdoterm.SdoTerm] = []
    for p in all_props:
        if isinstance(p, sdoterm.SdoTerm):
            properties.append(p)

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
    colls: List[sdocollaborators.collaborator] = sdocollaborators.collaborator.collaborators()

    # TODO Handle collaborators that are not contributors

    colls = sorted(colls, key=lambda t: t.title or "")

    for coll in colls:
        createCollab(coll)

    extra_vars: Dict[str, Any] = {"collaborators": colls, "title": "Collaborators"}
    return docsTemplateRender("docs/Collabs.j2", extra_vars)


def createCollab(coll: sdocollaborators.collaborator) -> None:
    terms: Dict[str, Dict[sdoterm.SdoTermType, List[sdoterm.SdoTerm]]] = {}
    termcount: int = 0
    contributor: bool = coll.contributor

    if contributor:
        terms, termcount = buildTermCatList(coll.getTerms())

    extra_vars: Dict[str, Any] = {
        "coll": coll,
        "title": coll.title,
        "contributor": contributor,
        "terms": terms,
        "termcount": termcount,
    }

    content: str = docsTemplateRender("docs/Collab.j2", extra_vars)
    filename: str = fileutils.ensureAbsolutePath(
        output_dir=schemaglobals.OUTPUTDIR,
        relative_path=os.path.join("docs/collab/", coll.ref + ".html"),
    )
    with open(filename, "w", encoding="utf8") as handle:
        handle.write(content)
    log.info("Created %s" % filename)


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
            "releases/%s/schema-all.html" % schemaversion.getVersion(),
        ],
    ),
    # "Collabs": (collabs,["docs/collaborators.html"]),
    "TermFind": (termfind, ["docs/termfind/termlist.txt"]),
    "Tree": (jsonldtree, ["docs/tree.jsonld"]),
}


def buildDocs(pages: Iterable[str]) -> None:
    process_pages: List[str]
    if any(filter(fileutils.isAll, pages)):
        process_pages = sorted(PAGELIST.keys())
    else:
        process_pages = list(pages)

    for page in process_pages:
        if page not in PAGELIST.keys():
            log.warning(f"Unknown page name: {page}")
            continue
        entry = PAGELIST.get(page)
        if not entry:
            log.warning(f"Missing entry for page {page}")
            continue
        func, filenames = entry
        if not func:
            log.warning(f"Missing function for page {page}")
            continue
        with pretty_logger.BlockLog(logger=log, message=f"Generating page {page}"):
            content: str = func(page)
            for relative_path in filenames:
                filename: str = fileutils.ensureAbsolutePath(
                    output_dir=schemaglobals.OUTPUTDIR, relative_path=relative_path
                )
                with open(filename, "w", encoding="utf8") as handle:
                    handle.write(content)
