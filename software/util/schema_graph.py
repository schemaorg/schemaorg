#!/usr/bin/env python
# -*- coding: utf-8; python-indent-offset: 4 -*-

"""A class that holds the schema graph and presents some operations on it.
"""

import rdflib
from pathlib import Path
import typing
from typing import Any, Dict, List, Optional, Tuple, Union, Iterable, Sequence, Set, Callable

import software

import util.schema as schema
from util.issues import Issues, ALL_ISSUES

URI_BASE = schema.constants.HOMEPAGE
SCHEMAORG: rdflib.Namespace = rdflib.Namespace(URI_BASE if URI_BASE.endswith('/') else URI_BASE + '/')


class SchemaOrgGraph(object):
    def __init__(
        self,
        source: Union[Path, Issues],
        issue_list: List[str] = ALL_ISSUES,
    ) -> None:
        if source is None:
            raise ValueError("SchemaOrgGraph requires a source (Path or Issues object).")

        self.g: rdflib.Graph = rdflib.Graph()
        # Binding it here, as by default it would bind the /elements/1.1/
        # instead
        # of the dc terms. this way, the elements get assigned "dc1" or such
        # as a prefix, and we do not use that.
        self.g.bind("dc", rdflib.Namespace("http://purl.org/dc/terms/"), replace=True)

        if isinstance(source, Issues):
            for f in source.get_ttl_files(issue_list):
                self.g.parse(str(f), format="turtle")
        else:
            self.g.parse(str(source), format="turtle")

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
        return set([s for s, p, o in self.g.triples((None, rdflib.RDF.type, subject_type))])

    def Types(self) -> Set[rdflib.term.Node]:
        return self.ListSubjects(rdflib.RDFS.Class)

    def Properties(self) -> Set[rdflib.term.Node]:
        return self.ListSubjects(rdflib.RDF.Property)
