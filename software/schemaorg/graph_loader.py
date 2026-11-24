"""RDF graph loading and release-scope partitioning."""

from __future__ import annotations

from collections.abc import Iterable
import logging
from pathlib import Path

import rdflib

from schemaorg import constants
from schemaorg.sdo_uri import SDO, SdoUri

log: logging.Logger = logging.getLogger(__name__)

_META_CLASSES: frozenset[rdflib.URIRef] = frozenset({
    rdflib.RDFS.Class,
    rdflib.OWL.Class,
    rdflib.RDF.Property,
})
_META_PROPS: frozenset[rdflib.URIRef] = frozenset({
    rdflib.RDF.Property,
    rdflib.OWL.ObjectProperty,
    rdflib.OWL.DatatypeProperty,
})
_FOREIGN_STUB_RULES: tuple[
    tuple[tuple[rdflib.URIRef, ...], frozenset[rdflib.URIRef], rdflib.URIRef],
    ...,
] = (
    (
        (rdflib.RDFS.subClassOf, rdflib.OWL.equivalentClass),
        _META_CLASSES,
        rdflib.RDFS.Class,
    ),
    (
        (rdflib.RDFS.subPropertyOf, rdflib.OWL.equivalentProperty),
        _META_PROPS,
        rdflib.RDF.Property,
    ),
)


_SCHEMA_ROOT: SdoUri = SdoUri(constants.SCHEMA_URI)


def validate_schema_namespaces(
    graph: rdflib.Graph, source: Path | None = None
) -> None:
    """Assert schema: <-> SCHEMA_URI 1:1 (allowing Turtle's unnamed ':' prefix)."""
    where = f" in {source}" if source is not None else ""
    for prefix, ns_uri in graph.namespaces():
        sdo = SdoUri(ns_uri)
        if prefix != constants.SCHEMA_PREFIX and not sdo.is_sdo():
            continue
        if prefix not in ("", constants.SCHEMA_PREFIX) or sdo != _SCHEMA_ROOT:
            raise ValueError(
                f"Invalid schema namespace binding '{prefix}:' -> <{ns_uri}>; "
                f"expected '{constants.SCHEMA_PREFIX}:' <-> <{_SCHEMA_ROOT}>{where}"
            )


def _copy_namespaces(source: rdflib.Graph, target: rdflib.Graph) -> None:
    for prefix, ns_uri in sorted(
        source.namespaces(), key=lambda kv: (kv[0] == "", kv[0])
    ):
        key = prefix or (
            constants.SCHEMA_PREFIX if SdoUri(ns_uri) == _SCHEMA_ROOT else ""
        )
        if key:
            target.bind(key, ns_uri, override=True)


def split_release_graphs(
    source_graph: rdflib.Graph,
) -> tuple[rdflib.Graph, rdflib.Graph]:
    """ALL graph (schema.org subjects plus foreign type stubs) and CURRENT graph (no attic)."""
    validate_schema_namespaces(source_graph)
    all_graph = rdflib.Graph(bind_namespaces="none")
    current_graph = rdflib.Graph(bind_namespaces="none")

    for s, p, o in source_graph:
        if isinstance(s, rdflib.URIRef) and SdoUri(s).is_sdo():
            all_graph.add((s, p, o))

    # Foreign classes and properties referenced by schema.org terms get a bare
    # type declaration so consumers can resolve them (skipping W3C meta-terms).
    for predicates, excluded, stub_type in _FOREIGN_STUB_RULES:
        for pred in predicates:
            for _, o in list(all_graph.subject_objects(pred)):
                if (
                    isinstance(o, rdflib.URIRef)
                    and o not in excluded
                    and not SdoUri(o).is_sdo()
                ):
                    all_graph.add((o, rdflib.RDF.type, stub_type))

    retired = {
        s
        for s, o in all_graph.subject_objects(SDO.isPartOf)
        if SdoUri(o).is_retired()
    }
    for s, p, o in all_graph:
        if s not in retired:
            current_graph.add((s, p, o))

    _copy_namespaces(source_graph, all_graph)
    _copy_namespaces(source_graph, current_graph)

    return all_graph, current_graph


class GraphLoader:
    """Parses a set of TTL files into a single RDF graph.

    Deliberately knows nothing about layouts, issues or releases: *which*
    files make up a graph is a selection concern, answered by ``Issues`` for
    the source tree and by ``Releases`` for a published release. Those two
    are not symmetric -- the source tree is a union of many files, a release
    is one chosen file -- so the choice is not hidden in here.
    """

    @staticmethod
    def load(files: Iterable[Path]) -> rdflib.Graph:
        """Loads the given TTL files into one graph.

        Namespace bindings are whatever the files themselves declare; none
        are added here. Enforces the ``schema:`` <-> ``SCHEMA_URI`` invariant
        after each file is parsed.
        """
        graph = rdflib.Graph(bind_namespaces="none")
        for file_path in files:
            try:
                graph.parse(file_path, format="turtle")
            except Exception as e:
                log.warning("Error parsing TTL file '%s': %s", file_path, e)
                raise
            validate_schema_namespaces(graph, source=file_path)
        return graph
