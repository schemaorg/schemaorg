#!/usr/bin/env python3
"""Generate schema.org release artifacts and website supporting files."""

from __future__ import annotations

import argparse
import csv
import io
import json
import logging
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence
from urllib.parse import ParseResult, urlparse

import rdflib
from rdflib.compare import to_canonical_graph
import rdflib.namespace

from schemaorg import constants
from schemaorg.layout import (
    Domain,
    InputLayout,
    Issues,
    NEXT_VERSION,
    OutputLayout,
    Releases,
)
from schemaorg.layout.releases import VersionRef
from schemaorg.sdo_uri import SCHEMA_URL, SDO, SdoUri
from schemaorg.version import Version, VersionItem
import SchemaExamples.schemaexamples as schemaexamples
import SchemaTerms.localmarkdown as localmarkdown
import SchemaTerms.sdoterm as sdoterm
import SchemaTerms.sdotermsource as sdotermsource
import scripts.shex_shacl_shapes_exporter as shex_shacl_shapes_exporter
import util.buildocspages as buildocspages
import util.fileutils as fileutils
import util.paths as paths
import util.pretty_logger as pretty_logger
import util.schema as schema
import util.sdojsonldcontext as sdojsonldcontext
from util.sdoowl import OwlBuild
from util.sort_dict import sort_dict, sort_xml

log: logging.Logger = logging.getLogger(__name__)

RELEASE_TARGETS: tuple[str, ...] = (
    "RDFExports",
    "CSVExports",
    "Context",
    "Owl",
    "Httpequivs",
    "Shex_Shacl",
    "Examples",
)
SITE_DOC_TARGETS: tuple[str, ...] = (
    "Context",
    "Tree",
    "jsoncounts",
    "jsonpcounts",
    "Owl",
    "Sitemap",
)

_active_input_layout: InputLayout | None = None
_active_output_layout: OutputLayout | None = None
_active_version_obj: Version | None = None
_active_target_version: VersionItem | None = None


def _current_output_layout() -> OutputLayout:
    return _active_output_layout or paths.DefaultOutputLayout()


def _current_releases() -> Releases:
    return Releases(
        _current_output_layout(), _active_version_obj or schema.VERSION
    )


def _current_target_version() -> VersionItem:
    return _active_target_version or schema.target_version()


def buildTurtleEquivs() -> str:
    """Build equivalences between http and https versions of schema.org terms."""
    http_sdo = rdflib.Namespace(SCHEMA_URL._replace(scheme="http").geturl())
    out_graph = rdflib.Graph()
    out_graph.bind("schema_p", http_sdo)
    out_graph.bind("schema_s", SDO)
    out_graph.bind("owl", rdflib.namespace.OWL)

    all_terms = sdotermsource.SdoTermSource.getAllTerms(expanded=True)
    for t in all_terms:
        # getAllTerms() also yields foreign nodes typed with a schema.org class
        # (e.g. the ELI dataset Organization); only schema.org terms have equivalents.
        if (
            isinstance(t, sdoterm.SdoTerm)
            and not t.retired
            and SdoUri(t.id).is_sdo()
        ):
            eqiv = (
                rdflib.namespace.OWL.equivalentProperty
                if t.termType == sdoterm.SdoTermType.PROPERTY
                else rdflib.namespace.OWL.equivalentClass
            )
            p_uri = http_sdo[t.id]
            s_uri = SDO[t.id]
            out_graph.add((p_uri, eqiv, s_uri))
            out_graph.add((s_uri, eqiv, p_uri))

    return str(
        out_graph.serialize(format="turtle", auto_compact=True, sort_keys=True)
    )


def jsonldcontext(page: str) -> str:
    return str(sdojsonldcontext.getContext())


jsonldtree = buildocspages.jsonldtree


def httpequivs(page: str) -> str:
    return buildTurtleEquivs()


def owl(page: str) -> str:
    return str(OwlBuild(version=_current_target_version()).getContent())


