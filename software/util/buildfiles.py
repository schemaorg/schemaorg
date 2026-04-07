#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import csv
import io
import json
import logging
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, Set, Callable, Iterable, Sequence

import rdflib
import rdflib.namespace
from rdflib.compare import to_canonical_graph

if Path.cwd() not in [Path(p).resolve() for p in sys.path]:
    sys.path.insert(1, str(Path.cwd()))

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
import software.SchemaTerms.localmarkdown as localmarkdown
import software.SchemaExamples.schemaexamples as schemaexamples
from software.util.sort_dict import sort_dict, sort_xml

VOCABURI: str = sdotermsource.SdoTermSource.vocabUri()
log: logging.Logger = logging.getLogger(__name__)


def buildTurtleEquivs() -> str:
    """Build equivalences between http and https versions of schema.org terms."""
    s_p: str = "http://schema.org/"
    s_s: str = "https://schema.org/"
    outGraph: rdflib.Graph = rdflib.Graph()
    outGraph.bind("schema_p", s_p)
    outGraph.bind("schema_s", s_s)
    outGraph.bind("owl", rdflib.namespace.OWL)

    all_terms: Sequence[Union[str, sdoterm.SdoTerm]] = sdotermsource.SdoTermSource.getAllTerms(expanded=True)
    t: Union[str, sdoterm.SdoTerm]
    for t in all_terms:
        if isinstance(t, sdoterm.SdoTerm) and not t.retired:
            eqiv: rdflib.URIRef = rdflib.namespace.OWL.equivalentClass
            if t.termType == sdoterm.SdoTermType.PROPERTY:
                eqiv = rdflib.namespace.OWL.equivalentProperty

            p_uri: rdflib.URIRef = rdflib.URIRef(f"{s_p}{t.id}")
            s_uri: rdflib.URIRef = rdflib.URIRef(f"{s_s}{t.id}")
            outGraph.add((p_uri, eqiv, s_uri))
            outGraph.add((s_uri, eqiv, p_uri))

    return str(outGraph.serialize(format="turtle", auto_compact=True, sort_keys=True))


def absoluteFilePath(fn: str) -> str:
    path: Path = Path(schemaglobals.OUTPUTDIR) / fn
    fileutils.checkFilePath(path.parent)
    return str(path)


def jsonldcontext(page: str) -> str:
    return str(sdojsonldcontext.getContext())


def jsonldtree(page: str) -> str:
    context: Dict[str, Any] = {
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "schema": "https://schema.org",
        "rdfs:subClassOf": {"@type": "@id"},
        "description": "rdfs:comment",
        "children": {"@reverse": "rdfs:subClassOf"}
    }
    data: Dict[str, Any] = _jsonldtree("Thing", visitset=set(), term={"@context": context})
    return json.dumps(sort_dict(data), indent=3)


