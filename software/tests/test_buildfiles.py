from __future__ import annotations

import logging
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import rdflib
from schemaorg.layout import OutputLayout, Protocol, Releases, Scope
from schemaorg.version import VersionItem
import scripts.buildfiles as buildfiles
import util.fileutils as fileutils
import util.schema as schema
from util.sdoowl import OwlBuild


class TestBuildFiles(unittest.TestCase):
    def testProtocolSwapEmpty(self) -> None:
        self.assertEqual(
            buildfiles.protocolSwap(content="", protocol="http", altprotocol="https"),
            "",
        )
        self.assertEqual(
            buildfiles.protocolSwap(
                content="Defined in http://schema.org and http://bib.schema.org",
                protocol="http",
                altprotocol="ftp",
            ),
            "Defined in ftp://schema.org and ftp://bib.schema.org",
        )

    def testProtocols(self) -> None:
        self.assertEqual(sorted(buildfiles.protocols()), ["http", "https"])

    def testUriWrap(self) -> None:
        self.assertEqual(
            buildfiles.uriwrap("Credential"), "https://schema.org/Credential"
        )
        self.assertEqual(
            buildfiles.uriwrap("https://example.com/Bogus"), "https://example.com/Bogus"
        )
        self.assertEqual(
            buildfiles.uriwrap(["Person", "Thing"]),
            "https://schema.org/Person, https://schema.org/Thing",
        )

    @patch("scripts.buildfiles.paths.DefaultOutputLayout")
    def testWriteCsvOut(self, mock_output_layout) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output_layout = OutputLayout(Path(temp_dir))
            mock_output_layout.return_value = output_layout
            buildfiles.writecsvout(
                ftype="properties",
                data=(
                    {"id": "123", "value": "http://schema.org/Fnuble"},
                    {"id": "456", "value": "Blubrl"},
                ),
                fields=("id", "value"),
                selector=fileutils.FileSelector.CURRENT,
                protocol="http",
                altprotocol="https",
            )

            releases = Releases(output_layout, schema.VERSION)
            http_csv = releases.file(
                protocol=Protocol.HTTP,
                scope=Scope.CURRENT,
                extension="-properties.csv",
            )
            https_csv = releases.file(
                protocol=Protocol.HTTPS,
                scope=Scope.CURRENT,
                extension="-properties.csv",
            )
            self.assertEqual(
                http_csv.read_text(encoding="utf-8"),
                '"id","value"\n"123","http://schema.org/Fnuble"\n"456","Blubrl"\n',
            )
            self.assertEqual(
                https_csv.read_text(encoding="utf-8"),
                '"id","value"\n"123","https://schema.org/Fnuble"\n"456","Blubrl"\n',
            )

    def testOwlBuildHandlesNextWithoutDate(self) -> None:
        empty_graph = rdflib.Graph()
        dated = OwlBuild(
            version=VersionItem("30.1", "2026-09-16"), graph=empty_graph
        ).getContent()
        self.assertIn("released: 2026-09-16", dated)
        self.assertIn("dcterms:modified", dated)

        unreleased = OwlBuild(
            version=VersionItem("next"), graph=empty_graph
        ).getContent()
        self.assertIn("Generated from Schema.org version: next", unreleased)
        self.assertNotIn("released:", unreleased)
        self.assertNotIn("None", unreleased)
        self.assertNotIn("dcterms:modified", unreleased)
        self.assertIn("<owl:versionInfo", unreleased)

    @patch(
        "SchemaTerms.sdotermsource.SdoTermSource.getAllTerms",
        return_value=["Person"],
    )
    def testSitemapOmitsLastmodWithoutDate(self, _mock_terms) -> None:
        dated = buildfiles.sitemap("Sitemap", version=VersionItem("30.1", "2026-09-16"))
        self.assertIn("<lastmod>2026-09-16</lastmod>", dated)

        unreleased = buildfiles.sitemap("Sitemap", version=VersionItem("next"))
        self.assertNotIn("<lastmod>", unreleased)
        self.assertIn("<loc>https://schema.org/Person</loc>", unreleased)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
