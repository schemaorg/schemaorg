#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Unit tests for schemaorg.model (S9-S11, S13)."""

import pickle
import unittest

import rdflib
from rdflib import OWL, RDF, RDFS, Literal, Namespace, URIRef

from schemaorg import constants
from schemaorg.graph_loader import GraphLoader
from schemaorg.layout import InputLayout, Issues
from schemaorg.model import (
    DataType,
    EnumerationValue,
    SDO,
    SchemaProperty,
    SchemaType,
    Vocabulary,
    VocabularyLoader,
)
from schemaorg.version import VersionItem

FIXTURE_TTL = """
@prefix : <https://schema.org/> .
@prefix owl: <http://www.w3.org/2002/07/owl#> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

:Thing a rdfs:Class ;
    rdfs:label "Thing" ;
    rdfs:comment "The most generic type of item." .

:Intangible a rdfs:Class ;
    rdfs:label "Intangible" ;
    rdfs:comment "A utility class." ;
    rdfs:subClassOf :Thing .

:Person a rdfs:Class ;
    rdfs:label "Person" ;
    rdfs:comment "A person." ;
    rdfs:subClassOf :Thing ;
    owl:equivalentClass <http://xmlns.com/foaf/0.1/Person> ;
    :source <http://www.w3.org/wiki/WebSchemas/SchemaDotOrgSources#source_rNews> ;
    :contributor <https://schema.org/docs/collab/rNews> .

:Patient a rdfs:Class ;
    rdfs:label "Patient" ;
    rdfs:comment "A patient." ;
    rdfs:subClassOf :Person ;
    :isPartOf <https://health-lifesci.schema.org> .

:PendingWidget a rdfs:Class ;
    rdfs:label "PendingWidget" ;
    rdfs:comment "A work-in-progress widget." ;
    rdfs:subClassOf :Thing ;
    :isPartOf <https://pending.schema.org> .

:RetiredWidget a rdfs:Class ;
    rdfs:label "RetiredWidget" ;
    rdfs:comment "An archived widget." ;
    rdfs:subClassOf :Thing ;
    :isPartOf <https://attic.schema.org> .

:DataType a rdfs:Class ;
    rdfs:label "DataType" ;
    rdfs:comment "The basic data types." ;
    rdfs:subClassOf rdfs:Class .

:Text a :DataType, rdfs:Class ;
    rdfs:label "Text" ;
    rdfs:comment "Data type: Text." .

:Boolean a :DataType, rdfs:Class ;
    rdfs:label "Boolean" ;
    rdfs:comment "Boolean: True or False." .

:True a :Boolean ;
    rdfs:label "True" ;
    rdfs:comment "The boolean value true." .

:False a :Boolean ;
    rdfs:label "False" ;
    rdfs:comment "The boolean value false." .

:Enumeration a rdfs:Class ;
    rdfs:label "Enumeration" ;
    rdfs:comment "Lists or enumerations." ;
    rdfs:subClassOf :Intangible .

:DayOfWeek a rdfs:Class ;
    rdfs:label "DayOfWeek" ;
    rdfs:comment "The day of the week." ;
    rdfs:subClassOf :Enumeration .

:Monday a :DayOfWeek ;
    rdfs:label "Monday" ;
    rdfs:comment "The day of the week between Sunday and Tuesday." .

:name a rdf:Property ;
    rdfs:label "name" ;
    rdfs:comment "The name of the item." ;
    :domainIncludes :Thing ;
    :rangeIncludes :Text ;
    owl:equivalentProperty <http://purl.org/dc/terms/title> .

:alumniOf a rdf:Property ;
    rdfs:label "alumniOf" ;
    rdfs:comment "An organization that the person is an alumni of." ;
    rdfs:subPropertyOf :name ;
    :domainIncludes :Person ;
    :rangeIncludes :Thing ;
    :inverseOf :alumni .

:alumni a rdf:Property ;
    rdfs:label "alumni" ;
    rdfs:comment "Alumni of an organization." ;
    :domainIncludes :Thing ;
    :rangeIncludes :Person ;
    :inverseOf :alumniOf .

:actors a rdf:Property ;
    rdfs:label "actors" ;
    rdfs:comment "Actors performing in the movie." ;
    :domainIncludes :Thing ;
    :rangeIncludes :Person ;
    :supersededBy :actor .

:actor a rdf:Property ;
    rdfs:label "actor" ;
    rdfs:comment "An actor." ;
    :domainIncludes :Thing ;
    :rangeIncludes :Person .
"""


def _build_fixture_graph() -> rdflib.Graph:
    g = rdflib.Graph(bind_namespaces="core")
    g.parse(data=FIXTURE_TTL, format="turtle")
    return g


class TestModelTermsFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.graph = _build_fixture_graph()
        self.version = VersionItem("30.1", "2026-09-16")
        self.vocab = VocabularyLoader(self.graph, version=self.version).load()

    def test_type_fields(self) -> None:
        person = self.vocab.types[SDO.Person]
        self.assertIsInstance(person, SchemaType)
        self.assertEqual(person.id, "Person")
        self.assertEqual(person.label, "Person")
        self.assertEqual(person.comment, "A person.")
        self.assertEqual(person.supers, [SDO.Thing])
        self.assertEqual(
            person.equivalents,
            [URIRef("http://xmlns.com/foaf/0.1/Person")],
        )
        self.assertEqual(
            person.source,
            [URIRef("http://www.w3.org/wiki/WebSchemas/SchemaDotOrgSources#source_rNews")],
        )
        self.assertEqual(
            person.contributor,
            [URIRef("https://schema.org/docs/collab/rNews")],
        )

    def test_property_fields(self) -> None:
        alumni_of = self.vocab.properties[SDO.alumniOf]
        self.assertIsInstance(alumni_of, SchemaProperty)
        self.assertEqual(alumni_of.id, "alumniOf")
        self.assertEqual(alumni_of.supers, [SDO.name])
        self.assertEqual(alumni_of.domainIncludes, [SDO.Person])
        self.assertEqual(alumni_of.rangeIncludes, [SDO.Thing])
        self.assertEqual(alumni_of.inverseOf, [SDO.alumni])

        actors = self.vocab.properties[SDO.actors]
        self.assertEqual(actors.supersededBy, [SDO.actor])
        self.assertEqual(self.vocab.supersedes[SDO.actor], (SDO.actors,))

    def test_datatype_and_boolean_literals(self) -> None:
        self.assertIn(SDO.DataType, self.vocab.datatypes)
        self.assertIn(SDO.Boolean, self.vocab.datatypes)
        self.assertIn(SDO["True"], self.vocab.datatypes)
        self.assertIn(SDO["False"], self.vocab.datatypes)
        self.assertIsInstance(self.vocab.types[SDO.Boolean], DataType)
        self.assertEqual(
            self.vocab.subs[SDO.DataType],
            (SDO.Boolean, SDO.Text),
        )
        self.assertEqual(
            self.vocab.subs[SDO.Boolean],
            (SDO["False"], SDO["True"]),
        )

    def test_enumeration_and_values(self) -> None:
        self.assertEqual(
            self.vocab.enumerations,
            frozenset({SDO.Enumeration, SDO.DayOfWeek}),
        )
        monday = self.vocab.enum_values[SDO.Monday]
        self.assertIsInstance(monday, EnumerationValue)
        self.assertEqual(monday.id, "Monday")
        self.assertEqual(
            self.vocab.enumeration_members[SDO.DayOfWeek],
            (SDO.Monday,),
        )

    def test_reverse_indexes_and_closure(self) -> None:
        self.assertEqual(
            self.vocab.declared_properties[SDO.Person],
            (SDO.alumniOf,),
        )
        self.assertEqual(
            self.vocab.expected_type_for[SDO.Person],
            (SDO.actor, SDO.actors, SDO.alumni),
        )
        self.assertEqual(
            self.vocab.ancestors[SDO.Patient],
            (SDO.Person, SDO.Thing),
        )
        self.assertEqual(
            self.vocab.all_properties[SDO.Patient],
            (SDO.actor, SDO.actors, SDO.alumni, SDO.alumniOf, SDO.name),
        )

    def test_hash_and_pickle(self) -> None:
        vocab_hash = hash(self.vocab)
        restored = pickle.loads(pickle.dumps(self.vocab))
        self.assertEqual(restored, self.vocab)
        self.assertEqual(hash(restored), vocab_hash)

    def test_layers_and_ga_terms(self) -> None:
        self.assertEqual(self.vocab.layer("Person"), "core")
        self.assertEqual(self.vocab.layer("Patient"), "health-lifesci")
        self.assertEqual(self.vocab.layer("PendingWidget"), "pending")
        self.assertEqual(self.vocab.layer("RetiredWidget"), "attic")

        ga = self.vocab.ga_terms()
        self.assertIn(SDO.Person, ga)
        self.assertIn(SDO.Patient, ga)
        self.assertNotIn(SDO.PendingWidget, ga)
        self.assertNotIn(SDO.RetiredWidget, ga)

        reordered_graph = rdflib.Graph(bind_namespaces="core")
        for triple in reversed(list(self.graph)):
            reordered_graph.add(triple)
        vocab2 = VocabularyLoader(reordered_graph, version=self.version).load()
        self.assertEqual(self.vocab, vocab2)

        mutated_graph = _build_fixture_graph()
        mutated_graph.add((SDO.name, SDO.rangeIncludes, SDO.Person))
        vocab3 = VocabularyLoader(mutated_graph, version=self.version).load()
        self.assertNotEqual(self.vocab.term(SDO.name), vocab3.term(SDO.name))


class TestVocabularyLoaderRealGraph(unittest.TestCase):
    def test_real_vocabulary_counts(self) -> None:
        files = Issues(InputLayout(constants.PROJECT_ROOT)).get_ttl_files()
        graph = GraphLoader().load(files)
        vocab = VocabularyLoader(graph).load()

        self.assertEqual(len(vocab.types), 940)
        self.assertEqual(len(vocab.properties), 1540)
        self.assertEqual(len(vocab.enumerations), 96)
        self.assertEqual(len(vocab.enum_values), 544)
        self.assertEqual(len(vocab.datatypes), 10)
        self.assertEqual(len(vocab.all_terms()), 3026)


if __name__ == "__main__":
    unittest.main()
