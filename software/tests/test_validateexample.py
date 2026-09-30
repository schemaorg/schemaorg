#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Tests for example validation: the validator, and the shapes it runs on.

ValidateExampleTests drives ExampleValidator on a toy shapes graph, so it
needs no build. Payloads cover the four outcomes: valid, invalid,
untargeted, and unparseable.

ShaclGateLivenessTests feeds the committed data/releases/<version>/ shapes
a payload they are required to reject. Without it, shapes carrying no
constraints or targeting the wrong namespace still exit 0. Both have
happened here.
"""

import textwrap
import unittest

import rdflib
from rdflib.namespace import SH

import util.paths as paths

import scripts.validate_examples_shacl as validator


class FakeExample:
    """Stand-in for a SchemaExamples example. validate() needs these two."""

    def __init__(self, key, jsonld):
        self._key = key
        self._jsonld = jsonld

    def getKey(self):
        return self._key

    def getJsonldRaw(self):
        return self._jsonld


class ValidateExampleTests(unittest.TestCase):

    GOOD = '{"@context":"http://schema.org/","@type":"Person","name":"Jane"}'
    BAD = ('{"@context":"http://schema.org/","@type":"Person",'
           '"name":{"@type":"Person","name":"not a string"}}')

    @classmethod
    def setUpClass(cls):
        shapes_turtle = textwrap.dedent("""\
            @prefix sh:     <http://www.w3.org/ns/shacl#> .
            @prefix schema: <http://schema.org/> .
            @prefix xsd:    <http://www.w3.org/2001/XMLSchema#> .
            @prefix ex:     <http://example.org/> .

            ex:PersonShape a sh:NodeShape ;
                sh:targetClass schema:Person ;
                sh:property [ sh:path schema:name ; sh:datatype xsd:string ] .
            """)
        cls.shapes = rdflib.Graph()
        cls.shapes.parse(data=shapes_turtle, format="turtle")
        cls.ontology = rdflib.Graph()
        cls.engine = validator.ExampleValidator(
            shacl_graph=cls.shapes, ont_graph=cls.ontology
        )

    def validate(self, name, jsonld):
        return self.engine.validate(FakeExample(name, jsonld))

    def testResultCarriesItsExample(self):
        example = FakeExample("some-key", self.GOOD)

        result = self.engine.validate(example)
        self.assertIs(result.example, example)
        self.assertEqual(result.name, "some-key")

    def testTargetClassesAreIndexed(self):
        self.assertEqual(
            self.engine.target_classes, frozenset({"http://schema.org/Person"})
        )

    def testShapesWithoutTargetsCannotBuildAValidator(self):
        with self.assertRaises(ValueError):
            validator.ExampleValidator(
                shacl_graph=rdflib.Graph(), ont_graph=rdflib.Graph()
            )

    def testValidExampleConforms(self):
        result = self.validate("good", self.GOOD)
        self.assertTrue(result.targeted)
        self.assertTrue(result.conforms)
        self.assertIsNone(result.error)
        self.assertIsNone(result.report, "clean examples carry no report")

    def testInvalidExampleIsRejectedWithAReport(self):
        result = self.validate("bad", self.BAD)
        self.assertTrue(result.targeted)
        self.assertFalse(result.conforms)
        self.assertIsNone(result.error, "a violation is not an error")
        self.assertTrue(result.report, "a failure must explain itself")

    def testUntargetedExampleConformsButIsNotTargeted(self):
        recipe = '{"@context":"http://schema.org/","@type":"Recipe","name":"Soup"}'

        result = self.validate("untargeted", recipe)
        self.assertFalse(result.targeted, "no shape targets Recipe")
        self.assertTrue(result.conforms, "vacuously true, not inspected")

    def testMalformedInputIsReportedNotRaised(self):
        result = self.validate("malformed", "{ this is not json")
        self.assertIsNotNone(result.error)
        self.assertFalse(result.conforms)

    def testNameIsCarriedThrough(self):
        self.assertEqual(self.validate("some-key", self.GOOD).name, "some-key")

    def testRepeatedValidationDoesNotGrowTheGraphs(self):
        """Shared graphs must converge, not accumulate.

        pyshacl injects two RDFS axioms into the shapes graph on first use.
        Idempotent, so reuse is safe, but it is a real write.
        """
        # Burn the one-off injection.
        self.validate("warmup", self.GOOD)
        shapes_before = len(self.shapes)
        ontology_before = len(self.ontology)

        for name, payload in (("good", self.GOOD), ("bad", self.BAD),
                              ("good2", self.GOOD)):
            self.validate(name, payload)

        self.assertEqual(len(self.shapes), shapes_before)
        self.assertEqual(len(self.ontology), ontology_before)


class ShaclGateLivenessTests(unittest.TestCase):
    """The shipped shapes must be able to reject something.

    Drives the real ExampleValidator: a canary validated under different
    settings than production proves nothing about production.
    """

    SHAPES_FILENAME = "schemaorg-shapes.shacl"
    SUBCLASSES_FILENAME = "schemaorg-subclasses.shacl"

    @classmethod
    def setUpClass(cls):
        shapes = cls._load(cls.SHAPES_FILENAME)
        ontology = cls._load(cls.SUBCLASSES_FILENAME)

        cls.result = None
        if shapes is None or ontology is None:
            return

        cls.shapes = shapes
        engine = validator.ExampleValidator(
            shacl_graph=shapes, ont_graph=ontology
        )
        # One pyshacl run, three assertions below.
        cls.result = engine.validate(
            FakeExample("canary", cls.canary_payload())
        )

    @classmethod
    def _load(cls, filename):
        path = paths.DefaultInputLayout().domain_file(
            paths.Domain.RELEASE_DATA, filename
        )
        if not path.is_file():
            return None
        graph = rdflib.Graph()
        graph.parse(source=str(path), format="turtle")
        return graph

    @staticmethod
    def canary_payload():
        """A payload the shapes are required to reject.

        schema:name ranges over Text, so a nested Person is a type error.
        https context, as the real examples write it: namespace drift shows
        up here as "the canary conformed".
        """
        return textwrap.dedent("""\
            {
              "@context": "https://schema.org",
              "@type": "Person",
              "name": { "@type": "Person", "name": "a Person is not a name" }
            }
            """)

    def setUp(self):
        if self.result is None:
            self.skipTest("release shapes not built")

    def testCanaryParses(self):
        """Usually fails when the schema.org context cannot be fetched."""
        self.assertIsNone(self.result.error)

    def testCanaryIsTargetedByTheShapes(self):
        targets = {str(t) for t in self.shapes.objects(None, SH.targetClass)}

        self.assertTrue(
            self.result.targeted,
            "no canary type matches any sh:targetClass, so nothing would be "
            "inspected. Signature of a namespace mismatch.\n"
            f"  sample targets: {sorted(targets)[:3]}",
        )

    def testCanaryIsRejected(self):
        self.assertFalse(
            self.result.conforms,
            "the canary is deliberately invalid (a Person used as a "
            "schema:name) yet it conformed. The shapes constrain nothing.",
        )


if __name__ == "__main__":
    unittest.main()
