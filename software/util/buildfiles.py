#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import standard python libraries
import csv
import io
import json
import logging
import os
import rdflib
import rdflib.namespace
import sys

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software

import software.scripts.shex_shacl_shapes_exporter as shex_shacl_shapes_exporter
import software.util.fileutils as fileutils
import software.util.pretty_logger as pretty_logger
import software.util.schemaglobals as schemaglobals
import software.util.schemaversion as schemaversion
import software.util.sdojsonldcontext as sdojsonldcontext
import software.util.textutils as textutils

import software.SchemaTerms.sdotermsource as sdotermsource
import software.SchemaTerms.sdoterm as sdoterm
import software.SchemaExamples.schemaexamples as schemaexamples

VOCABURI = sdotermsource.SdoTermSource.vocabUri()

log = logging.getLogger(__name__)


def buildTurtleEquivs():
    """Build equivalences to"""
    s_p = "http://schema.org/"
    s_s = "https://schema.org/"
    outGraph = rdflib.Graph()
    outGraph.bind("schema_p", s_p)
    outGraph.bind("schema_s", s_s)
    outGraph.bind("owl", rdflib.namespace.OWL)

    for t in sdotermsource.SdoTermSource.getAllTerms(expanded=True):
        if not t.retired:  # drops non-schema terms and those in attic
            eqiv = rdflib.namespace.OWL.equivalentClass
            if t.termType == sdoterm.SdoTermType.PROPERTY:
                eqiv = rdflib.namespace.OWL.equivalentProperty

            p = rdflib.URIRef(s_p + t.id)
            s = rdflib.URIRef(s_s + t.id)
            outGraph.add((p, eqiv, s))
            outGraph.add((s, eqiv, p))
            log.debug("%s ", t.uri)

    return outGraph.serialize(format="turtle", auto_compact=True, sort_keys=True)


def absoluteFilePath(fn):
    name = os.path.join(schemaglobals.OUTPUTDIR, fn)
    fileutils.checkFilePath(os.path.dirname(name))
    return name


def jsonldcontext(page):
    return sdojsonldcontext.getContext()


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


def _jsonldtree(tid, term=None):
    termdesc = sdotermsource.SdoTermSource.getTerm(tid)
    if not term:
        term = {}
    term["@type"] = "rdfs:Class"
    term["@id"] = "schema:" + termdesc.id
    term["name"] = termdesc.label
    if termdesc.supers:
        sups = []
        for sup in termdesc.supers.ids:
            sups.append("schema:" + sup)
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
                subs.append(_jsonldtree(sub))
            term["children"] = subs
    return term


def httpequivs(page):
    return buildTurtleEquivs()


def owl(page):
    from sdoowl import OwlBuild

    return OwlBuild().getContent()


def sitemap(page):
    node = """ <url>
   <loc>https://schema.org/%s</loc>
   <lastmod>%s</lastmod>
 </url>
"""
    STATICPAGES = [
        "docs/schemas.html",
        "docs/full.html",
        "docs/gs.html",
        "docs/about.html",
        "docs/howwework.html",
        "docs/releases.html",
        "docs/faq.html",
        "docs/datamodel.html",
        "docs/developers.html",
        "docs/extension.html",
        "docs/meddocs.html",
        "docs/hotels.html",
    ]

    output = []
    output.append("""<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
""")
    terms = sdotermsource.SdoTermSource.getAllTerms(suppressSourceLinks=True)
    version_date = schemaversion.getCurrentVersionDate()
    for term in terms:
        if not (term.startswith("http://") or term.startswith("https://")):
            output.append(node % (term, version_date))
    for term in STATICPAGES:
        output.append(node % (term, version_date))
    output.append("</urlset>\n")
    return "".join(output)


def protocolSwap(content, protocol, altprotocol):
    ret = content.replace("%s://schema.org" % protocol, "%s://schema.org" % altprotocol)
    for ext in ["attic", "auto", "bib", "health-lifesci", "meta", "pending"]:
        ret = ret.replace(
            "%s://%s.schema.org" % (protocol, ext),
            "%s://%s.schema.org" % (altprotocol, ext),
        )
    return ret


