#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import standard python libraries

import json
import logging
import os
import sys

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software.scripts.buildtermlist as buildtermlist
import software.util.fileutils as fileutils
import software.util.jinga_render as jinga_render
import software.util.pretty_logger as pretty_logger
import software.util.schemaglobals as schemaglobals
import software.util.schemaversion as schemaversion
import software.util.textutils as textutils

import software.SchemaTerms.sdotermsource as sdotermsource
import software.SchemaTerms.sdocollaborators as sdocollaborators
import software.SchemaTerms.sdoterm as sdoterm

log = logging.getLogger(__name__)


def docsTemplateRender(template, extra_vars=None):
    tvars = {"BUILDOPTS": schemaglobals.BUILDOPTS, "docsdir": schemaglobals.DOCSDOCSDIR}
    if extra_vars:
        tvars.update(extra_vars)
    return jinga_render.templateRender(template, tvars)


def schemasPage(page):
    extra_vars = {
        "home_page": "False",
        "title": "Schemas",
        "termcounts": sdotermsource.SdoTermSource.termCounts(),
    }
    return docsTemplateRender("docs/Schemas.j2", extra_vars)


def homePage(page):
    global STRCLASSVAL
    title = schemaglobals.SITENAME
    template = "docs/Home.j2"
    filt = None
    overrideclassval = None
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
    sectionterms = {}
    termcount = 0
    if filt:
        terms = sdotermsource.SdoTermSource.getAllTerms(layer=filt, expanded=True)
        for t in terms:
            t.cat = ""
            if filt == "pending":
                for s in t.sources:
                    if "schemaorg/issue" in s:
                        t.cat = "issue-" + os.path.basename(s)
                        break
        terms.sort(key=lambda u: (u.cat, u.id))
        sectionterms, termcount = buildTermCatList(terms, checkCat=True)

    extra_vars = {
        "home_page": "True",
        "title": title,
        "termcount": termcount,
        "sectionterms": sectionterms,
    }
    STRCLASSVAL = overrideclassval
    ret = docsTemplateRender(template, extra_vars)
    STRCLASSVAL = None
    return ret


def buildTermCatList(terms, checkCat=False):
    first = True
    cat = None
    termcat = {}
    termcount = 0
    for t in terms:
        if checkCat:
            tcat = t.cat
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

    termcat = dict(sorted(termcat.items()))
    return termcat, termcount


VISITLIST = []


class listingNode:
    def __init__(self, term, depth=0, title="", parent=None):
        global VISITLIST
        termdesc = sdotermsource.SdoTermSource.getTerm(term)
        if parent is None:
            VISITLIST = []
        self.repeat = False
        self.subs = []
        self.parent = parent
        self.title = title
        self.id = termdesc.label
        self.termType = termdesc.termType
        self.depth = depth
        self.retired = termdesc.retired
        self.pending = termdesc.pending
        if self.id not in VISITLIST:
            VISITLIST.append(self.id)
            if termdesc.termType == sdoterm.SdoTermType.ENUMERATION:
                for enum in sorted(termdesc.enumerationMembers.ids):
                    self.subs.append(listingNode(enum, depth=depth + 1, parent=self))
            for sub in sorted(termdesc.subs.ids):
                self.subs.append(listingNode(sub, depth=depth + 1, parent=self))

        else:  # Visited this node before so don't parse children
            self.repeat = True


def jsonldtree(page):
    global VISITLIST
    VISITLIST = []

    term = {}
    context = {}
    context["rdfs"] = "http://www.w3.org/2000/01/rdf-schema#"
    context["schema"] = "https://schema.org"
    context["rdfs:subClassOf"] = {"@type": "@id"}
    context["description"] = "rdfs:comment"
    context["children"] = {"@reverse": "rdfs:subClassOf"}
    term["@context"] = context
    data = _jsonldtree("Thing", term)
    return json.dumps(data, indent=3)