def sitemap(page: str, version: VersionItem | None = None) -> str:
    target = version or _current_target_version()
    version_date = target.date()
    lastmod = f"   <lastmod>{version_date}</lastmod>\n" if version_date else ""

    def node(t: str) -> str:
        return f" <url>\n   <loc>{constants.SCHEMA_URI}{t}</loc>\n{lastmod} </url>\n"

    static_pages = (
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
    )

    output: list[str] = [
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    ]
    terms = sdotermsource.SdoTermSource.getAllTerms(suppressSourceLinks=True)
    for term in sorted(map(str, terms)):
        if SdoUri(term).is_sdo():
            output.append(node(term))
    for p in static_pages:
        output.append(node(p))
    output.append("</urlset>\n")
    return "".join(output)


def protocolSwap(content: str, protocol: str, altprotocol: str) -> str:
    extensions = ("attic", "auto", "bib", "health-lifesci", "meta", "pending")
    ret = content
    for layer in ("core", *extensions):
        root: ParseResult = urlparse(str(SdoUri.for_layer(layer)))
        ret = ret.replace(
            root._replace(scheme=protocol).geturl(),
            root._replace(scheme=altprotocol).geturl(),
        )
    return ret


def protocols() -> tuple[str, str]:
    """Return the protocols (http, https) in order of priority."""
    return ("https", "http") if SCHEMA_URL.scheme == "https" else ("http", "https")


ALL_GRAPH: rdflib.Graph | None = None
CURRENT_GRAPH: rdflib.Graph | None = None


def exportrdf(exportType: str, subdirectory_path: str | None = None) -> None:
    global ALL_GRAPH, CURRENT_GRAPH

    if ALL_GRAPH is None:
        ALL_GRAPH = rdflib.Graph()
        ALL_GRAPH.bind("schema", SDO)
        sdotermsource.bindNameSpaces(ALL_GRAPH)

        CURRENT_GRAPH = rdflib.Graph()
        sdotermsource.bindNameSpaces(CURRENT_GRAPH)
        CURRENT_GRAPH.bind("schema", SDO)

        ALL_GRAPH += sdotermsource.SdoTermSource.sourceGraph()
        protocol, _ = protocols()
        sdo_origin = SCHEMA_URL._replace(path="").geturl()

        ALL_GRAPH.update(
            "DELETE {?s ?p ?o} WHERE { ?s ?p ?o. "
            f'FILTER (!regex(str(?s), "^{protocol}://([\\\\w-]+\\\\.)?schema\\\\.org")). }}'
        )

        insert_foreign_types = f"""
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        INSERT {{ ?classNode a rdfs:Class . ?propNode a rdf:Property . }}
        WHERE {{
            {{ {{ ?s rdfs:subClassOf ?classNode }} UNION {{ ?s owl:equivalentClass ?classNode }}
                FILTER (isURI(?classNode) && ?classNode != rdfs:Class && ?classNode != owl:Class && ?classNode != rdf:Property && !strstarts(str(?classNode), "{sdo_origin}"))
            }} UNION
            {{ {{ ?s rdfs:subPropertyOf ?propNode }} UNION {{ ?s owl:equivalentProperty ?propNode }}
                FILTER (isURI(?propNode) && ?propNode != rdf:Property && ?propNode != owl:ObjectProperty && ?propNode != owl:DatatypeProperty && !strstarts(str(?propNode), "{sdo_origin}"))
            }}
        }}"""
        ALL_GRAPH.update(insert_foreign_types)

        assert CURRENT_GRAPH is not None
        CURRENT_GRAPH += ALL_GRAPH
        CURRENT_GRAPH.update(
            f"PREFIX schema: <{constants.SCHEMA_URI}> "
            f"DELETE {{?s ?p ?o}} WHERE {{ ?s ?p ?o; schema:isPartOf <{SdoUri.for_layer('attic')}>. }}"
        )

    formats = ("json-ld", "turtle", "nt", "nquads", "rdf")
    if exportType == "RDFExports":
        for fmt in sorted(formats):
            assert ALL_GRAPH is not None
            assert CURRENT_GRAPH is not None
            _exportrdf(fmt, ALL_GRAPH, CURRENT_GRAPH, subdirectory_path)
    elif (extype := exportType.removeprefix("RDFExport.")) in formats:
        assert ALL_GRAPH is not None
        assert CURRENT_GRAPH is not None
        _exportrdf(extype, ALL_GRAPH, CURRENT_GRAPH, subdirectory_path)
    else:
        raise ValueError(f"Unknown export format: {exportType}")