def protocols():
    """Return the protocols (http, https) in order of priority."""
    vocaburi = sdotermsource.SdoTermSource.vocabUri()
    if vocaburi.startswith("https"):
        return "https", "http"
    return "http", "https"


allGraph = None
currentGraph = None


def exportrdf(exportType):
    global allGraph, currentGraph

    if not allGraph:
        allGraph = rdflib.Graph()
        allGraph.bind("schema", VOCABURI)
        currentGraph = rdflib.Graph()
        currentGraph.bind("schema", VOCABURI)

        allGraph += sdotermsource.SdoTermSource.sourceGraph()

        protocol, altprotocol = protocols()

        deloddtriples = """DELETE {?s ?p ?o}
            WHERE {
                ?s ?p ?o.
                FILTER (! strstarts(str(?s), "%s://schema.org") ).
            }""" % (protocol)
        allGraph.update(deloddtriples)
        currentGraph += allGraph

        delattic = """PREFIX schema: <%s://schema.org/>
        DELETE {?s ?p ?o}
        WHERE{
            ?s ?p ?o;
                schema:isPartOf <%s://attic.schema.org>.
        }""" % (protocol, protocol)
        currentGraph.update(delattic)

    formats = ["json-ld", "turtle", "nt", "nquads", "rdf"]
    extype = exportType[len("RDFExport."):]
    if exportType == "RDFExports":
        for output_format in sorted(formats):
            _exportrdf(output_format, allGraph, currentGraph)
    elif extype in formats:
        _exportrdf(extype, allGraph, currentGraph)
    else:
        raise Exception("Unknown export format: %s" % exportType)


# Set of completed EDF exports.
completed_rdf_exports = set()


def _exportrdf(output_format, all, current):

    protocol, altprotocol = protocols()

    if output_format in completed_rdf_exports:
        return
    else:
        completed_rdf_exports.add(output_format)

    version = schemaversion.getVersion()

    for selector in fileutils.FILESET_SELECTORS:
        if fileutils.isAll(selector):
            g = all
        else:
            g = current
        if output_format == "nquads":
            gr = rdflib.Dataset()
            qg = gr.graph(rdflib.URIRef("%s://schema.org/%s" % (protocol, version)))
            qg += g
            g = gr
        fn = fileutils.releaseFilePath(
            output_dir=schemaglobals.getOutputDir(),
            version=version,
            selector=selector,
            protocol=protocol,
            output_format=output_format,
        )

        afn = fileutils.releaseFilePath(
            output_dir=schemaglobals.getOutputDir(),
            version=version,
            selector=selector,
            protocol=altprotocol,
            output_format=output_format,
        )

        with pretty_logger.BlockLog(logger=log, message=f"Exporting {fn} and {afn}"):
            if output_format == "rdf":
                fmt = "pretty-xml"
            else:
                fmt = output_format
            out = g.serialize(format=fmt, auto_compact=True, sort_keys=True)
            with open(fn, "w", encoding="utf8") as f:
                f.write(out)
            with open(afn, "w", encoding="utf8") as af:
                af.write(protocolSwap(out, protocol=protocol, altprotocol=altprotocol))


def array2str(values):
    if not values:
        return ""
    return ", ".join(values)


def uriwrap(thing):
    """Convert various types into uris."""
    if not thing:
        return ""
    if isinstance(thing, str):
        if thing.startswith("http:") or thing.startswith("https:"):
            return thing
        return VOCABURI + thing
    if isinstance(thing, sdoterm.SdoTermSequence):
        return uriwrap(thing.ids)
    if isinstance(thing, sdoterm.SdoTermOrId):
        return uriwrap(thing.id)
    if isinstance(thing, sdoterm.SdoTerm):
        return uriwrap(thing.id)
    try:
        return array2str(map(uriwrap, thing))
    except TypeError as e:
        log.fatal("Cannot uriwrap %s:%s", thing, e)


