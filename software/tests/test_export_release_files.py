from __future__ import annotations

import json
import logging
from pathlib import Path
import tempfile
import unittest

from schemaorg.layout import Domain, InputLayout, OutputLayout
from schemaorg.progress import LogProgressReporter
from schemaorg.tasks.export_release_files import ExportReleaseFilesTask
from schemaorg.version import Version


class TestExportReleaseFilesTask(unittest.TestCase):
    def setUp(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.root = Path(temp_dir.name)
        self.in_dir = self.root / "in"
        self.out_dir = self.root / "out"
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

        data_dir = self.in_dir / Domain.DATA.value
        data_dir.mkdir()
        (data_dir / "schema.ttl").write_text(
            "@prefix : <https://schema.org/> .\n"
            "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
            ':Thing a rdfs:Class ; rdfs:label "Thing" ; rdfs:comment "Generic." .\n'
            ':OldThing a rdfs:Class ; rdfs:label "OldThing" ; :isPartOf <https://attic.schema.org> .\n'
            ':name a rdf:Property ; rdfs:label "name" ; :domainIncludes :Thing ; :rangeIncludes :Thing .\n',
            encoding="utf-8",
        )
        (data_dir / "examples.txt").write_text(
            'TYPES: #eg-1 Thing\nPRE-MARKUP:\nX\nJSON:\n{"@type": "Thing"}\n',
            encoding="utf-8",
        )

    def test_exports_9_next_release_files_and_cleans_stale_files(self) -> None:
        stale = self.out_dir / "data" / "releases" / "next" / "stale.txt"
        stale.parent.mkdir(parents=True)
        stale.write_text("remove me", encoding="utf-8")

        logger = logging.getLogger("test.export_release")
        reporter = LogProgressReporter(logger=logger, log_steps=False)
        with self.assertLogs(logger, level=logging.INFO) as captured:
            written = ExportReleaseFilesTask(
                input_layout=InputLayout(self.in_dir),
                output_layout=OutputLayout(self.out_dir / "data"),
                version=self.version.next(),
                progress=reporter,
            ).run()

        self.assertEqual(len(written), 9)
        self.assertTrue(all(p.is_file() for p in written))
        self.assertFalse(stale.exists())
        self.assertIn("(9/9 files)", "\n".join(captured.output))

    def test_exports_all_35_numbered_release_files(self) -> None:
        logger = logging.getLogger("test.export_release.numbered")
        reporter = LogProgressReporter(logger=logger, log_steps=False)
        with self.assertLogs(logger, level=logging.INFO) as captured:
            written = ExportReleaseFilesTask(
                input_layout=InputLayout(self.in_dir),
                output_layout=OutputLayout(self.out_dir / "data"),
                version=self.version.resolve("30.1"),
                progress=reporter,
            ).run()

        self.assertEqual(len(written), 35)
        self.assertTrue(all(p.is_file() for p in written))
        self.assertIn("(35/35 files)", "\n".join(captured.output))


if __name__ == "__main__":
    unittest.main()
