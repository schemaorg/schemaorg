#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Unit tests for schemaorg.graph_loader."""

from pathlib import Path
import tempfile
import unittest

import rdflib

from schemaorg import constants
from schemaorg.graph_loader import GraphLoader
from schemaorg.layout import Domain, InputLayout, Issues


class TestGraphLoader(unittest.TestCase):
    """Test suite for GraphLoader."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.layout = InputLayout(self.root)
        self.issues = Issues(self.layout)
        self.loader = GraphLoader()

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_no_files(self):
        self.assertEqual(len(self.loader.load([])), 0)

    def test_load_custom_namespaces_merged(self):
        data_dir = self.layout.dir(Domain.DATA)
        ext_dir = data_dir / "ext" / "pending"
        ext_dir.mkdir(parents=True, exist_ok=True)

        core_ttl = data_dir / "schema.ttl"
        core_ttl.write_text(
            "@prefix : <https://schema.org/> .\n"
            "@prefix custom1: <https://example.org/custom1#> .\n"
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
            ":Thing a rdfs:Class ;\n"
            "    custom1:prop \"value1\" .\n",
            encoding="utf-8",
        )

        issue_ttl = ext_dir / "issue-999.ttl"
        issue_ttl.write_text(
            "@prefix : <https://schema.org/> .\n"
            "@prefix custom2: <https://example.org/custom2#> .\n"
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
            ":SpecialThing a rdfs:Class ;\n"
            "    custom2:prop \"value2\" .\n",
            encoding="utf-8",
        )

        graph = self.loader.load(self.issues.get_ttl_files(issues=["999"]))
        ns = dict(graph.namespaces())
        self.assertEqual(set(ns), {"", "custom1", "custom2", "rdfs"})

        # Verify custom namespaces from files were merged
        self.assertIn("custom1", ns)
        self.assertEqual(str(ns["custom1"]), "https://example.org/custom1#")
        self.assertIn("custom2", ns)
        self.assertEqual(str(ns["custom2"]), "https://example.org/custom2#")

        self.assertIn("", ns)
        self.assertEqual(str(ns[""]), "https://schema.org/")

        # Verify triples from both files are in the graph
        thing_uri = rdflib.URIRef("https://schema.org/Thing")
        special_uri = rdflib.URIRef("https://schema.org/SpecialThing")
        self.assertIn((thing_uri, rdflib.RDF.type, rdflib.RDFS.Class), graph)
        self.assertIn((special_uri, rdflib.RDF.type, rdflib.RDFS.Class), graph)

    def test_load_issue_filtering(self):
        data_dir = self.layout.dir(Domain.DATA)
        ext_dir = data_dir / "ext" / "pending"
        ext_dir.mkdir(parents=True, exist_ok=True)

        core_ttl = data_dir / "schema.ttl"
        core_ttl.write_text(
            "@prefix : <https://schema.org/> .\n"
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
            ":Core a rdfs:Class .\n",
            encoding="utf-8",
        )

        issue1 = ext_dir / "issue-1.ttl"
        issue1.write_text(
            "@prefix : <https://schema.org/> .\n"
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
            ":Issue1Class a rdfs:Class .\n",
            encoding="utf-8",
        )

        issue2 = ext_dir / "issue-2.ttl"
        issue2.write_text(
            "@prefix : <https://schema.org/> .\n"
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
            ":Issue2Class a rdfs:Class .\n",
            encoding="utf-8",
        )

        # Loading only issue 1
        g = self.loader.load(self.issues.get_ttl_files(issues=["1"]))
        core_uri = rdflib.URIRef("https://schema.org/Core")
        issue1_uri = rdflib.URIRef("https://schema.org/Issue1Class")
        issue2_uri = rdflib.URIRef("https://schema.org/Issue2Class")

        self.assertIn((core_uri, rdflib.RDF.type, rdflib.RDFS.Class), g)
        self.assertIn((issue1_uri, rdflib.RDF.type, rdflib.RDFS.Class), g)
        self.assertNotIn((issue2_uri, rdflib.RDF.type, rdflib.RDFS.Class), g)

        # Loading with default issues (ALL_ISSUES)
        g_all = self.loader.load(self.issues.get_ttl_files())
        self.assertIn((core_uri, rdflib.RDF.type, rdflib.RDFS.Class), g_all)
        self.assertIn((issue1_uri, rdflib.RDF.type, rdflib.RDFS.Class), g_all)
        self.assertIn((issue2_uri, rdflib.RDF.type, rdflib.RDFS.Class), g_all)

    def test_load_parse_error_raises(self):
        data_dir = self.layout.dir(Domain.DATA)
        data_dir.mkdir(parents=True, exist_ok=True)
        bad_ttl = data_dir / "schema.ttl"
        bad_ttl.write_text("THIS IS NOT VALID TURTLE !!!", encoding="utf-8")

        with self.assertLogs(level="WARNING"):
            with self.assertRaises(Exception):
                self.loader.load(self.issues.get_ttl_files())

    def test_load_real_data_single_issue(self):
        real_issues = Issues(InputLayout(constants.PROJECT_ROOT))
        g = self.loader.load(real_issues.get_ttl_files(issues=["1062"]))

        self.assertGreater(len(g), 1000)
        ns = dict(g.namespaces())
        self.assertEqual(str(ns.get("")), "https://schema.org/")
        self.assertEqual(str(ns.get("dc")), "http://purl.org/dc/terms/")
        self.assertIn("cmns-cls", ns)
        self.assertIn("fibo-be-corp-corp", ns)

        # 1062 term exists
        plan_uri = rdflib.URIRef("https://schema.org/HealthInsurancePlan")
        self.assertIn((plan_uri, rdflib.RDF.type, rdflib.RDFS.Class), g)


if __name__ == "__main__":
    unittest.main()
