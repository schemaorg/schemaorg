from __future__ import annotations

import unittest
from urllib.parse import urlparse

from rdflib import BNode, Literal, URIRef

from schemaorg import constants
from schemaorg.layout import Domain
from schemaorg.sdo_uri import SCHEMA_URL, SDO, SdoUri


class TestSdoUri(unittest.TestCase):
    def test_schema_org_uri(self) -> None:
        sdo = SdoUri(SDO.Person)
        self.assertTrue(sdo.is_sdo())
        self.assertEqual(sdo.term_name(), "Person")
        self.assertEqual(sdo.uri, SDO.Person)
        self.assertEqual(str(sdo), "https://schema.org/Person")

    def test_none_rejected(self) -> None:
        with self.assertRaises(TypeError):
            SdoUri(None)  # type: ignore[arg-type]

    def test_bnode_not_a_uri(self) -> None:
        bnode = BNode()
        wrapped = SdoUri(bnode)
        self.assertFalse(wrapped.is_sdo())
        self.assertEqual(str(wrapped), str(bnode))
        self.assertEqual(wrapped.term_name(), str(bnode))
        self.assertFalse(wrapped.is_retired())
        with self.assertRaises(ValueError):
            _ = wrapped.uri
        with self.assertRaises(ValueError):
            _ = wrapped.path
        # Same characters as a plain str still mean a bare term name.
        self.assertTrue(SdoUri(str(bnode)).is_sdo())
        self.assertEqual(str(SdoUri(str(bnode))), f"https://schema.org/{bnode}")

    def test_literal_not_a_uri(self) -> None:
        for raw in ("Person", "https://schema.org/Person", "https://attic.schema.org"):
            wrapped = SdoUri(Literal(raw))
            self.assertFalse(wrapped.is_sdo())
            self.assertEqual(str(wrapped), raw)
            self.assertEqual(wrapped.term_name(), raw)
            self.assertFalse(wrapped.is_retired())
            with self.assertRaises(ValueError):
                _ = wrapped.uri
            with self.assertRaises(ValueError):
                _ = wrapped.path

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

    def test_schema_prefix_curie(self) -> None:
        prefixed = SdoUri(f"{constants.SCHEMA_PREFIX}:Person")
        self.assertTrue(prefixed.is_sdo())
        self.assertEqual(prefixed.uri, SDO.Person)
        self.assertEqual(prefixed.term_name(), "Person")
        self.assertEqual(str(prefixed), "https://schema.org/Person")
        self.assertEqual(prefixed, SdoUri("Person"))
        self.assertEqual(hash(prefixed), hash(SdoUri(SDO.Person)))

        self.assertEqual(
            SdoUri(f"{constants.SCHEMA_PREFIX}:").uri, SDO[""]
        )
        self.assertEqual(
            str(SdoUri(f"{constants.SCHEMA_PREFIX}:docs/collab/rNews")),
            "https://schema.org/docs/collab/rNews",
        )
        self.assertEqual(
            SdoUri(f"{constants.SCHEMA_PREFIX}:/Person").uri, SDO.Person
        )
        self.assertEqual(
            SdoUri(urlparse(f"{constants.SCHEMA_PREFIX}:Person")).uri,
            SDO.Person,
        )

        # Other CURIE prefixes and Literals must not resolve to schema.org.
        self.assertFalse(SdoUri("bibo:Issue").is_sdo())
        self.assertFalse(
            SdoUri(Literal(f"{constants.SCHEMA_PREFIX}:Person")).is_sdo()
        )

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

    def test_relative_paths_and_path_property(self) -> None:
        for raw in ("/docs/collab/rNews", "docs/collab/rNews"):
            sdo = SdoUri(raw)
            self.assertTrue(sdo.is_sdo())
            self.assertEqual(str(sdo), "https://schema.org/docs/collab/rNews")
            self.assertEqual(sdo.path, "/docs/collab/rNews")
            self.assertEqual(sdo.term_name(), "docs/collab/rNews")

        self.assertEqual(SdoUri("Person").path, "/Person")
        self.assertEqual(SdoUri.for_layer("pending").path, "")
        self.assertEqual(
            SdoUri("http://xmlns.com/foaf/0.1/Person").path,
            "/foaf/0.1/Person",
        )

    def test_from_path(self) -> None:
        collab = SdoUri.from_path(Domain.DOCS_COLLAB, "rNews")
        self.assertTrue(collab.is_sdo())
        self.assertEqual(str(collab), "https://schema.org/docs/collab/rNews")
        self.assertEqual(collab.path, "/docs/collab/rNews")
        self.assertEqual(
            collab.uri, URIRef("https://schema.org/docs/collab/rNews")
        )

        # POSIX semantics: an absolute segment overrides earlier segments.
        overridden = SdoUri.from_path(Domain.DOCS_COLLAB, "/tmp/test")
        self.assertEqual(str(overridden), "https://schema.org/tmp/test")
        self.assertEqual(overridden.path, "/tmp/test")

        # Root and leading double-slash still resolve under schema.org.
        self.assertEqual(str(SdoUri.from_path()), constants.SCHEMA_URI)
        self.assertEqual(SdoUri.from_path().path, "/")
        dbl = SdoUri.from_path("//example.com/foo")
        self.assertTrue(dbl.is_sdo())
        self.assertEqual(str(dbl), "https://schema.org/example.com/foo")
        self.assertEqual(dbl.path, "/example.com/foo")

    def test_equality_and_hashing(self) -> None:
        self.assertEqual(SdoUri("Person"), SdoUri(SDO.Person))
        self.assertEqual(hash(SdoUri("Person")), hash(SdoUri(SDO.Person)))
        self.assertEqual(len({SdoUri("Person"), SdoUri(SDO.Person)}), 1)
        self.assertNotEqual(SdoUri("Person"), SdoUri(Literal("Person")))
        self.assertNotEqual(
            SdoUri("https://schema.org/Person"),
            SdoUri(Literal("https://schema.org/Person")),
        )
        self.assertNotEqual(SdoUri("Person"), "https://schema.org/Person")


if __name__ == "__main__":
    unittest.main()
