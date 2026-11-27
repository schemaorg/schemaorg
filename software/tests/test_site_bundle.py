from __future__ import annotations

import json
import logging
from pathlib import Path
import tempfile
import unittest

from schemaorg.layout import Domain, InputLayout, OutputLayout, Releases
from schemaorg.progress import LogProgressReporter, NullProgressReporter
from schemaorg.site_bundle import SiteBundle
from schemaorg.version import Version, VersionItem


class TestSiteBundle(unittest.TestCase):
    def setUp(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.root = Path(temp_dir.name)
        self.layout = InputLayout(self.root)

        versions_path = self.root / "versions.json"
        versions_path.write_text(
            json.dumps({
                "schemaversion": "30.1",
                "releaseLog": {"30.1": "2026-09-16"},
            }),
            encoding="utf-8",
        )
        self.version = Version(versions_path)

        data_dir = self.layout.dir(Domain.DATA)
        data_dir.mkdir(parents=True)
        (data_dir / "examples.txt").write_text(
            'TYPES: #eg-1 Person\nPRE-MARKUP:\nAda\nJSON:\n{"@type": "Person"}\n',
            encoding="utf-8",
        )
        collab_dir = data_dir / "collab"
        collab_dir.mkdir()
        (collab_dir / "rNews.md").write_text(
            "---\ntitle: rNews\nurl: https://iptc.org\n--- DescriptionText.md\nNews.\n",
            encoding="utf-8",
        )
        stats_dir = self.layout.dir(Domain.PUBLIC_STATS) / "commoncrawl"
        stats_dir.mkdir(parents=True)
        (stats_dir / "stats_2026_09.json").write_text(
            json.dumps([{
                "Name": "https://schema.org/Person",
                "Domain Bucket": "Over 1,000,000 domains",
            }]),
            encoding="utf-8",
        )

    def _write_release_ttl(
        self, releases: Releases, version: VersionItem | None = None
    ) -> Path:
        ttl_path = releases.file(version or self.version.next())
        ttl_path.parent.mkdir(parents=True, exist_ok=True)
        ttl_path.write_text(
            "@prefix : <https://schema.org/> .\n"
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
            ':Thing a rdfs:Class ; rdfs:label "Thing" ; rdfs:comment "Generic." .\n'
            ':Person a rdfs:Class ; rdfs:label "Person" ; rdfs:subClassOf :Thing ; '
            ':contributor <https://schema.org/docs/collab/rNews> .\n',
            encoding="utf-8",
        )
        return ttl_path

    def test_from_release_loads_all_stage2_inputs(self) -> None:
        releases_out = OutputLayout(self.root / "data")
        ttl_path = self._write_release_ttl(Releases(releases_out, self.version))

        logger = logging.getLogger("test.bundle")
        reporter = LogProgressReporter(logger=logger, log_steps=True)
        with self.assertLogs(logger, level=logging.INFO) as captured:
            bundle = SiteBundle.from_release(
                input_layout=self.layout,
                releases_layout=releases_out,
                target_version=self.version.next(),
                progress=reporter,
            )

        self.assertEqual(bundle.release_file, ttl_path)
        self.assertEqual(bundle.target_version.number(), "next")
        self.assertEqual(bundle.current_version.number(), "30.1")
        self.assertIsNotNone(bundle.catalog.get("Person"))
        self.assertEqual(len(bundle.examples.examplesForTerm("Person")), 1)
        self.assertEqual(len(bundle.stats_providers), 1)
        self.assertIn("(6/6 steps)", "\n".join(captured.output))

    def test_from_release_uses_precomputed_jsonld_when_present(self) -> None:
        releases_out = OutputLayout(self.root / "data")
        releases = Releases(releases_out, self.version)
        self._write_release_ttl(releases)
        jsonld_path = releases.file(self.version.next(), extension=".jsonld")
        jsonld_path.write_text(
            json.dumps({
                "@context": {"schema": "https://schema.org/"},
                "@graph": [{
                    "@id": "schema:Person",
                    "@type": "rdfs:Class",
                    "rdfs:label": "PrecomputedPerson",
                }],
            }),
            encoding="utf-8",
        )

        bundle = SiteBundle.from_release(
            input_layout=self.layout,
            releases_layout=releases_out,
            target_version=self.version.next(),
            progress=NullProgressReporter(),
        )
        person = bundle.catalog.get("Person")
        self.assertIsNotNone(person)
        assert person is not None
        self.assertIn(
            "PrecomputedPerson", bundle.jsonld_index.render_for(person)
        )

    def test_missing_release_file_raises_without_creating_output_dirs(
        self,
    ) -> None:
        fresh_out = self.root / "fresh_out"
        with self.assertRaises(FileNotFoundError):
            SiteBundle.from_release(
                input_layout=self.layout,
                releases_layout=OutputLayout(fresh_out),
                target_version=self.version.next(),
                progress=NullProgressReporter(),
            )
        self.assertFalse(fresh_out.exists())

    def test_resolves_target_version_before_output_layout_guard(self) -> None:
        fresh_out = self.root / "undeclared_out"
        with self.assertRaises(ValueError):
            SiteBundle.from_release(
                input_layout=self.layout,
                releases_layout=OutputLayout(fresh_out),
                target_version=VersionItem("99.9", "2099-01-01"),
                progress=NullProgressReporter(),
            )
        self.assertFalse(fresh_out.exists())

        releases_out = OutputLayout(self.root / "data")
        self._write_release_ttl(
            Releases(releases_out, self.version), self.version.current()
        )
        bundle = SiteBundle.from_release(
            input_layout=self.layout,
            releases_layout=releases_out,
            target_version=VersionItem("30.1", "2000-01-01"),
            progress=NullProgressReporter(),
        )
        self.assertEqual(bundle.target_version.date(), "2026-09-16")


if __name__ == "__main__":
    unittest.main()
