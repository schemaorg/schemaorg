#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Unit tests for schemaorg.sdo_uri."""

import unittest
from urllib.parse import urlparse

from rdflib import BNode, URIRef

from schemaorg import constants
from schemaorg.sdo_uri import SCHEMA_URL, SDO, SdoUri


class TestSdoUri(unittest.TestCase):
    def test_schema_org_uri(self) -> None:
        sdo = SdoUri(SDO.Person)
        self.assertTrue(sdo.is_sdo())
        self.assertEqual(sdo.term_name(), "Person")
        self.assertEqual(sdo.uri, SDO.Person)
        self.assertEqual(str(sdo), "https://schema.org/Person")

    def test_bnode_not_expanded(self) -> None:
        bnode = BNode()
        wrapped = SdoUri(bnode)
        self.assertFalse(wrapped.is_sdo())
        self.assertEqual(str(wrapped), str(bnode))
        self.assertEqual(wrapped.term_name(), str(bnode))
        self.assertFalse(wrapped.is_retired())
        # Same characters as a plain str still mean a bare term name.
        self.assertTrue(SdoUri(str(bnode)).is_sdo())
        self.assertEqual(str(SdoUri(str(bnode))), f"https://schema.org/{bnode}")

    def test_external_uri_preserved(self) -> None:
        ext = SdoUri("http://xmlns.com/foaf/0.1/Person")
        self.assertFalse(ext.is_sdo())
        self.assertEqual(ext.uri, URIRef("http://xmlns.com/foaf/0.1/Person"))
        self.assertEqual(str(ext), "http://xmlns.com/foaf/0.1/Person")

        file_uri = SdoUri("file:///tmp/comics.rdfa")
        self.assertFalse(file_uri.is_sdo())
        self.assertEqual(str(file_uri), "file:///tmp/comics.rdfa")

    def test_bare_term_name(self) -> None:
        bare = SdoUri("Person")
        self.assertTrue(bare.is_sdo())
        self.assertEqual(bare.uri, SDO.Person)
        self.assertEqual(bare.term_name(), "Person")
        self.assertEqual(str(bare), "https://schema.org/Person")

    def test_layer_extraction(self) -> None:
        hls = SdoUri("https://health-lifesci.schema.org")
        self.assertTrue(hls.is_sdo())
        self.assertEqual(hls.layer(), "health-lifesci")

        pending = SdoUri("https://pending.schema.org")
        self.assertTrue(pending.is_sdo())
        self.assertEqual(pending.layer(), "pending")
        self.assertFalse(pending.is_retired())

        attic = SdoUri("https://attic.schema.org")
        self.assertTrue(attic.is_sdo())
        self.assertEqual(attic.layer(), "attic")
        self.assertTrue(attic.is_retired())

        core = SdoUri("https://schema.org")
        self.assertTrue(core.is_sdo())
        self.assertEqual(core.layer(), "core")
        self.assertFalse(core.is_retired())

    def test_for_layer(self) -> None:
        for core_layer in (None, "", "core"):
            self.assertEqual(str(SdoUri.for_layer(core_layer)), "https://schema.org")
        pending = SdoUri.for_layer("pending")
        self.assertEqual(str(pending), "https://pending.schema.org")
        self.assertEqual(pending.uri, URIRef("https://pending.schema.org"))
        self.assertIsInstance(pending.uri, URIRef)
        for layer in ("pending", "attic", "health-lifesci"):
            self.assertEqual(SdoUri.for_layer(layer).layer(), layer)
        self.assertEqual(SdoUri.for_layer().layer(), "core")

    def test_parse_result_input(self) -> None:
        root = SdoUri(SCHEMA_URL)
        self.assertEqual(str(root), constants.SCHEMA_URI)
        self.assertTrue(root.is_sdo())
        self.assertEqual(root.term_name(), "")

        pending = SdoUri(urlparse("https://pending.schema.org/Foo"))
        self.assertEqual(pending.layer(), "pending")
        self.assertEqual(pending.term_name(), "Foo")

        with self.assertLogs("schemaorg.sdo_uri", level="WARNING"):
            upgraded = SdoUri(urlparse("http://schema.org/Foo"))
        self.assertEqual(str(upgraded), str(SdoUri("http://schema.org/Foo")))
        self.assertEqual(upgraded.uri, SDO.Foo)

        bare = SdoUri(urlparse("Foo"))
        self.assertEqual(str(bare), str(SdoUri("Foo")))
        self.assertEqual(bare.uri, SDO.Foo)
        self.assertEqual(str(SdoUri("Thing")), "https://schema.org/Thing")

    def test_http_schema_org_upgraded_with_warning(self) -> None:
        with self.assertLogs("schemaorg.sdo_uri", level="WARNING"):
            upgraded = SdoUri("http://schema.org/Person")
        self.assertTrue(upgraded.is_sdo())
        self.assertEqual(upgraded.uri, SDO.Person)
        self.assertEqual(upgraded.term_name(), "Person")
        self.assertEqual(str(upgraded), "https://schema.org/Person")

        with self.assertLogs("schemaorg.sdo_uri", level="WARNING"):
            upgraded_layer = SdoUri("http://pending.schema.org")
        self.assertTrue(upgraded_layer.is_sdo())
        self.assertEqual(upgraded_layer.layer(), "pending")
        self.assertEqual(str(upgraded_layer), "https://pending.schema.org")


if __name__ == "__main__":
    unittest.main()