def exportcsv(page):
    protocol, altprotocol = protocols()

    typeFields = [
        "id",
        "label",
        "comment",
        "subTypeOf",
        "enumerationtype",
        "equivalentClass",
        "properties",
        "subTypes",
        "supersedes",
        "supersededBy",
        "isPartOf",
    ]
    propFields = [
        "id",
        "label",
        "comment",
        "subPropertyOf",
        "equivalentProperty",
        "subproperties",
        "domainIncludes",
        "rangeIncludes",
        "inverseOf",
        "supersedes",
        "supersededBy",
        "isPartOf",
    ]
    typedata = []
    typedataAll = []
    propdata = []
    propdataAll = []
    terms = sdotermsource.SdoTermSource.getAllTerms(
        expanded=True, suppressSourceLinks=True
    )
    for term in terms:
        if (
            term.termType == sdoterm.SdoTermType.REFERENCE
            or term.id.startswith("http://")
            or term.id.startswith("https://")
        ):
            continue
        row = {}
        row["id"] = term.uri
        row["label"] = term.label
        row["comment"] = term.comment
        row["supersedes"] = uriwrap(term.supersedes)
        row["supersededBy"] = uriwrap(term.supersededBy)
        ext = term.extLayer
        if len(ext):
            ext = "%s://%s.schema.org" % (protocol, ext)
        row["isPartOf"] = ext
        if term.termType == sdoterm.SdoTermType.PROPERTY:
            row["subPropertyOf"] = uriwrap(term.supers)
            row["equivalentProperty"] = uriwrap(term.equivalents.ids)
            row["subproperties"] = uriwrap(term.subs.ids)
            row["domainIncludes"] = uriwrap(term.domainIncludes.ids)
            row["rangeIncludes"] = uriwrap(term.rangeIncludes.ids)
            row["inverseOf"] = uriwrap(term.inverse.id)
            propdataAll.append(row)
            if not term.retired:
                propdata.append(row)
        else:
            row["subTypeOf"] = uriwrap(term.supers.ids)
            if term.termType == sdoterm.SdoTermType.ENUMERATIONVALUE:
                row["enumerationtype"] = uriwrap(term.enumerationParent.id)
            else:
                row["properties"] = uriwrap(term.allproperties.ids)
            row["equivalentClass"] = uriwrap(term.equivalents.ids)
            row["subTypes"] = uriwrap(term.subs.ids)
            typedataAll.append(row)
            if not term.retired:
                typedata.append(row)

    writecsvout(
        "properties",
        propdata,
        propFields,
        fileutils.FileSelector.CURRENT,
        protocol,
        altprotocol,
    )
    writecsvout(
        "properties",
        propdataAll,
        propFields,
        fileutils.FileSelector.ALL,
        protocol,
        altprotocol,
    )
    writecsvout(
        "types",
        typedata,
        typeFields,
        fileutils.FileSelector.CURRENT,
        protocol,
        altprotocol,
    )
    writecsvout(
        "types",
        typedataAll,
        typeFields,
        fileutils.FileSelector.ALL,
        protocol,
        altprotocol,
    )


def writecsvout(ftype, data, fields, selector, protocol, altprotocol):
    version = schemaversion.getVersion()
    fn = fileutils.releaseFilePath(
        output_dir=schemaglobals.getOutputDir(),
        version=version,
        selector=selector,
        protocol=protocol,
        suffix=ftype,
        output_format="csv",
    )
    afn = fileutils.releaseFilePath(
        output_dir=schemaglobals.getOutputDir(),
        version=version,
        selector=selector,
        protocol=altprotocol,
        suffix=ftype,
        output_format="csv",
    )

    with pretty_logger.BlockLog(
        message=f"Preparing files {ftype}: {fn} and {afn}.", logger=log
    ):
        # Create the original version in memory.
        with io.StringIO() as csv_buffer:
            writer = csv.DictWriter(
                csv_buffer,
                fieldnames=fields,
                quoting=csv.QUOTE_ALL,
                lineterminator="\n",
            )
            writer.writeheader()
            for row in data:
                writer.writerow(row)
            data = csv_buffer.getvalue()

        with open(fn, "w", encoding="utf8") as file_handle:
            file_handle.write(data)

        with open(afn, "w", encoding="utf8") as file_handle:
            file_handle.write(
                protocolSwap(data, protocol=protocol, altprotocol=altprotocol)
            )


