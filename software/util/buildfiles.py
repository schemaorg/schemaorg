#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import standard python libraries
import csv
import io
import json
import logging
import os
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, Set
import rdflib
import rdflib.namespace
import sys
from rdflib.compare import to_canonical_graph

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
from software.util.sort_dict import sort_dict, sort_xml

VOCABURI: str = sdotermsource.SdoTermSource.vocabUri()

log: logging.Logger = logging.getLogger(__name__)

VISITLIST: List[str] = []

def buildTurtleEquivs() -> str:
    """Build equivalences to"""
    s_p: str = "http://schema.org/"
    s_s: str = "https://schema.org/"
    outGraph: rdflib.Graph = rdflib.Graph()
    outGraph.bind("schema_p", s_p)
    outGraph.bind("schema_s", s_s)
    outGraph.bind("owl", rdflib.namespace.OWL)

    all_terms: List[sdoterm.SdoTerm] = sdotermsource.SdoTermSource.getAllTerms(expanded=True)
    for t in all_terms:
        if not t.retired:  # drops non-schema terms and those in attic
            eqiv: rdflib.term.URIRef = rdflib.namespace.OWL.equivalentClass
            if t.termType == sdoterm.SdoTermType.PROPERTY:
                eqiv = rdflib.namespace.OWL.equivalentProperty

            p: rdflib.URIRef = rdflib.URIRef(s_p + t.id)
            s: rdflib.URIRef = rdflib.URIRef(s_s + t.id)
            outGraph.add((p, eqiv, s))
            outGraph.add((s, eqiv, p))
            log.debug("%s ", t.uri)

    return str(outGraph.serialize(format="turtle", auto_compact=True, sort_keys=True))


def absoluteFilePath(fn: str) -> str:
    name: str = os.path.join(schemaglobals.OUTPUTDIR, fn)
    fileutils.checkFilePath(os.path.dirname(name))
    return name


def jsonldcontext(page: str) -> str:
    return str(sdojsonldcontext.getContext())


def jsonldtree(page: str) -> str:
    global VISITLIST
    VISITLIST = []

    term: Dict[str, Any] = {}
    context: Dict[str, Any] = {}
    context["rdfs"] = "http://www.w3.org/2000/01/rdf-schema#"
    context["schema"] = "https://schema.org"
    context["rdfs:subClassOf"] = {"@type": "@id"}
    context["description"] = "rdfs:comment"
    context["children"] = {"@reverse": "rdfs:subClassOf"}
    term["@context"] = context
    data: Dict[str, Any] = _jsonldtree("Thing", term)
    return json.dumps(sort_dict(data), indent=3)