def _jsonldtree(tid: str, visitset: Set[str], term: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    termdesc: Optional[sdoterm.SdoTerm] = sdotermsource.SdoTermSource.getTerm(tid)
    if not termdesc:
        return term or {}

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
            term_dict["children"] = [_jsonldtree(sub, visitset) for sub in termdesc.subs.ids]
    return term_dict


def httpequivs(page: str) -> str:
    return buildTurtleEquivs()


def owl(page: str) -> str:
    from software.util.sdoowl import OwlBuild
    return str(OwlBuild().getContent())


def sitemap(page: str) -> str:
    version_date: str = str(schemaversion.getCurrentVersionDate() or "")
    def node(t: str) -> str:
        return f""" <url>
   <loc>https://schema.org/{t}</loc>
   <lastmod>{version_date}</lastmod>
 </url>
"""
    STATICPAGES: List[str] = [
        "docs/schemas.html", "docs/full.html", "docs/gs.html", "docs/about.html",
        "docs/howwework.html", "docs/releases.html", "docs/faq.html",
        "docs/datamodel.html", "docs/developers.html", "docs/extension.html",
        "docs/meddocs.html", "docs/hotels.html",
    ]

    output: List[str] = ['<?xml version="1.0" encoding="utf-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n']
    terms: Sequence[Union[str, sdoterm.SdoTerm]] = sdotermsource.SdoTermSource.getAllTerms(suppressSourceLinks=True)
    term: Union[str, sdoterm.SdoTerm]
    for term in sorted(map(str, terms)):
        if not term.startswith(("http://", "https://")):
            output.append(node(term))
    p: str
    for p in STATICPAGES:
        output.append(node(p))
    output.append("</urlset>\n")
    return "".join(output)


def protocolSwap(content: str, protocol: str, altprotocol: str) -> str:
    ret: str = content.replace(f"{protocol}://schema.org", f"{altprotocol}://schema.org")
    extensions: List[str] = ["attic", "auto", "bib", "health-lifesci", "meta", "pending"]
    ext: str
    for ext in extensions:
        ret = ret.replace(f"{protocol}://{ext}.schema.org", f"{altprotocol}://{ext}.schema.org")
    return ret


def protocols() -> Tuple[str, str]:
    """Return the protocols (http, https) in order of priority."""
    return ("https", "http") if sdotermsource.SdoTermSource.vocabUri().startswith("https") else ("http", "https")


ALL_GRAPH: Optional[rdflib.Graph] = None
CURRENT_GRAPH: Optional[rdflib.Graph] = None


def exportrdf(exportType: str, subdirectory_path: Optional[str] = None) -> None:
    global ALL_GRAPH, CURRENT_GRAPH

    if not ALL_GRAPH:
        ALL_GRAPH = rdflib.Graph()
        ALL_GRAPH.bind("schema", VOCABURI)
        sdotermsource.bindNameSpaces(ALL_GRAPH)

        CURRENT_GRAPH = rdflib.Graph()
        sdotermsource.bindNameSpaces(CURRENT_GRAPH)
        CURRENT_GRAPH.bind("schema", VOCABURI)

        ALL_GRAPH += sdotermsource.SdoTermSource.sourceGraph()
        protocol: str
        protocol, _ = protocols()

        log.debug("Cleanup non schema org things.")
        ALL_GRAPH.update(f'DELETE {{?s ?p ?o}} WHERE {{ ?s ?p ?o. FILTER (! strstarts(str(?s), "{protocol}://schema.org") ). }}')

        log.debug("Generate Foreign types – SPARQL INSERT")
        insert_foreign_types: str = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        INSERT {{ ?classNode a rdfs:Class . ?propNode a rdf:Property . }}
        WHERE {{
            {{ {{ ?s rdfs:subClassOf ?classNode }} UNION {{ ?s owl:equivalentClass ?classNode }}
                FILTER (isURI(?classNode) && ?classNode != rdfs:Class && ?classNode != owl:Class && ?classNode != rdf:Property && !strstarts(str(?classNode), "{protocol}://schema.org"))
            }} UNION
            {{ {{ ?s rdfs:subPropertyOf ?propNode }} UNION {{ ?s owl:equivalentProperty ?propNode }}
                FILTER (isURI(?propNode) && ?propNode != rdf:Property && ?propNode != owl:ObjectProperty && ?propNode != owl:DatatypeProperty && !strstarts(str(?propNode), "{protocol}://schema.org"))
            }}
        }}"""
        ALL_GRAPH.update(insert_foreign_types)

        log.debug("Merge")
        assert CURRENT_GRAPH is not None
        CURRENT_GRAPH += ALL_GRAPH

        log.debug("Delete items from the attic")
        CURRENT_GRAPH.update(f'PREFIX schema: <{protocol}://schema.org/> DELETE {{?s ?p ?o}} WHERE{{ ?s ?p ?o; schema:isPartOf <{protocol}://attic.schema.org>. }}')

    formats: List[str] = ["json-ld", "turtle", "nt", "nquads", "rdf"]
    if exportType == "RDFExports":
        fmt: str
        for fmt in sorted(formats):
            assert ALL_GRAPH is not None
            assert CURRENT_GRAPH is not None
            _exportrdf(fmt, ALL_GRAPH, CURRENT_GRAPH, subdirectory_path)
    elif (extype := exportType[len("RDFExport."):]) in formats:
        assert ALL_GRAPH is not None
        assert CURRENT_GRAPH is not None
        _exportrdf(extype, ALL_GRAPH, CURRENT_GRAPH, subdirectory_path)
    else:
        raise ValueError(f"Unknown export format: {exportType}")


def _exportrdf(output_format: str, all_graph: rdflib.Graph, current_graph: rdflib.Graph, subdirectory_path: Optional[str] = None) -> None:
    protocol: str
    altprotocol: str
    protocol, altprotocol = protocols()
    version: str = schemaversion.getVersion()

    selector: str
    for selector in fileutils.FILESET_SELECTORS:
        g: rdflib.Graph = all_graph if fileutils.isAll(selector) else current_graph
        ns_mgr: rdflib.namespace.NamespaceManager = g.namespace_manager
        g_can: rdflib.Graph = to_canonical_graph(g)
        g_can.namespace_manager = ns_mgr

        p: str
        for p in fileutils.FILESET_PROTOCOLS:
            final_g: Union[rdflib.Graph, rdflib.Dataset] = g_can
            if output_format == "nquads":
                ds: rdflib.Dataset = rdflib.Dataset()
                qg: rdflib.Graph = ds.graph(rdflib.URIRef(f"{p}://schema.org/{version}"))
                trip: Tuple[rdflib.term.Node, rdflib.term.Node, rdflib.term.Node]
                for trip in g_can:
                    qg.add(trip)
                final_g = ds

            fn: str = fileutils.releaseFilePath(
                output_dir=schemaglobals.getOutputDir(),
                version=version,
                selector=selector,
                protocol=p,
                output_format=output_format,
                subdirectory_path=subdirectory_path,
            )
            with pretty_logger.BlockLog(logger=log, message=f"Exporting {fn}"):
                fmt: str = "pretty-xml" if output_format == "rdf" else output_format
                out: str = str(final_g.serialize(format=fmt, auto_compact=True, sort_keys=True, max_depth=1))

                if output_format in ("nt", "nquads"):
                    out = "\n".join(sorted(line.rstrip() for line in out.splitlines() if line.strip())) + "\n"
                elif output_format == "rdf":
                    try:
                        out = sort_xml(out)
                    except Exception as e:
                        log.warning(f"Failed to sort RDF XML: {e}")
                elif output_format == "json-ld":
                    try:
                        out = json.dumps(sort_dict(json.loads(out)), indent=2)
                    except Exception as e:
                        log.warning(f"Failed to sort JSON-LD: {e}")

                content: str = out
                if p != protocol:
                    content = protocolSwap(out, protocol, altprotocol)

                Path(fn).write_text(content, encoding="utf8")


def array2str(values: List[str]) -> str:
    return ", ".join(values) if values else ""


def uriwrap(thing: Any) -> str:
    """Convert various types into uris. Sorts items if they are a list."""
    if not thing:
        return ""
    if isinstance(thing, str):
        return thing if thing.startswith(("http:", "https:")) else f"{VOCABURI}{thing}"
    if isinstance(thing, (sdoterm.SdoTermSequence, sdoterm.SdoTermOrId, sdoterm.SdoTerm)):
        return uriwrap(getattr(thing, "ids", getattr(thing, "id", None)))
    try:
        return array2str(sorted(map(uriwrap, thing)))
    except (TypeError, ValueError) as e:
        log.fatal(f"Cannot uriwrap {thing}:{e}")
        return ""


def exportcsv(page: str) -> None:
    protocol: str
    altprotocol: str
    protocol, altprotocol = protocols()
    type_fields: List[str] = ["id", "label", "comment", "subTypeOf", "enumerationtype", "equivalentClass", "properties", "subTypes", "supersedes", "supersededBy", "isPartOf"]
    prop_fields: List[str] = ["id", "label", "comment", "subPropertyOf", "equivalentProperty", "subproperties", "domainIncludes", "rangeIncludes", "inverseOf", "supersedes", "supersededBy", "isPartOf"]

    typedata: List[Dict[str, str]] = []
    typedata_all: List[Dict[str, str]] = []
    propdata: List[Dict[str, str]] = []
    propdata_all: List[Dict[str, str]] = []
    terms: Sequence[Union[str, sdoterm.SdoTerm]] = sdotermsource.SdoTermSource.getAllTerms(expanded=True, suppressSourceLinks=True)

    term: Union[str, sdoterm.SdoTerm]
    for term in terms:
        if not isinstance(term, sdoterm.SdoTerm) or term.termType == sdoterm.SdoTermType.REFERENCE or term.id.startswith(("http://", "https://")):
            continue

        row: Dict[str, str] = {
            "id": term.uri, "label": term.label, "comment": term.comment,
            "supersedes": uriwrap(term.supersedes), "supersededBy": uriwrap(term.supersededBy),
            "isPartOf": f"{protocol}://{term.extLayer}.schema.org" if term.extLayer else ""
        }

        if term.termType == sdoterm.SdoTermType.PROPERTY:
            row.update({
                "subPropertyOf": uriwrap(term.supers), "equivalentProperty": uriwrap(term.equivalents.ids),
                "subproperties": uriwrap(term.subs.ids), "domainIncludes": uriwrap(term.domainIncludes.ids),
                "rangeIncludes": uriwrap(term.rangeIncludes.ids), "inverseOf": uriwrap(term.inverse.id)
            })
            propdata_all.append(row)
            if not term.retired: propdata.append(row)
        else:
            row.update({
                "subTypeOf": uriwrap(term.supers.ids), "equivalentClass": uriwrap(term.equivalents.ids),
                "subTypes": uriwrap(term.subs.ids)
            })
            if term.termType == sdoterm.SdoTermType.ENUMERATIONVALUE:
                row["enumerationtype"] = uriwrap(term.enumerationParent.id)
            else:
                row["properties"] = uriwrap(term.allproperties.ids)
            typedata_all.append(row)
            if not term.retired: typedata.append(row)

    writecsvout("properties", propdata, prop_fields, fileutils.FileSelector.CURRENT, protocol, altprotocol)
    writecsvout("properties", propdata_all, prop_fields, fileutils.FileSelector.ALL, protocol, altprotocol)
    writecsvout("types", typedata, type_fields, fileutils.FileSelector.CURRENT, protocol, altprotocol)
    writecsvout("types", typedata_all, type_fields, fileutils.FileSelector.ALL, protocol, altprotocol)


def writecsvout(ftype: str, data: List[Dict[str, str]], fields: List[str], selector: Union[fileutils.FileSelector, str], protocol: str, altprotocol: str) -> None:
    version: str = schemaversion.getVersion()
    paths: List[str] = [fileutils.releaseFilePath(output_dir=schemaglobals.getOutputDir(), version=version, selector=selector, protocol=p, suffix=ftype, output_format="csv") for p in (protocol, altprotocol)]

    with pretty_logger.BlockLog(message=f"Preparing files {ftype}: {paths[0]} and {paths[1]}.", logger=log):
        csv_data: str
        with io.StringIO() as buffer:
            writer: csv.DictWriter = csv.DictWriter(buffer, fieldnames=fields, quoting=csv.QUOTE_ALL, lineterminator="\n")
            writer.writeheader()
            writer.writerows(data)
            csv_data = buffer.getvalue()

        Path(paths[0]).write_text(csv_data, encoding="utf8")
        Path(paths[1]).write_text(protocolSwap(csv_data, protocol, altprotocol), encoding="utf8")


def jsoncounts(page: str) -> str:
    counts: Dict[str, Any] = sdotermsource.SdoTermSource.termCounts()
    counts["schemaorgversion"] = schemaversion.getVersion()
    return json.dumps(sort_dict(counts))


def jsonpcounts(page: str) -> str:
    return f"\n    COUNTS = '{jsoncounts(page)}';\n\n    insertschemacounts ( COUNTS );\n    "


def exportshex_shacl(page: str) -> None:
    version: str = schemaversion.getVersion()
    release_dir: Path = Path.cwd() / schemaglobals.RELEASE_DIR / version
    nt_path: Path = release_dir / "schemaorg-all-http.nt"

    if not nt_path.exists():
        log.info(f"Generating missing {nt_path} for Shex_Shacl")
        assert ALL_GRAPH is not None
        _exportrdf("nt", ALL_GRAPH, CURRENT_GRAPH or ALL_GRAPH)

    shex_shacl_shapes_exporter.generate_files(
        term_defs_path=nt_path,
        outputdir=release_dir,
        outputfileprefix="schemaorg-",
    )


def examples(page: str) -> str:
    return str(schemaexamples.SchemaExamples.allExamplesSerialised())


FILELIST: Dict[str, Tuple[Callable[[str], Any], List[str]]] = {
    "Context": (jsonldcontext, ["docs/jsonldcontext.jsonld", "docs/jsonldcontext.json", "docs/jsonldcontext.json.txt", f"releases/{schemaversion.getVersion()}/schemaorgcontext.jsonld"]),
    "Tree": (jsonldtree, ["docs/tree.jsonld"]),
    "jsoncounts": (jsoncounts, ["docs/jsoncounts.json"]),
    "jsonpcounts": (jsonpcounts, ["docs/jsonpcounts.js"]),
    "Owl": (owl, ["docs/schemaorg.owl", f"releases/{schemaversion.getVersion()}/schemaorg.owl"]),
    "Httpequivs": (httpequivs, [f"releases/{schemaversion.getVersion()}/httpequivs.ttl"]),
    "Sitemap": (sitemap, ["docs/sitemap.xml"]),
    "RDFExports": (exportrdf, [""]),
    "RDFExport.turtle": (exportrdf, [""]),
    "RDFExport.rdf": (exportrdf, [""]),
    "RDFExport.nt": (exportrdf, [""]),
    "RDFExport.nquads": (exportrdf, [""]),
    "RDFExport.json-ld": (exportrdf, [""]),
    "Shex_Shacl": (exportshex_shacl, [""]),
    "CSVExports": (exportcsv, [""]),
    "Examples": (examples, [f"releases/{schemaversion.getVersion()}/schemaorg-all-examples.txt"]),
}


def buildFiles(files: Iterable[str]) -> None:
    software.SchemaTerms.localmarkdown.MarkdownTool.setWikilinkCssClass("localLink")
    software.SchemaTerms.localmarkdown.MarkdownTool.setWikilinkPrePath("https://schema.org/")
    software.SchemaTerms.localmarkdown.MarkdownTool.setWikilinkPostPath("")

    targets: List[str] = sorted(FILELIST.keys()) if any(fileutils.isAll(f) for f in files) else list(files)

    process_files: List[str] = []
    seen: Set[str] = set()
    t: str
    for t in targets:
        if t not in seen:
            process_files.append(t)
            seen.add(t)

    if "Shex_Shacl" in seen:
        if "RDFExport.nt" not in seen and "RDFExports" not in seen:
            process_files.insert(0, "RDFExport.nt")

    if "Shex_Shacl" in seen:
        process_files.remove("Shex_Shacl")
        process_files.append("Shex_Shacl")

    if "RDFExports" in seen and "RDFExport.nt" in seen:
         process_files.remove("RDFExport.nt")
         process_files.insert(0, "RDFExport.nt")

    p: str
    for p in process_files:
        if entry := FILELIST.get(p):
            func: Callable[[str], Any]
            filenames: List[str]
            func, filenames = entry
            with pretty_logger.BlockLog(message=f"Preparing file {p}.", logger=log):
                content: Any = func(p)
                if content:
                    fn: str
                    for fn in filenames:
                        if fn:
                            Path(absoluteFilePath(fn)).write_text(str(content), encoding="utf8")
        else:
            log.warning(f"Unknown files name: {p}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    buildFiles(sys.argv[1:])