def jsoncounts(page):
    counts = sdotermsource.SdoTermSource.termCounts()
    counts["schemaorgversion"] = schemaversion.getVersion()
    return json.dumps(counts)


def jsonpcounts(page):
    content = """
    COUNTS = '%s';

    insertschemacounts ( COUNTS );
    """ % jsoncounts(page)
    return content


def exportshex_shacl(page):
    release_dir = os.path.join(
        os.getcwd(), schemaglobals.RELEASE_DIR, schemaversion.getVersion()
    )
    shex_shacl_shapes_exporter.generate_files(
        term_defs_path=os.path.join(release_dir, "schemaorg-all-http.nt"),
        outputdir=release_dir,
        outputfileprefix="schemaorg-",
    )


def examples(page):
    return schemaexamples.SchemaExamples.allExamplesSerialised()


FILELIST = {
    "Context": (
        jsonldcontext,
        [
            "docs/jsonldcontext.jsonld",
            "docs/jsonldcontext.json",
            "docs/jsonldcontext.json.txt",
            "releases/%s/schemaorgcontext.jsonld" % schemaversion.getVersion(),
        ],
    ),
    "Tree": (jsonldtree, ["docs/tree.jsonld"]),
    "jsoncounts": (jsoncounts, ["docs/jsoncounts.json"]),
    "jsonpcounts": (jsonpcounts, ["docs/jsonpcounts.js"]),
    "Owl": (
        owl,
        [
            "docs/schemaorg.owl",
            "releases/%s/schemaorg.owl" % schemaversion.getVersion(),
        ],
    ),
    "Httpequivs": (
        httpequivs,
        ["releases/%s/httpequivs.ttl" % schemaversion.getVersion()],
    ),
    "Sitemap": (sitemap, ["docs/sitemap.xml"]),
    "RDFExports": (exportrdf, [""]),
    "RDFExport.turtle": (exportrdf, [""]),
    "RDFExport.rdf": (exportrdf, [""]),
    "RDFExport.nt": (exportrdf, [""]),
    "RDFExport.nquads": (exportrdf, [""]),
    "RDFExport.json-ld": (exportrdf, [""]),
    "Shex_Shacl": (exportshex_shacl, [""]),
    "CSVExports": (exportcsv, [""]),
    "Examples": (
        examples,
        ["releases/%s/schemaorg-all-examples.txt" % schemaversion.getVersion()],
    ),
}


def buildFiles(files):
    log.debug("Initalizing Mardown")
    software.SchemaTerms.localmarkdown.MarkdownTool.setWikilinkCssClass("localLink")
    software.SchemaTerms.localmarkdown.MarkdownTool.setWikilinkPrePath(
        "https://schema.org/"
    )
    # Production site uses no suffix in link - mapping to file done in server config
    software.SchemaTerms.localmarkdown.MarkdownTool.setWikilinkPostPath("")

    if any(filter(fileutils.isAll, files)):
        files = sorted(FILELIST.keys())

    for p in files:
        with pretty_logger.BlockLog(message=f"Preparing file {p}.", logger=log):
            if p in FILELIST.keys():
                func, filenames = FILELIST.get(p, None)
                if func:
                    content = func(p)
                    if content:
                        for filename in filenames:
                            fn = absoluteFilePath(filename)
                            with open(fn, "w", encoding="utf8") as handle:
                                handle.write(content)
            else:
                log.warning("Unknown files name: %s" % p)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    buildFiles(sys.argv[1:])
