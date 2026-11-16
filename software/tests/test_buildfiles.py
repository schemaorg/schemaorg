from __future__ import annotations

import json
import logging
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import rdflib
from schemaorg.layout import (
    Domain,
    InputLayout,
    OutputLayout,
    Protocol,
    Releases,
    Scope,
)
from schemaorg.version import Version, VersionItem
import SchemaTerms.sdotermsource as sdotermsource
import scripts.buildfiles as buildfiles
import util.fileutils as fileutils
import util.schema as schema
from util.sdoowl import OwlBuild

FIXTURE_TTL = """\
@prefix : <https://schema.org/> .
@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .

:Thing a rdfs:Class ;
    rdfs:label "Thing" ;
    rdfs:comment "The most generic type." .

:DataType a rdfs:Class ;
    rdfs:subClassOf rdfs:Class ;
    rdfs:label "DataType" ;
    rdfs:comment "Basic data types." .

:Text a :DataType, rdfs:Class ;
    rdfs:label "Text" ;
    rdfs:comment "Data type: Text." .

:Person a rdfs:Class ;
    rdfs:subClassOf :Thing ;
    rdfs:label "Person" ;
    rdfs:comment "A person." .

:name a rdf:Property ;
    rdfs:label "name" ;
    rdfs:comment "The name of the item." ;
    :domainIncludes :Thing ;
    :rangeIncludes :Text .
"""


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

    def testExportReleaseFilesAndSiteDocsWithLayouts(self) -> None:
        self.addCleanup(
            sdotermsource.SdoTermSource.loadSourceGraph, "default", init=True
        )
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            in_dir = root / "in"
            site_dir = root / "site"
            (in_dir / "data").mkdir(parents=True)
            (in_dir / "versions.json").write_text(
                json.dumps(
                    {
                        "schemaversion": "30.1",
                        "releaseLog": {"30.1": "2026-09-16"},
                    }
                ),
                encoding="utf-8",
            )
            (in_dir / "data" / "schema.ttl").write_text(
                FIXTURE_TTL, encoding="utf-8"
            )
            input_layout = InputLayout(in_dir)
            release_out_layout = OutputLayout(in_dir / "data")
            site_out_layout = OutputLayout(site_dir)

            stale = release_out_layout.file(Domain.RELEASE, "next/stale.txt")
            stale.write_text("obsolete", encoding="utf-8")

            buildfiles.export_release_files(
                input_layout=input_layout, output_layout=release_out_layout
            )

            self.assertFalse((in_dir / "data" / "docs").exists())
            self.assertFalse(stale.exists())

            releases = Releases(
                release_out_layout, Version(in_dir / "versions.json")
            )
            self.assertEqual(len(list(releases.dir("next").iterdir())), 35)
            https_nq = releases.file(filename="schemaorg-all-https.nq").read_text(
                encoding="utf-8"
            )
            self.assertIn("<https://schema.org/next> .", https_nq)

            buildfiles.export_site_docs(
                input_layout=input_layout, output_layout=site_out_layout
            )
            for name in (
                "jsoncounts.json",
                "jsonpcounts.js",
                "sitemap.xml",
                "tree.jsonld",
                "schemaorg.owl",
                "jsonldcontext.jsonld",
                "jsonldcontext.json",
                "jsonldcontext.json.txt",
            ):
                self.assertTrue(
                    site_out_layout.file(Domain.DOCS, name).is_file(), name
                )
            self.assertFalse((site_dir / "releases").exists())

            buildfiles.export_release_files(
                input_layout=input_layout,
                output_layout=release_out_layout,
                version="30.1",
            )
            self.assertTrue(releases.file("30.1", filename="schemaorg.owl").is_file())


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