def _jsonldtree(tid: str, term=None):
    termdesc = sdotermsource.SdoTermSource.getTerm(tid)
    if not term:
        term = {}
    term["@type"] = "rdfs:Class"
    term["@id"] = "schema:" + termdesc.id
    term["name"] = termdesc.label
    if termdesc.supers:
        sups = ["schema:" + sup for sup in termdesc.supers.ids]
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
    if tid not in VISITLIST:
        VISITLIST.append(tid)
        if termdesc.subs:
            subs = []
            for sub in termdesc.subs.ids:
                subs.append(_jsonldtree(tid=sub))
            term["children"] = subs
    return term


listings = None


def fullPage(page):
    global listings
    if not listings:
        listings = []
        listings.append(listingNode("Thing", title="Types:"))
        listings.append(listingNode("DataType", title="DataTypes:"))
    extra_vars = {
        "home_page": "False",
        "title": "Full schema hierarchy",
        "listings": listings,
    }

    return docsTemplateRender("docs/%s.j2" % page, extra_vars)


def fullReleasePage(page):
    listings = []
    listings.append(listingNode("Thing", title="Type hierarchy"))
    types = sdotermsource.SdoTermSource.getAllEnumerationvalues(expanded=True)
    types.extend(sdotermsource.SdoTermSource.getAllTypes(expanded=True))
    types = sdotermsource.SdoTermSource.expandTerms(types)
    types = sorted(types, key=lambda t: t.id)
    extra_vars = {
        "home_page": "False",
        "title": "Full Release Summary",
        "version": schemaversion.getVersion(),
        "date": schemaversion.getCurrentVersionDate(),
        "listings": listings,
        "types": types,
        "properties": sdotermsource.SdoTermSource.getAllProperties(expanded=True),
    }
    return docsTemplateRender("docs/FullRelease.j2", extra_vars)


def collabs(page):
    colls = sdocollaborators.collaborator.collaborators()

    # TODO Handle collaborators that are not contributors

    colls = sorted(colls, key=lambda t: t.title)

    for coll in colls:
        createCollab(coll)

    extra_vars = {"collaborators": colls, "title": "Collaborators"}
    return docsTemplateRender("docs/Collabs.j2", extra_vars)


def createCollab(coll):
    terms = []
    termcount = 0
    contributor = coll.contributor

    if contributor:
        terms, termcount = buildTermCatList(coll.getTerms())

    extra_vars = {
        "coll": coll,
        "title": coll.title,
        "contributor": contributor,
        "terms": terms,
        "termcount": termcount,
    }

    content = docsTemplateRender("docs/Collab.j2", extra_vars)
    filename = fileutils.ensureAbsolutePath(
        output_dir=schemaglobals.OUTPUTDIR,
        relative_path=os.path.join("docs/collab/", coll.ref + ".html"),
    )
    with open(filename, "w", encoding="utf8") as handle:
        handle.write(content)
    log.info("Created %s" % filename)


def termfind(file):
    if not schemaglobals.hasOpt("notermfinder"):
        log.info("Building term list")
        return "".join(buildtermlist.generateTerms(tags=True))
    return ""


PAGELIST = {
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


def buildDocs(pages):
    if any(filter(fileutils.isAll, pages)):
        pages = sorted(PAGELIST.keys())

    for page in pages:
        if page not in PAGELIST.keys():
            log.warning(f"Unknown page name: {page}")
            continue
        func, filenames = PAGELIST.get(page, None)
        if not func:
            log.warning(f"Missing function for page {page}")
            continue
        with pretty_logger.BlockLog(logger=log, message=f"Generating page {page}"):
            content = func(page)
            for relative_path in filenames:
                filename = fileutils.ensureAbsolutePath(
                    output_dir=schemaglobals.OUTPUTDIR, relative_path=relative_path
                )
                with open(filename, "w", encoding="utf8") as handle:
                    handle.write(content)
