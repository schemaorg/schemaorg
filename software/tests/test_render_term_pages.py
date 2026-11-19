from __future__ import annotations

import json
import logging
from pathlib import Path
import tempfile
import unittest

from schemaorg.layout import Domain, InputLayout, OutputLayout, Releases
from schemaorg.progress import LogProgressReporter, NullProgressReporter
from schemaorg.site_bundle import SiteBundle
from schemaorg.tasks.render_term_pages import (
    RenderTermPagesTask,
    term_output_path,
)
from schemaorg.version import Version


class TestRenderTermPagesTask(unittest.TestCase):
    def setUp(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.root = Path(temp_dir.name)
        self.in_dir = self.root / "in"
        self.out_dir = self.root / "site"
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

        templates_dir = self.input_layout.dir(Domain.TEMPLATES) / "terms"
        templates_dir.mkdir(parents=True)
        (templates_dir / "TermPage.j2").write_text(
            "<h1>{{ term.id }}</h1>"
            "<p>V{{ version }}</p>"
            "{% for ex in examples %}<span>{{ ex.getKey() }}</span>{% endfor %}"
            "{% for b in stats_badges %}<b>{{ b.badge }}</b>{% endfor %}",
            encoding="utf-8",
        )

        data_dir = self.input_layout.dir(Domain.DATA)
        data_dir.mkdir(parents=True)
        (data_dir / "examples.txt").write_text(
            'TYPES: #eg-7 Person\nPRE-MARKUP:\nAda\nJSON:\n{"@type": "Person"}\n',
            encoding="utf-8",
        )
        stats_dir = self.input_layout.dir(Domain.PUBLIC_STATS) / "commoncrawl"
        stats_dir.mkdir(parents=True)
        (stats_dir / "stats_2026_09.json").write_text(
            json.dumps([{
                "Name": "https://schema.org/Person",
                "Domain Bucket": "10k-100k",
            }]),
            encoding="utf-8",
        )

        releases = Releases(self.input_layout, self.version)
        ttl_path = releases.file(self.version.next())
        ttl_path.parent.mkdir(parents=True)
        ttl_path.write_text(
            "@prefix : <https://schema.org/> .\n"
            "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
            ':Person a rdfs:Class ; rdfs:label "Person" .\n'
            ':name a rdf:Property ; rdfs:label "name" ; :domainIncludes :Person .\n',
            encoding="utf-8",
        )
        self.bundle = SiteBundle.from_release(
            input_layout=self.input_layout,
            releases_layout=self.input_layout,
            target_version=self.version.next(),
            progress=NullProgressReporter(),
        )

    def test_term_output_path_routes_types_and_properties(self) -> None:
        out = OutputLayout(self.out_dir)
        self.assertEqual(
            term_output_path(out, "Person"),
            self.out_dir.resolve() / "terms/types/P/Person.html",
        )
        self.assertEqual(
            term_output_path(out, "name"),
            self.out_dir.resolve() / "terms/properties/n/name.html",
        )
        self.assertEqual(
            term_output_path(out, "3DModel"),
            self.out_dir.resolve() / "terms/types/3/3DModel.html",
        )
        with self.assertRaises(ValueError):
            term_output_path(out, "")

    def test_renders_all_terms_with_examples_and_stats(self) -> None:
        logger = logging.getLogger("test.render_terms")
        reporter = LogProgressReporter(logger=logger, log_steps=True)
        out = OutputLayout(self.out_dir)
        with self.assertLogs(logger, level=logging.INFO) as captured:
            count = RenderTermPagesTask(
                bundle=self.bundle,
                output_layout=out,
                build_opts=(),
                term_ids=("ALL",),
                progress=reporter,
            ).run()

        self.assertEqual(count, 2)
        person_html = (out.output_dir / "terms/types/P/Person.html").read_text(
            encoding="utf-8"
        )
        self.assertIn("<h1>Person</h1>", person_html)
        self.assertIn("<p>Vnext</p>", person_html)
        self.assertIn("<span>eg-0007</span>", person_html)
        self.assertIn("<b>10k-100k</b>", person_html)
        self.assertTrue(
            (out.output_dir / "terms/properties/n/name.html").is_file()
        )
        self.assertIn("(2/2 pages)", "\n".join(captured.output))


if __name__ == "__main__":
    unittest.main()