def _jsonldtree(tid: str, term: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    termdesc: Optional[sdoterm.SdoTerm] = sdotermsource.SdoTermSource.getTerm(tid)
    if not termdesc:
        return term or {}
    if term is None:
        term = {}
    term["@type"] = "rdfs:Class"
    term["@id"] = "schema:" + termdesc.id
    term["name"] = termdesc.label
    if termdesc.supers:
        sups: List[str] = []
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
            subs: List[Dict[str, Any]] = []
            for sub in termdesc.subs.ids:
                subs.append(_jsonldtree(sub))
            term["children"] = subs
    return term


def httpequivs(page: str) -> str:
    return buildTurtleEquivs()


def owl(page: str) -> str:
    from software.util.sdoowl import OwlBuild

    return str(OwlBuild().getContent())


def sitemap(page: str) -> str:
    node: str = """ <url>
   <loc>https://schema.org/%s</loc>
   <lastmod>%s</lastmod>
 </url>
"""
    STATICPAGES: List[str] = [
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

    output: List[str] = []
    output.append("""<?xml version="1.0" encoding="utf-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
""")
    terms: List[str] = sdotermsource.SdoTermSource.getAllTerms(suppressSourceLinks=True)
    version_date: str = schemaversion.getCurrentVersionDate()
    for term in sorted(terms):
        if not (str(term).startswith("http://") or str(term).startswith("https://")):
            output.append(node % (term, version_date))
    for term in STATICPAGES:
        output.append(node % (term, version_date))
    output.append("</urlset>\n")
    return "".join(output)


def protocolSwap(content: str, protocol: str, altprotocol: str) -> str:
    ret: str = content.replace("%s://schema.org" % protocol, "%s://schema.org" % altprotocol)
    for ext in ["attic", "auto", "bib", "health-lifesci", "meta", "pending"]:
        ret = ret.replace(
            "%s://%s.schema.org" % (protocol, ext),
            "%s://%s.schema.org" % (altprotocol, ext),
        )
    return ret


def protocols() -> Tuple[str, str]:
    """Return the protocols (http, https) in order of priority."""
    vocaburi: str = sdotermsource.SdoTermSource.vocabUri()
    if vocaburi.startswith("https"):
        return "https", "http"
    return "http", "https"


allGraph: Optional[rdflib.Graph] = None
currentGraph: Optional[rdflib.Graph] = None


def exportrdf(exportType: str, subdirectory_path: Optional[str] = None) -> None:
    global allGraph, currentGraph

    if not allGraph:
        # The bindings need to be done for each graph
        # as they are not copied over.
        allGraph = rdflib.Graph()
        allGraph.bind("schema", VOCABURI)
        sdotermsource.bindNameSpaces(allGraph)
        currentGraph = rdflib.Graph()
        sdotermsource.bindNameSpaces(currentGraph)
        currentGraph.bind("schema", VOCABURI)

        # Loads triples AND the bindings you added to sourceGraph()
        allGraph += sdotermsource.SdoTermSource.sourceGraph()

        protocol, altprotocol = protocols()

        log.debug("Cleanup non schema org things.")
        # We delete everything where Subject is not schema.org.
        # Since we haven't created the new types yet, they are safe.
        deloddtriples: str = """DELETE {?s ?p ?o}
           WHERE {
               ?s ?p ?o.
               FILTER (! strstarts(str(?s), "%s://schema.org") ).
           }""" % (protocol)
        allGraph.update(deloddtriples)

        log.debug("Generate Foreign types – SPARQL INSERT")
        # Insert all the types and properties that are equivalent or inherited from.
        insert_foreign_types: str = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>

        INSERT {
            ?classNode a rdfs:Class .
            ?propNode a rdf:Property .
        }
        WHERE {
            { # Find Foreign Classes
                { ?s rdfs:subClassOf ?classNode } UNION { ?s owl:equivalentClass ?classNode }

                FILTER (isURI(?classNode))
                FILTER (?classNode != rdfs:Class)
                FILTER (?classNode != owl:Class)
                FILTER (?classNode != rdf:Property)
                FILTER (!strstarts(str(?classNode), "%s://schema.org"))
            }
            UNION
            { # Find Foreign Properties
                { ?s rdfs:subPropertyOf ?propNode } UNION { ?s owl:equivalentProperty ?propNode }

                FILTER (isURI(?propNode))
                FILTER (?propNode != rdf:Property)
                FILTER (?propNode != owl:ObjectProperty)
                FILTER (?propNode != owl:DatatypeProperty)
                FILTER (!strstarts(str(?propNode), "%s://schema.org"))
            }
        }
        """ % (protocol, protocol)

        allGraph.update(insert_foreign_types)

        log.debug("Merge")
        currentGraph += allGraph

        log.debug("Delete items from the attic")
        delattic: str = """PREFIX schema: <%s://schema.org/>
        DELETE {?s ?p ?o}
        WHERE{
          ?s ?p ?o;
              schema:isPartOf <%s://attic.schema.org>.
        }""" % (protocol, protocol)

        currentGraph.update(delattic)

    formats: List[str] = ["json-ld", "turtle", "nt", "nquads", "rdf"]
    extype: str = exportType[len("RDFExport.") :]
    if exportType == "RDFExports":
        for output_format in sorted(formats):
            _exportrdf(output_format, allGraph, currentGraph, subdirectory_path)
    elif extype in formats:
        _exportrdf(extype, allGraph, currentGraph, subdirectory_path)
    else:
        raise Exception("Unknown export format: %s" % exportType)


# Set of completed EDF exports.
completed_rdf_exports: Set[str] = set()


def _exportrdf(output_format: str, all_graph: rdflib.Graph, current_graph: rdflib.Graph, subdirectory_path: Optional[str] = None) -> None:
    protocol, altprotocol = protocols()

    if output_format in completed_rdf_exports:
        return
    else:
        completed_rdf_exports.add(output_format)

    version: str = schemaversion.getVersion()

    for selector in fileutils.FILESET_SELECTORS:
        g: Union[rdflib.Graph, rdflib.Dataset]
        if fileutils.isAll(selector):
            g = all_graph
        else:
            g = current_graph

        nsMgr = g.namespace_manager
        g = to_canonical_graph(g)
        g.namespace_manager = nsMgr

        if output_format == "nquads":
            gr: rdflib.Dataset = rdflib.Dataset()
            qg: rdflib.Graph = gr.graph(rdflib.URIRef("%s://schema.org/%s" % (protocol, version)))
            qg += g
            g = gr

        for p in fileutils.FILESET_PROTOCOLS:
            fn: str = fileutils.releaseFilePath(
                output_dir=schemaglobals.getOutputDir(),
                version=version,
                selector=selector,
                protocol=p,
                output_format=output_format,
                subdirectory_path=subdirectory_path,
            )
            with pretty_logger.BlockLog(logger=log, message=f"Exporting {fn}"):
                fmt: str
                if output_format == "rdf":
                    fmt = "pretty-xml"
                else:
                    fmt = output_format
                out: str = str(g.serialize(format=fmt, auto_compact=True, sort_keys=True, max_depth=1))
                if output_format in ("nt", "nquads"):
                    out = "\n".join(sorted(line.rstrip() for line in out.splitlines() if line.strip())) + "\n"
                if output_format == "rdf":
                    try:
                        out = sort_xml(out)
                    except Exception as e:
                        log.warning(f"Failed to sort RDF XML: {e}")
                if output_format == "json-ld":
                    try:
                        data: Any = json.loads(out)
                        out = json.dumps(sort_dict(data), indent=2)
                    except Exception as e:
                        log.warning(f"Failed to sort JSON-LD: {e}")

                with open(fn, "w", encoding="utf8") as f:
                    if p == altprotocol:
                        out = protocolSwap(out, protocol, altprotocol)
                    f.write(out)


def array2str(values: List[str]) -> str:
    if not values:
        return ""
    return ", ".join(values)


def uriwrap(thing: Any) -> str:
    """Convert various types into uris. Sorts items if they are a list."""
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
        return array2str(sorted(map(uriwrap, thing)))
    except TypeError as e:
        log.fatal("Cannot uriwrap %s:%s", thing, e)
        return ""


def exportcsv(page: str) -> None:
    protocol, altprotocol = protocols()

    typeFields: List[str] = [
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
    propFields: List[str] = [
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
    typedata: List[Dict[str, str]] = []
    typedataAll: List[Dict[str, str]] = []
    propdata: List[Dict[str, str]] = []
    propdataAll: List[Dict[str, str]] = []
    terms: List[sdoterm.SdoTerm] = sdotermsource.SdoTermSource.getAllTerms(
        expanded=True, suppressSourceLinks=True
    )
    for term in terms:
        if not isinstance(term, sdoterm.SdoTerm):
            continue
        if (
            term.termType == sdoterm.SdoTermType.REFERENCE
            or term.id.startswith("http://")
            or term.id.startswith("https://")
        ):
            continue
        row: Dict[str, str] = {}
        row["id"] = term.uri
        row["label"] = term.label
        row["comment"] = term.comment
        row["supersedes"] = uriwrap(term.supersedes)
        row["supersededBy"] = uriwrap(term.supersededBy)
        ext: str = term.extLayer
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


def writecsvout(ftype: str, data: List[Dict[str, str]], fields: List[str], selector: Union[fileutils.FileSelector, str], protocol: str, altprotocol: str) -> None:
    version: str = schemaversion.getVersion()
    fn: str = fileutils.releaseFilePath(
        output_dir=schemaglobals.getOutputDir(),
        version=version,
        selector=selector,
        protocol=protocol,
        suffix=ftype,
        output_format="csv",
    )
    afn: str = fileutils.releaseFilePath(
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
        csv_data: str
        with io.StringIO() as csv_buffer:
            writer: csv.DictWriter = csv.DictWriter(
                csv_buffer,
                fieldnames=fields,
                quoting=csv.QUOTE_ALL,
                lineterminator="\n",
            )
            writer.writeheader()
            for row in data:
                writer.writerow(row)
            csv_data = csv_buffer.getvalue()

        with open(fn, "w", encoding="utf8") as file_handle:
            file_handle.write(csv_data)

        with open(afn, "w", encoding="utf8") as file_handle:
            file_handle.write(
                protocolSwap(csv_data, protocol=protocol, altprotocol=altprotocol)
            )


def jsoncounts(page: str) -> str:
    counts: Dict[str, Any] = sdotermsource.SdoTermSource.termCounts()
    counts["schemaorgversion"] = schemaversion.getVersion()
    return json.dumps(sort_dict(counts))


def jsonpcounts(page: str) -> str:
    content: str = """
    COUNTS = '%s';

    insertschemacounts ( COUNTS );
    """ % jsoncounts(page)
    return content


def exportshex_shacl(page: str) -> None:
    release_dir: Path = Path.cwd() / schemaglobals.RELEASE_DIR / schemaversion.getVersion()
    shex_shacl_shapes_exporter.generate_files(
        term_defs_path=release_dir / "schemaorg-all-http.nt",
        outputdir=release_dir,
        outputfileprefix="schemaorg-",
    )


def examples(page: str) -> str:
    return str(schemaexamples.SchemaExamples.allExamplesSerialised())


FILELIST: Dict[str, Tuple[Any, List[str]]] = {
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


def buildFiles(files: List[str]) -> None:
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
            if p in sorted(FILELIST.keys()):
                entry: Optional[Tuple[Any, List[str]]] = FILELIST.get(p, None)
                if entry:
                    func, filenames = entry
                    content: Any = func(p)
                    if content:
                        for filename in filenames:
                            if not filename:
                                continue
                            fn: str = absoluteFilePath(filename)
                            with open(fn, "w", encoding="utf8") as handle:
                                handle.write(str(content))
            else:
                log.warning("Unknown files name: %s" % p)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    buildFiles(sys.argv[1:])