def get_release_file_path(
    selector: fileutils.FileSelector | str,
    protocol: str,
    output_format: str,
    suffix: str | None = None,
    subdirectory_path: str | None = None,
) -> Path:
    extension = fileutils.EXTENSIONS_FOR_FORMAT[output_format.lower()]
    parts = [str(selector).lower(), protocol.lower()]
    if suffix:
        parts.append(suffix)
    merged = "-".join(parts)
    filename = f"schemaorg-{merged}.{extension}"

    if subdirectory_path is not None:
        return _current_output_layout().file(
            paths.Domain.ROOT, f"{subdirectory_path}/{filename}"
        )
    return _current_releases().file(
        _current_target_version(), filename=filename
    )


def _exportrdf(
    output_format: str,
    all_graph: rdflib.Graph,
    current_graph: rdflib.Graph,
    subdirectory_path: str | None = None,
) -> None:
    protocol, altprotocol = protocols()
    version = _current_target_version().number()

    for selector in fileutils.FILESET_SELECTORS:
        g = all_graph if fileutils.isAll(selector) else current_graph
        ns_mgr = g.namespace_manager
        g_can: rdflib.Graph = to_canonical_graph(g)
        g_can.namespace_manager = ns_mgr

        if output_format == "rdf":
            g_out = rdflib.Graph()
            g_out.namespace_manager = ns_mgr

            def type_sort_key(trip: tuple[Any, Any, Any]) -> tuple[int, str, str]:
                s, p, o = trip
                if p == rdflib.RDF.type:
                    if o == rdflib.RDFS.Class:
                        return (0, str(s), str(o))
                    return (1, str(s), str(o))
                return (2, str(s), str(p))

            for t in sorted(g_can, key=type_sort_key):
                g_out.add(t)
            g_can = g_out

        for p in fileutils.FILESET_PROTOCOLS:
            final_g: rdflib.Graph | rdflib.Dataset = g_can
            if output_format == "nquads":
                ds = rdflib.Dataset()
                qg = ds.graph(
                    rdflib.URIRef(f"{SCHEMA_URL._replace(scheme=p).geturl()}{version}")
                )
                for trip in g_can:
                    qg.add(trip)
                final_g = ds

            fn = get_release_file_path(
                selector=selector,
                protocol=p,
                output_format=output_format,
                subdirectory_path=subdirectory_path,
            )
            with pretty_logger.BlockLog(logger=log, message=f"Exporting {fn}"):
                fmt = "pretty-xml" if output_format == "rdf" else output_format
                out = str(
                    final_g.serialize(
                        format=fmt, auto_compact=True, sort_keys=True, max_depth=1
                    )
                )

                if output_format in ("nt", "nquads"):
                    out = (
                        "\n".join(
                            sorted(
                                line.rstrip()
                                for line in out.splitlines()
                                if line.strip()
                            )
                        )
                        + "\n"
                    )
                elif output_format == "rdf":
                    try:
                        out = sort_xml(out)
                    except Exception as e:
                        log.warning("Failed to sort RDF XML: %s", e)
                elif output_format == "json-ld":
                    try:
                        out = json.dumps(sort_dict(json.loads(out)), indent=2)
                    except Exception as e:
                        log.warning("Failed to sort JSON-LD: %s", e)

                content = (
                    protocolSwap(out, protocol, altprotocol)
                    if p != protocol
                    else out
                )
                fn.write_text(content, encoding="utf-8")


