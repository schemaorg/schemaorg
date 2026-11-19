from __future__ import annotations

import json
import logging
from pathlib import Path
import tempfile
import unittest

from schemaorg.layout import Domain, InputLayout, OutputLayout, Releases
from schemaorg.progress import LogProgressReporter, NullProgressReporter
from schemaorg.site_bundle import SiteBundle
from schemaorg.tasks.render_docs_pages import RenderDocsPagesTask
from schemaorg.version import Version


class TestRenderDocsPagesTask(unittest.TestCase):
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

        docs_templates = self.input_layout.dir(Domain.TEMPLATES) / "docs"
        docs_templates.mkdir(parents=True)
        (docs_templates / "Home.j2").write_text(
            "<h1>{{ title }}</h1>", encoding="utf-8"
        )
        (docs_templates / "Schemas.j2").write_text(
            "Count={{ termcounts.Type }}", encoding="utf-8"
        )
        (docs_templates / "Full.j2").write_text(
            "{% for n in listings %}{{ n.id }}{% endfor %}",
            encoding="utf-8",
        )

        data_dir = self.input_layout.dir(Domain.DATA)
        data_dir.mkdir(parents=True)

        releases = Releases(self.input_layout, self.version)
        ttl_path = releases.file(self.version.next())
        ttl_path.parent.mkdir(parents=True)
        ttl_path.write_text(
            "@prefix : <https://schema.org/> .\n"
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
            ':Thing a rdfs:Class ; rdfs:label "Thing" .\n'
            ':DataType a rdfs:Class ; rdfs:label "DataType" .\n',
            encoding="utf-8",
        )
        self.bundle = SiteBundle.from_release(
            input_layout=self.input_layout,
            releases_layout=self.input_layout,
            target_version=self.version.next(),
            progress=NullProgressReporter(),
        )

    def test_renders_selected_docs_pages_and_termfind(self) -> None:
        logger = logging.getLogger("test.render_docs")
        reporter = LogProgressReporter(logger=logger, log_steps=True)
        out = OutputLayout(self.out_dir)

        with self.assertLogs(logger, level=logging.INFO) as captured:
            written = RenderDocsPagesTask(
                bundle=self.bundle,
                output_layout=out,
                build_opts=(),
                page_names=("Home", "Schemas", "Full", "TermFind"),
                progress=reporter,
            ).run()

        self.assertEqual(written, 4)
        self.assertEqual(
            out.file(Domain.DOCS, "home.html").read_text(encoding="utf-8"),
            "<h1>Schema.org</h1>",
        )
        self.assertEqual(
            out.file(Domain.DOCS, "schemas.html").read_text(encoding="utf-8"),
            "Count=1",
        )
        self.assertEqual(
            out.file(Domain.DOCS, "full.html").read_text(encoding="utf-8"),
            "ThingDataType",
        )
        self.assertIn(
            "Thing t\n",
            out.file(Domain.DOCS_TERMFIND, "termlist.txt").read_text(
                encoding="utf-8"
            ),
        )
        self.assertIn("(4/4 pages)", "\n".join(captured.output))


if __name__ == "__main__":
    unittest.main()
