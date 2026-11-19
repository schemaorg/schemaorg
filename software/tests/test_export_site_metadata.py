from __future__ import annotations

import json
import logging
from pathlib import Path
import tempfile
import unittest

import rdflib

from schemaorg.layout import Domain, InputLayout, OutputLayout, Releases
from schemaorg.model import VocabularyLoader
from schemaorg.progress import LogProgressReporter
from schemaorg.tasks.export_site_metadata import ExportSiteMetadataTask
from schemaorg.version import Version


class TestExportSiteMetadataTask(unittest.TestCase):
    def setUp(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.root = Path(temp_dir.name)
        self.in_dir = self.root / "in"
        self.site_dir = self.root / "site"
        self.in_dir.mkdir()

        versions_path = self.in_dir / "versions.json"
        versions_path.write_text(
            json.dumps({
                "schemaversion": "30.1",
                "releaseLog": {"30.1": "2026-09-16"},
            }),
            encoding="utf-8",
        )
        self.version = Version(versions_path)
        self.input_layout = InputLayout(self.in_dir)
        releases = Releases(self.input_layout, self.version)
        ctx_path = releases.file(
            self.version.next(), filename="schemaorgcontext.jsonld"
        )
        ctx_path.parent.mkdir(parents=True)
        ctx_path.write_text('{"@context": {}}', encoding="utf-8")
        releases.file(
            self.version.next(), filename="schemaorg.owl"
        ).write_text("<rdf:RDF/>", encoding="utf-8")

        graph = rdflib.Graph()
        graph.parse(
            data=(
                "@prefix : <https://schema.org/> .\n"
                "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
                ':Thing a rdfs:Class ; rdfs:label "Thing" .\n'
            ),
            format="turtle",
        )
        self.vocab = VocabularyLoader(graph, version=self.version.next()).load()

    def test_writes_all_8_site_metadata_files(self) -> None:
        logger = logging.getLogger("test.export_site_metadata")
        reporter = LogProgressReporter(logger=logger, log_steps=True)
        out_layout = OutputLayout(self.site_dir)
        with self.assertLogs(logger, level=logging.INFO) as captured:
            written = ExportSiteMetadataTask(
                input_layout=self.input_layout,
                output_layout=out_layout,
                version=self.version.next(),
                vocab=self.vocab,
                progress=reporter,
            ).run()

        self.assertEqual(len(written), 8)
        self.assertTrue(all(p.is_file() for p in written))
        self.assertEqual(
            out_layout.file(Domain.DOCS, "jsonldcontext.jsonld").read_text(
                encoding="utf-8"
            ),
            '{"@context": {}}',
        )
        self.assertIn("(8/8 files)", "\n".join(captured.output))


if __name__ == "__main__":
    unittest.main()
