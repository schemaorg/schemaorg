from __future__ import annotations

import json
import unittest

import rdflib

from schemaorg.jsonld_slice import TermJsonLdIndex
from schemaorg.model import VocabularyLoader
from schemaorg.term_view import TermKind, TermSeq, TermViewCatalog

FIXTURE_TTL = """
@prefix : <https://schema.org/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix foaf: <http://xmlns.com/foaf/0.1/> .

:Thing a rdfs:Class ; rdfs:label "Thing" ; rdfs:comment "Root." .
:Intangible a rdfs:Class ; rdfs:label "Intangible" ; rdfs:subClassOf :Thing .
:Enumeration a rdfs:Class ; rdfs:label "Enumeration" ; rdfs:subClassOf :Intangible .
:DayOfWeek a rdfs:Class ; rdfs:label "DayOfWeek" ; rdfs:subClassOf :Enumeration .
:Monday a :DayOfWeek ; rdfs:label "Monday" .
:Person a rdfs:Class ; rdfs:label "Person" ; rdfs:subClassOf :Thing ;
    owl:equivalentClass foaf:Person .
:DataType a rdfs:Class ; rdfs:label "DataType" ; rdfs:subClassOf rdfs:Class .
:Number a :DataType, rdfs:Class ; rdfs:label "Number" .
:Integer a rdfs:Class ; rdfs:label "Integer" ; rdfs:subClassOf :Number .
:name a rdf:Property ; rdfs:label "name" ; rdfs:comment "dc: not a compact IRI." ;
    :domainIncludes :Thing ; :rangeIncludes :Number .
:alumni a rdf:Property ; rdfs:label "alumni" ; :domainIncludes :Person ;
    :rangeIncludes :Person ; :inverseOf :alumniOf .
:alumniOf a rdf:Property ; rdfs:label "alumniOf" ; :domainIncludes :Person ;
    :rangeIncludes :Person ; :inverseOf :alumni .
"""


class TestTermViewAndJsonLdSlice(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = rdflib.Graph(bind_namespaces="none")
        self.graph.parse(data=FIXTURE_TTL, format="turtle")
        self.vocab = VocabularyLoader(self.graph).load()
        self.catalog = TermViewCatalog.from_graph(self.graph, self.vocab)
        self.jsonld = TermJsonLdIndex.from_graph(self.graph)

    def _view(self, term_id: str):
        v = self.catalog.get(term_id)
        self.assertIsNotNone(v)
        assert v is not None
        return v

    def test_term_seq_exposes_terms_and_ids(self) -> None:
        person = self._view("Person")
        seq = TermSeq([person])
        self.assertEqual(seq.terms, (person,))
        self.assertEqual(seq.ids, ("Person",))

    def test_kinds_and_breadcrumbs(self) -> None:
        self.assertEqual(self._view("Person").termType, TermKind.TYPE)
        self.assertEqual(self._view("Number").termType, TermKind.DATATYPE)
        self.assertEqual(self._view("Integer").termType, TermKind.TYPE)
        self.assertEqual(self._view("DayOfWeek").termType, TermKind.ENUMERATION)
        self.assertEqual(
            self._view("Monday").termType, TermKind.ENUMERATIONVALUE
        )

        self.assertEqual(
            self._view("Integer").superPaths[0].ids,
            ("DataType", "Number", "Integer"),
        )
        self.assertEqual(
            self._view("name").superPaths[0].ids,
            ("Thing", "Property", "name"),
        )
        self.assertEqual(
            self._view("Monday").superPaths[0].ids,
            ("Thing", "Intangible", "Enumeration", "DayOfWeek", "Monday"),
        )

    def test_pure_enumeration_clears_term_stack_and_formats_references(
        self,
    ) -> None:
        dow = self.catalog.get("DayOfWeek")
        assert dow is not None
        self.assertEqual(dow.termStack, ())
        self.assertEqual(dow.allproperties.ids, ("name",))

        person = self.catalog.get("Person")
        assert person is not None
        self.assertEqual(person.equivalents[0].label, "foaf:Person")
        self.assertEqual(person.equivalents[0].termType, TermKind.REFERENCE)

        dt = self.catalog.get("DataType")
        assert dt is not None
        self.assertEqual(dt.supers[0].label, "rdfs:Class")

    def test_jsonld_slice_flattens_single_node_and_trims_context(self) -> None:
        name = self.catalog.get("name")
        assert name is not None
        single = json.loads(self.jsonld.render_for(name))
        self.assertEqual(single["@id"], "schema:name")
        self.assertNotIn("@graph", single)
        self.assertNotIn("foaf", single["@context"])

        person = self.catalog.get("Person")
        assert person is not None
        multi = json.loads(self.jsonld.render_for(person))
        self.assertIn("foaf", multi["@context"])
        self.assertEqual(
            [n["@id"] for n in multi["@graph"]],
            [
                "schema:Person",
                "schema:Thing",
                "schema:alumni",
                "schema:alumniOf",
                "schema:name",
            ],
        )


if __name__ == "__main__":
    unittest.main()