def uriwrap(thing: Any) -> str:
    """Convert various types into uris. Sorts items if they are a list."""
    if not thing:
        return ""
    if isinstance(thing, str):
        return str(SdoUri(thing))
    if isinstance(
        thing, (sdoterm.SdoTermSequence, sdoterm.SdoTermOrId, sdoterm.SdoTerm)
    ):
        return uriwrap(getattr(thing, "ids", getattr(thing, "id", None)))
    try:
        return ", ".join(sorted(map(uriwrap, thing)))
    except (TypeError, ValueError) as e:
        log.error("Cannot uriwrap %s: %s", thing, e)
        return ""


def exportcsv(page: str) -> None:
    protocol, altprotocol = protocols()
    type_fields = [
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
    prop_fields = [
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

    typedata: list[dict[str, str]] = []
    typedata_all: list[dict[str, str]] = []
    propdata: list[dict[str, str]] = []
    propdata_all: list[dict[str, str]] = []
    terms = sdotermsource.SdoTermSource.getAllTerms(
        expanded=True, suppressSourceLinks=True
    )

    for term in terms:
        if (
            not isinstance(term, sdoterm.SdoTerm)
            or term.termType == sdoterm.SdoTermType.REFERENCE
            or not SdoUri(term.id).is_sdo()
        ):
            continue

        row: dict[str, str] = {
            "id": term.uri,
            "label": term.label,
            "comment": term.comment,
            "supersedes": uriwrap(term.supersedes),
            "supersededBy": uriwrap(term.supersededBy),
            "isPartOf": sdotermsource.uriFromLayer(term.extLayer)
            if term.extLayer
            else "",
        }

        if term.termType == sdoterm.SdoTermType.PROPERTY:
            row.update(
                {
                    "subPropertyOf": uriwrap(term.supers),
                    "equivalentProperty": uriwrap(term.equivalents.ids),
                    "subproperties": uriwrap(term.subs.ids),
                    "domainIncludes": uriwrap(term.domainIncludes.ids),
                    "rangeIncludes": uriwrap(term.rangeIncludes.ids),
                    "inverseOf": uriwrap(term.inverse.id),
                }
            )
            propdata_all.append(row)
            if not term.retired:
                propdata.append(row)
        else:
            row.update(
                {
                    "subTypeOf": uriwrap(term.supers.ids),
                    "equivalentClass": uriwrap(term.equivalents.ids),
                    "subTypes": uriwrap(term.subs.ids),
                }
            )
            if term.termType == sdoterm.SdoTermType.ENUMERATIONVALUE:
                row["enumerationtype"] = uriwrap(term.enumerationParent.id)
            else:
                row["properties"] = uriwrap(term.allproperties.ids)
            typedata_all.append(row)
            if not term.retired:
                typedata.append(row)

    writecsvout(
        "properties", propdata, prop_fields, fileutils.FileSelector.CURRENT, protocol, altprotocol
    )
    writecsvout(
        "properties", propdata_all, prop_fields, fileutils.FileSelector.ALL, protocol, altprotocol
    )
    writecsvout(
        "types", typedata, type_fields, fileutils.FileSelector.CURRENT, protocol, altprotocol
    )
    writecsvout(
        "types", typedata_all, type_fields, fileutils.FileSelector.ALL, protocol, altprotocol
    )


def writecsvout(
    ftype: str,
    data: Sequence[dict[str, str]],
    fields: Sequence[str],
    selector: fileutils.FileSelector | str,
    protocol: str,
    altprotocol: str,
) -> None:
    paths_list = [
        get_release_file_path(
            selector=selector, protocol=p, suffix=ftype, output_format="csv"
        )
        for p in (protocol, altprotocol)
    ]

    with pretty_logger.BlockLog(
        message=f"Preparing files {ftype}: {paths_list[0]} and {paths_list[1]}.",
        logger=log,
    ):
        with io.StringIO() as buffer:
            writer = csv.DictWriter(
                buffer, fieldnames=fields, quoting=csv.QUOTE_ALL, lineterminator="\n"
            )
            writer.writeheader()
            writer.writerows(data)
            csv_data = buffer.getvalue()

        paths_list[0].write_text(csv_data, encoding="utf-8")
        paths_list[1].write_text(
            protocolSwap(csv_data, protocol, altprotocol), encoding="utf-8"
        )


def jsoncounts(page: str) -> str:
    counts = dict(sdotermsource.SdoTermSource.termCounts())
    counts["schemaorgversion"] = _current_target_version().number()
    return json.dumps(sort_dict(counts))


def jsonpcounts(page: str) -> str:
    return f"\n    COUNTS = '{jsoncounts(page)}';\n\n    insertschemacounts ( COUNTS );\n    "


def exportshex_shacl(page: str) -> None:
    version = _current_target_version().number()
    nt_path = get_release_file_path(
        selector=fileutils.FileSelector.ALL,
        protocol="http",
        output_format="nt",
    )

    if not nt_path.exists():
        log.info("Generating missing %s for Shex_Shacl", nt_path)
        assert ALL_GRAPH is not None
        _exportrdf("nt", ALL_GRAPH, CURRENT_GRAPH or ALL_GRAPH)

    shex_shacl_shapes_exporter.generate_files(
        term_defs_path=nt_path,
        version=version,
        releases=_current_releases(),
    )


def examples(page: str) -> str:
    if _active_input_layout is not None:
        example_files = Issues(_active_input_layout).get_example_files()
        loaded = schemaexamples.SchemaExamples.from_files(example_files)
    else:
        loaded = schemaexamples.SchemaExamples.from_default()
    return "\n".join(ex.serialize() for ex in loaded.allExamples())


FILELIST: dict[str, tuple[Callable[[str], Any], list[tuple[Any, ...]]]] = {
    "Context": (
        jsonldcontext,
        [
            ("file", paths.Domain.DOCS, "jsonldcontext.jsonld"),
            ("file", paths.Domain.DOCS, "jsonldcontext.json"),
            ("file", paths.Domain.DOCS, "jsonldcontext.json.txt"),
            ("file", paths.Domain.RELEASE, "schemaorgcontext.jsonld"),
        ],
    ),
    "Tree": (jsonldtree, [("file", paths.Domain.DOCS, "tree.jsonld")]),
    "jsoncounts": (jsoncounts, [("file", paths.Domain.DOCS, "jsoncounts.json")]),
    "jsonpcounts": (jsonpcounts, [("file", paths.Domain.DOCS, "jsonpcounts.js")]),
    "Owl": (
        owl,
        [
            ("file", paths.Domain.DOCS, "schemaorg.owl"),
            ("file", paths.Domain.RELEASE, "schemaorg.owl"),
        ],
    ),
    "Httpequivs": (httpequivs, [("file", paths.Domain.RELEASE, "httpequivs.ttl")]),
    "Sitemap": (sitemap, [("file", paths.Domain.DOCS, "sitemap.xml")]),
    "RDFExports": (exportrdf, []),
    "RDFExport.turtle": (exportrdf, []),
    "RDFExport.rdf": (exportrdf, []),
    "RDFExport.nt": (exportrdf, []),
    "RDFExport.nquads": (exportrdf, []),
    "RDFExport.json-ld": (exportrdf, []),
    "Shex_Shacl": (exportshex_shacl, []),
    "CSVExports": (exportcsv, []),
    "Examples": (
        examples,
        [("file", paths.Domain.RELEASE, "schemaorg-all-examples.txt")],
    ),
}


def buildFiles(
    files: Iterable[str],
    domains: frozenset[paths.Domain] | None = None,
) -> None:
    localmarkdown.MarkdownTool.setWikilinkCssClass("localLink")
    localmarkdown.MarkdownTool.setWikilinkPrePath(constants.SCHEMA_URI)
    localmarkdown.MarkdownTool.setWikilinkPostPath("")

    targets = (
        sorted(FILELIST.keys())
        if any(fileutils.isAll(f) for f in files)
        else list(files)
    )

    process_files = list(dict.fromkeys(targets))
    seen = set(process_files)

    if "Shex_Shacl" in seen:
        if "RDFExport.nt" not in seen and "RDFExports" not in seen:
            process_files.insert(0, "RDFExport.nt")
        process_files.remove("Shex_Shacl")
        process_files.append("Shex_Shacl")

    if "RDFExports" in seen and "RDFExport.nt" in seen:
        process_files.remove("RDFExport.nt")
        process_files.insert(0, "RDFExport.nt")

    output_layout = _current_output_layout()
    releases = _current_releases()
    target_version = _current_target_version()

    for p in process_files:
        if entry := FILELIST.get(p):
            func, filenames = entry
            filtered = [
                (kind, domain, filename)
                for kind, domain, filename in filenames
                if domains is None or domain in domains
            ]
            if filenames and not filtered:
                continue
            with pretty_logger.BlockLog(message=f"Preparing file {p}.", logger=log):
                content = func(p)
                if content is not None:
                    for _, domain, filename in filtered:
                        if domain == paths.Domain.RELEASE:
                            out_path = releases.file(target_version, filename=filename)
                        else:
                            out_path = output_layout.file(domain, filename)
                        out_path.write_text(str(content), encoding="utf-8")
        else:
            log.warning("Unknown files name: %s", p)


def export_release_files(
    input_layout: InputLayout,
    output_layout: OutputLayout,
    version: VersionRef = NEXT_VERSION,
) -> None:
    """Load source TTLs and write all 35 schema release files."""
    global ALL_GRAPH, CURRENT_GRAPH
    global _active_input_layout, _active_output_layout
    global _active_version_obj, _active_target_version

    version_obj = Version(input_layout.file(Domain.ROOT, constants.VERSIONS_FILE))
    target_version = version_obj.resolve(version)
    releases = Releases(output_layout, version_obj)
    target_dir = releases.dir(target_version)
    if target_dir.is_dir():
        for existing in target_dir.iterdir():
            if existing.is_file():
                existing.unlink()

    ALL_GRAPH = None
    CURRENT_GRAPH = None
    sdojsonldcontext.CONTEXT = None
    sdotermsource.SdoTermSource.loadSourceGraph(
        files=Issues(input_layout).get_ttl_files(), init=True
    )

    _active_input_layout = input_layout
    _active_output_layout = output_layout
    _active_version_obj = version_obj
    _active_target_version = target_version
    try:
        buildFiles(
            RELEASE_TARGETS,
            domains=frozenset({paths.Domain.RELEASE}),
        )
    finally:
        _active_input_layout = None
        _active_output_layout = None
        _active_version_obj = None
        _active_target_version = None


def export_site_docs(
    input_layout: InputLayout,
    output_layout: OutputLayout,
    version: VersionRef = NEXT_VERSION,
) -> None:
    """Load target release TTL and write Domain.DOCS supporting files."""
    global _active_input_layout, _active_output_layout
    global _active_version_obj, _active_target_version

    version_obj = Version(input_layout.file(Domain.ROOT, constants.VERSIONS_FILE))
    target_version = version_obj.resolve(version)
    ttl_files = Releases(input_layout, version_obj).get_ttl_files(target_version)

    sdojsonldcontext.CONTEXT = None
    sdotermsource.SdoTermSource.loadSourceGraph(files=ttl_files, init=True)
    sdotermsource.bindNameSpaces(sdotermsource.SdoTermSource.sourceGraph())

    _active_input_layout = input_layout
    _active_output_layout = output_layout
    _active_version_obj = version_obj
    _active_target_version = target_version
    try:
        buildFiles(
            SITE_DOC_TARGETS,
            domains=frozenset({paths.Domain.DOCS}),
        )
    finally:
        _active_input_layout = None
        _active_output_layout = None
        _active_version_obj = None
        _active_target_version = None


def main(argv: Sequence[str] | None = None) -> None:
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input-dir",
        type=Path,
        default=constants.PROJECT_ROOT,
        help="Root directory of the schema.org input layout.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=constants.PROJECT_ROOT / "data",
        help="Root directory containing the releases/ output directory.",
    )
    parser.add_argument(
        "--version",
        default=NEXT_VERSION,
        help="Target release version ('next', 'latest', or declared X.Y).",
    )
    args = parser.parse_args(argv)
    export_release_files(
        InputLayout(args.input_dir),
        OutputLayout(args.output_dir),
        version=args.version,
    )


if __name__ == "__main__":
    main()
