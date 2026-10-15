"""RDF graph renderer (turtle, nt, nquads, rdf/xml, json-ld)."""

from __future__ import annotations

import functools
import json
from typing import Any

import rdflib
from rdflib.compare import to_canonical_graph
from rdflib.namespace import NamespaceManager, XMLNS

from util.sort_dict import sort_dict, sort_xml

RDF_FORMATS: tuple[str, ...] = ("json-ld", "nquads", "nt", "rdf", "turtle")


def _type_sort_key(trip: tuple[Any, Any, Any]) -> tuple[int, str, str]:
    s, p, o = trip
    if p == rdflib.RDF.type:
        return (0 if o == rdflib.RDFS.Class else 1, str(s), str(o))
    return (2, str(s), str(p))


class RdfRenderer:
    """Deterministic serializations of one graph; canonicalizes it once across formats."""

    def __init__(self, graph: rdflib.Graph) -> None:
        self.graph = graph

    @functools.cached_property
    def canonical(self) -> rdflib.Graph:
        g_can: rdflib.Graph = to_canonical_graph(self.graph)
        g_can.namespace_manager = self.graph.namespace_manager
        return g_can

    @functools.cached_property
    def _type_sorted(self) -> rdflib.Graph:
        # rdf/xml lists class declarations first, then other typings, then the rest,
        # and requires the reserved XML namespace bound for @lang literals.
        g_out = rdflib.Graph(bind_namespaces="none")
        ns_mgr = NamespaceManager(g_out, bind_namespaces="none")
        for prefix, uri in self.graph.namespaces():
            ns_mgr.bind(prefix, uri, override=True)
        ns_mgr.bind("xml", XMLNS, override=False)
        g_out.namespace_manager = ns_mgr
        for triple in sorted(self.canonical, key=_type_sort_key):
            g_out.add(triple)
        return g_out

    def render(
        self,
        output_format: str,
        dataset_uri: rdflib.URIRef | None = None,
    ) -> str:
        """Serializes the graph; nquads wraps it in a dataset named dataset_uri."""
        if output_format not in RDF_FORMATS:
            raise ValueError(f"Unknown RDF export format: {output_format}")

        source: rdflib.Graph | rdflib.Dataset = self.canonical
        if output_format == "rdf":
            source = self._type_sorted
        elif output_format == "nquads":
            if dataset_uri is None:
                raise ValueError("nquads export requires a dataset_uri")
            ds = rdflib.Dataset()
            qg = ds.graph(dataset_uri)
            for triple in self.canonical:
                qg.add(triple)
            source = ds

        fmt = "pretty-xml" if output_format == "rdf" else output_format
        out = str(
            source.serialize(
                format=fmt, auto_compact=True, sort_keys=True, max_depth=1
            )
        )

        if output_format in ("nt", "nquads"):
            lines = sorted(
                line.rstrip() for line in out.splitlines() if line.strip()
            )
            return f"{chr(10).join(lines)}\n" if lines else ""
        if output_format == "rdf":
            return sort_xml(out)
        if output_format == "json-ld":
            return json.dumps(sort_dict(json.loads(out)), indent=2)
        return out
