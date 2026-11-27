from __future__ import annotations

import logging
from pathlib import Path
import tempfile
import unittest

from schemaorg.layout import OutputLayout
from schemaorg.progress import LogProgressReporter, NullProgressReporter
from schemaorg.tasks.render_term_pages import (
    RenderTermPagesTask,
    term_output_path,
)
from schemaorg.testing import build_site_fixture

_FIXTURE_TTL = (
    "@prefix : <https://schema.org/> .\n"
    "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
    "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
    ':Thing a rdfs:Class ; rdfs:label "Thing" .\n'
    ':Person a rdfs:Class ; rdfs:label "Person" ; rdfs:subClassOf :Thing .\n'
    ':name a rdf:Property ; rdfs:label "name" ; :domainIncludes :Person .\n'
)
_FIXTURE_EXAMPLES = (
    "TYPES: #eg-7 Person\n"
    "PRE-MARKUP:\nAda & Grace\n"
    'JSON:\n{"@type": "Person", "name": "Ada & Grace"}\n'
)


class TestRenderTermPagesTask(unittest.TestCase):
    def setUp(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.root = Path(temp_dir.name)
        self.out_dir = self.root / "site"
        _, self.bundle, _ = build_site_fixture(
            self.root,
            _FIXTURE_TTL,
            templates={
                "terms/TermPage.j2": (
                    "<h1>{{ term.id }}</h1>"
                    "<p>V{{ version }}</p>"
                    "{% for ex in examples %}<span>{{ ex.getKey() }}:{{ ex.getHtml() }}</span>{% endfor %}"
                    "{% for b in stats_badges %}<b>{{ b.badge }}</b>{% endfor %}"
                )
            },
            examples_txt=_FIXTURE_EXAMPLES,
            stats_json=[{
                "Name": "https://schema.org/Person",
                "Domain Bucket": "10k-100k",
            }],
        )

    def test_term_output_path_routes_types_properties_and_rejects_invalid(
        self,
    ) -> None:
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
        for bad in ("", "🟪"):
            with self.assertRaises(ValueError):
                term_output_path(out, bad)

    def test_renders_all_terms_handles_empty_and_unknown_terms(self) -> None:
        out = OutputLayout(self.out_dir)
        self.assertEqual(
            RenderTermPagesTask(
                bundle=self.bundle,
                output_layout=out,
                build_opts=(),
                term_ids=("",),
                progress=NullProgressReporter(),
            ).run(),
            0,
        )

        logger = logging.getLogger("test.render_terms")
        reporter = LogProgressReporter(logger=logger, log_steps=True)
        with self.assertLogs(logger, level=logging.INFO) as captured:
            count = RenderTermPagesTask(
                bundle=self.bundle,
                output_layout=out,
                build_opts=(),
                term_ids=("ALL",),
                progress=reporter,
            ).run()

        self.assertEqual(count, 3)
        person_html = (out.output_dir / "terms/types/P/Person.html").read_text(
            encoding="utf-8"
        )
        self.assertIn("<h1>Person</h1>", person_html)
        self.assertIn("Ada &amp; Grace", person_html)
        self.assertIn("<b>10k-100k</b>", person_html)
        self.assertTrue(
            (out.output_dir / "terms/properties/n/name.html").is_file()
        )
        self.assertIn("(3/3 pages)", "\n".join(captured.output))

        with self.assertLogs(logger, level=logging.ERROR) as err_logs:
            unknown_count = RenderTermPagesTask(
                bundle=self.bundle,
                output_layout=out,
                build_opts=(),
                term_ids=("NoSuchTerm",),
                progress=reporter,
            ).run()
        self.assertEqual(unknown_count, 0)
        self.assertIn("No such term: NoSuchTerm", "\n".join(err_logs.output))

    def test_real_term_page_template_escapes_examples_and_applies_build_opts(
        self,
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            _, real_bundle, _ = build_site_fixture(
                tmp_root,
                _FIXTURE_TTL,
                use_real_templates=True,
                examples_txt=_FIXTURE_EXAMPLES,
                version_ref="30.1",
            )
            out = OutputLayout(tmp_root / "site")
            written = RenderTermPagesTask(
                bundle=real_bundle,
                output_layout=out,
                build_opts=("goto",),
                term_ids=("Person",),
                progress=NullProgressReporter(),
            ).run()
            self.assertEqual(written, 1)
            html = (out.output_dir / "terms/types/P/Person.html").read_text(
                encoding="utf-8"
            )
            self.assertIn("Ada &amp; Grace", html)
            self.assertIn("jumpmenu.js", html)
            self.assertIn("30.1", html)
            self.assertNotIn("google-public-stats-badge-container", html)


if __name__ == "__main__":
    unittest.main()
