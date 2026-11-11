from __future__ import annotations

import unittest

import rdflib

import SchemaTerms.sdoterm as sdoterm
import SchemaTerms.sdotermsource as sdotermsource


class TestConversionFunctions(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        sdotermsource.SdoTermSource.sourceGraph()

    def testVocabUri(self) -> None:
        self.assertEqual(sdotermsource.SdoTermSource.vocabUri(), "https://schema.org/")

    def testToFullId(self) -> None:
        self.assertEqual(sdotermsource.toFullId("fnord"), "https://schema.org/fnord")
        self.assertEqual(
            sdotermsource.toFullId("https://schema.org/Thing"),
            "https://schema.org/Thing",
        )

    def testUriWrap(self) -> None:
        self.assertEqual(sdotermsource.uriWrap("fnord"), "fnord")
        self.assertEqual(
            sdotermsource.uriWrap("https://schema.org/Thing"),
            "<https://schema.org/Thing>",
        )

    def testLayerFromUri(self) -> None:
        self.assertIsNone(sdotermsource.layerFromUri(None))
        self.assertIsNone(sdotermsource.layerFromUri("https://schema.org/Thing"))
        self.assertEqual(
            sdotermsource.layerFromUri("https://exclusive.schema.org/Thing"),
            "exclusive",
        )
        self.assertEqual(
            sdotermsource.layerFromUri("https://health-lifesci.schema.org/Patient"),
            "health-lifesci",
        )

    def testUriFromLayer(self) -> None:
        self.assertEqual(sdotermsource.uriFromLayer(), "https://schema.org")
        self.assertEqual(
            sdotermsource.uriFromLayer("premium"), "https://premium.schema.org"
        )

    def testUri2id(self) -> None:
        self.assertEqual(sdotermsource.uri2id(""), "")
        self.assertEqual(sdotermsource.uri2id("https://schema.org/Thing"), "Thing")
        self.assertEqual(
            sdotermsource.uri2id("http://purl.org/dc/elements/1.1/"),
            "http://purl.org/dc/elements/1.1/",
        )

    def testPrefixFromUri(self) -> None:
        self.assertIsNone(sdotermsource.prefixFromUri(""))
        self.assertEqual(
            sdotermsource.prefixFromUri("https://schema.org/Thing"), "schema"
        )
        self.assertEqual(
            sdotermsource.prefixFromUri("http://purl.org/dc/elements/1.1/"), "dc"
        )
        self.assertEqual(
            sdotermsource.prefixFromUri(
                "https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Registration/"
            ),
            "fibo-fnd-arr-reg",
        )

    def testUriForPrefix(self) -> None:
        self.assertIsNone(sdotermsource.uriForPrefix(""))
        self.assertEqual(
            sdotermsource.uriForPrefix("schema"),
            rdflib.URIRef("https://schema.org/"),
        )
        self.assertEqual(
            sdotermsource.uriForPrefix("dc"),
            rdflib.URIRef("http://purl.org/dc/elements/1.1/"),
        )
        self.assertIsNone(sdotermsource.uriForPrefix("feedface"))

    def testPrefixedIdFromUri(self) -> None:
        self.assertEqual(
            sdotermsource.prefixedIdFromUri("https://schema.org/Thing"), "schema:Thing"
        )
        self.assertEqual(
            sdotermsource.prefixedIdFromUri("http://purl.org/dc/elements/1.1/title"),
            "dc:title",
        )
        self.assertEqual(
            sdotermsource.prefixedIdFromUri(
                "https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Registration/hasRegistrationIdentifier"
            ),
            "fibo-fnd-arr-reg:hasRegistrationIdentifier",
        )

    def testGetComment(self) -> None:
        product_term = sdotermsource.SdoTermSource.getTerm("Product")
        self.assertIn("product", product_term.comment)

    def testGetAcknowledgements(self) -> None:
        product_term = sdotermsource.SdoTermSource.getTerm("Product")
        self.assertTrue(product_term.acknowledgements)
        collaborator = product_term.acknowledgements[0]
        self.assertEqual(
            collaborator.uri, "https://schema.org/docs/collab/GoodRelationsTerms"
        )
        self.assertIn(
            "GoodRelations Vocabulary for E-Commerce", collaborator.acknowledgement
        )

    def testParentPathsNoExternalDuplicates(self) -> None:
        seller_paths = sdotermsource.SdoTermSource.getParentPathTo("seller")
        self.assertEqual(seller_paths, [["Thing", "Property", "participant", "seller"]])

        min_price_paths = sdotermsource.SdoTermSource.getParentPathTo("minPrice")
        self.assertEqual(min_price_paths, [["Thing", "Property", "minPrice"]])

    def testLazyResolution(self) -> None:
        lazy_pending = sdoterm.SdoTermOrId(term_id="subTrip")
        self.assertFalse(lazy_pending.expanded)
        self.assertTrue(lazy_pending.pending)
        self.assertFalse(lazy_pending.retired)
        self.assertEqual(lazy_pending.extLayer, "pending")

        lazy_attic = sdoterm.SdoTermOrId(term_id="variablesMeasured")
        self.assertFalse(lazy_attic.expanded)
        self.assertFalse(lazy_attic.pending)
        self.assertTrue(lazy_attic.retired)
        self.assertEqual(lazy_attic.extLayer, "attic")


if __name__ == "__main__":
    unittest.main()
