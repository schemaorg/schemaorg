#!/usr/bin/env python
# -*- coding: utf-8; python-indent-offset: 4 -*-

"""A class that holds the schema graph and presents some operations on it.
"""

import rdflib
from pathlib import Path
from typing import Any, List, Set, Union

import util.schema as schema
from schemaorg.graph_loader import GraphLoader


URI_BASE = schema.constants.HOMEPAGE
SCHEMAORG: rdflib.Namespace = rdflib.Namespace(URI_BASE if URI_BASE.endswith('/') else URI_BASE + '/')


class SchemaOrgGraph(object):
    """Comparison helpers over a graph built from a list of TTL files.

    Which files those are is the caller's problem: ``Issues`` answers it for
    the source tree, ``Releases`` for a published release, and a CLI can just
    pass the paths it was given.
    """

    def __init__(self, files: Sequence[Path]) -> None:
        if not files:
            raise ValueError("SchemaOrgGraph requires at least one TTL file.")
        self.g: rdflib.Graph = GraphLoader().load(files)

    def __getattr__(self, name: str) -> Any:
        return getattr(self.g, name)

    def IdenticalTo(self, other: "SchemaOrgGraph") -> bool:
        only_in_other: rdflib.Graph = other.g - self.g
        only_in_self: rdflib.Graph = self.g - other.g
        if only_in_other or only_in_self:
            raise ValueError(f"Graphs differ: {only_in_other + only_in_self}")
        return True

    def FullyContains(self, graph: "SchemaOrgGraph") -> bool:
        only_in_subset: rdflib.Graph = graph.g - self.g
        if only_in_subset:
            raise ValueError(f"Graph does not contain it all: {only_in_subset}")
        return True

    def ListSubjects(self, subject_type: rdflib.term.URIRef) -> Set[rdflib.term.Node]:
        return {s for s, _, _ in self.g.triples((None, rdflib.RDF.type, subject_type))}

    def Types(self) -> Set[rdflib.term.Node]:
        return self.ListSubjects(rdflib.RDFS.Class)

    def Properties(self) -> Set[rdflib.term.Node]:
        return self.ListSubjects(rdflib.RDF.Property)
