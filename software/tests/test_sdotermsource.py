#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import sys
import os
import unittest
import logging
import rdflib

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software

import software.SchemaTerms.sdotermsource as sdotermsource
import software.SchemaTerms.sdoterm as sdoterm


class TestConversionFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sdotermsource.SdoTermSource.sourceGraph()

    def testVocabUri(self):
        self.assertEqual(sdotermsource.SdoTermSource.vocabUri(), "https://schema.org/")

    def testToFullId(self):
        self.assertEqual(sdotermsource.toFullId("fnord"), "https://schema.org/fnord")
        self.assertEqual(
            sdotermsource.toFullId("http://schema.org/Thing"), "http://schema.org/Thing"
        )

    def testUriWrap(self):
        self.assertEqual(sdotermsource.uriWrap("fnord"), "fnord")
        self.assertEqual(
            sdotermsource.uriWrap("http://schema.org/Thing"),
            "<http://schema.org/Thing>",
        )

    def testLayerFromUri(self):
        self.assertIsNone(sdotermsource.layerFromUri(None))
        self.assertIsNone(sdotermsource.layerFromUri("https://schema.org/Thing"))
        self.assertEqual(
            sdotermsource.layerFromUri("https://exclusive.schema.org/Thing"),
            "exclusive",
        )

    def testUriFromLayer(self):
        self.assertEqual(sdotermsource.uriFromLayer(), "https://schema.org")
        self.assertEqual(
            sdotermsource.uriFromLayer("premium"), "https://premium.schema.org"
        )

    def testGetProtoAndRoot(self):
        self.assertEqual(
            sdotermsource.getProtoAndRoot(""), sdotermsource.ProtoAndRoot(None, None)
        )
        self.assertEqual(
            sdotermsource.getProtoAndRoot("http://schema.org/Thing"),
            sdotermsource.ProtoAndRoot("http://", "schema.org/Thing"),
        )

    def testUri2id(self):
        self.assertEqual(sdotermsource.uri2id(""), "")
        self.assertEqual(sdotermsource.uri2id("https://schema.org/Thing"), "Thing")
        self.assertEqual(
            sdotermsource.uri2id("http://purl.org/dc/elements/1.1/"),
            "http://purl.org/dc/elements/1.1/",
        )

    def testPrefixFromUri(self):
        self.assertIsNone(sdotermsource.prefixFromUri(""))
        self.assertEqual(
            sdotermsource.prefixFromUri("https://schema.org/Thing"), "schema"
        )
        self.assertEqual(
            sdotermsource.prefixFromUri("http://purl.org/dc/elements/1.1/"), "dc"
        )

    def testUriForPrefix(self):
        self.assertIsNone(sdotermsource.uriForPrefix(""))
        self.assertEqual(
            sdotermsource.uriForPrefix("schema"),
            rdflib.term.URIRef("https://schema.org/"),
        )
        self.assertEqual(
            sdotermsource.uriForPrefix("dc"),
            rdflib.term.URIRef("http://purl.org/dc/elements/1.1/"),
        )
        self.assertIsNone(sdotermsource.uriForPrefix("gs1"))

    def testPrefixedIdFromUri(self):
        self.assertEqual(
            sdotermsource.prefixedIdFromUri("https://schema.org/Thing"), "schema:Thing"
        )
        self.assertEqual(
            sdotermsource.prefixedIdFromUri("http://purl.org/dc/elements/1.1/title"),
            "dc:title",
        )

    def testGetComment(self):
        product_term = sdotermsource.SdoTermSource.getTerm("Product")
        self.assertIn("product", product_term.comment)

    def testGetAckowledgements(self):
        product_term = sdotermsource.SdoTermSource.getTerm("Product")
        self.assertTrue(product_term.acknowledgements)
        collaborator = product_term.acknowledgements[0]
        self.assertEqual(collaborator.uri, "https://schema.org/docs/collab/GoodRelationsTerms")
        self.assertIn("GoodRelations Vocabulary for E-Commerce", collaborator.acknowledgement)


if __name__ == "__main__":
    unittest.main()
