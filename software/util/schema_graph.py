"""A class that holds the schema graph and presents some operations on it."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Any

import rdflib

from schemaorg.graph_loader import GraphLoader
from schemaorg.sdo_uri import SDO as SCHEMAORG

__all__ = ["SCHEMAORG", "SchemaOrgGraph"]


class SchemaOrgGraph:
    """Comparison helpers over a graph built from a list of TTL files.

    Which files those are is the caller's problem: ``Issues`` answers it for
    the source tree, ``Releases`` for a published release, and a CLI can just
    pass the paths it was given.
    """

    def __init__(self, files: Sequence[Path]) -> None:
        if not files:
            raise ValueError("SchemaOrgGraph requires at least one TTL file.")
        self.g: rdflib.Graph = GraphLoader.load(files)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.g, name)

    def IdenticalTo(self, other: SchemaOrgGraph) -> bool:
        return not (other.g - self.g) and not (self.g - other.g)

    def FullyContains(self, graph: SchemaOrgGraph) -> bool:
        return not (graph.g - self.g)

    def ListSubjects(self, subject_type: rdflib.term.URIRef) -> set[rdflib.term.Node]:
        return {s for s, _, _ in self.g.triples((None, rdflib.RDF.type, subject_type))}

    def Types(self) -> set[rdflib.term.Node]:
        return self.ListSubjects(rdflib.RDFS.Class)

    def Properties(self) -> set[rdflib.term.Node]:
        return self.ListSubjects(rdflib.RDF.Property)
