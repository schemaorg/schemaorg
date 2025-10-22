#!/usr/bin/env python
# -*- coding: utf-8; python-indent-offset: 4 -*-

"""A class that holds the schema graph and presents some operations on it.
"""

import rdflib

import software.util.schemaglobals as schemaglobals


SCHEMAORG = rdflib.Namespace(schemaglobals.HOMEPAGE)


class SchemaOrgGraph(object):
    def __init__(self, filename: str = None, format: str = "turtle"):
        self.g = rdflib.Graph()
        # Binding it here, as by default it would bind the /elements/1.1/ instead
        # of the dc terms. this way, the elements get assigned "dc1" or such
        # as a prefix, and we do not use that.
        self.g.bind("dc", rdflib.Namespace("http://purl.org/dc/terms/"), replace=True)
        if filename:
            self.g.parse(filename, format=format)

    def __getattr__(self, *args, **kwargs):
        return getattr(self.g, *args, **kwargs)

    def IdenticalTo(self, other: "SchemaOrgGraph"):
        only_in_other = other.g - self.g
        only_in_self = self.g - other.g
        if only_in_other or only_in_self:
            raise ValueError(f"Graphs differ: {only_in_other + only_in_self}")
        return True

    def FullyContains(self, graph: "SchemaOrgGraph"):
        only_in_subset = graph.g - self.g
        if only_in_subset:
            raise ValueError(f"Graph does not contain it all: {only_in_subset}")
        return True

    def ListSubjects(self, subject_type: rdflib.term.URIRef):
        return set([s for s, p, o in self.g.triples((None, rdflib.RDF.type, subject_type))])

    def Types(self):
        return self.ListSubjects(rdflib.RDFS.Class)

    def Properties(self):
        return self.ListSubjects(rdflib.RDF.Property)
