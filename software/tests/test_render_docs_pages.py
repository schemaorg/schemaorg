from __future__ import annotations

import logging
from pathlib import Path
import tempfile
import unittest

from schemaorg.layout import Domain, OutputLayout
from schemaorg.progress import LogProgressReporter, NullProgressReporter
from schemaorg.tasks.render_docs_pages import (
    ListingNode,
    RenderDocsPagesTask,
)
from schemaorg.testing import build_site_fixture

_FIXTURE_TTL = (
    "@prefix : <https://schema.org/> .\n"
    "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
    "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
    ':Thing a rdfs:Class ; rdfs:label "Thing" .\n'
    ':DataType a rdfs:Class ; rdfs:label "DataType" ; rdfs:subClassOf rdfs:Class .\n'
    ':Text a :DataType, rdfs:Class ; rdfs:label "Text" .\n'
    ':Org a rdfs:Class ; rdfs:label "Org" ; rdfs:subClassOf :Thing .\n'
    ':Place a rdfs:Class ; rdfs:label "Place" ; rdfs:subClassOf :Thing .\n'
    ':LocalBiz a rdfs:Class ; rdfs:label "LocalBiz" ; rdfs:subClassOf :Org, :Place ;\n'
    '    :isPartOf <https://pending.schema.org> ; :source <https://github.com/schemaorg/schemaorg/issues/123> .\n'
    ':name a rdf:Property ; rdfs:label "name" ; :domainIncludes :Thing ; :rangeIncludes :Text .\n'
)


class TestRenderDocsPagesTask(unittest.TestCase):
    def setUp(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.root = Path(temp_dir.name)
        self.out_dir = self.root / "site"
        _, self.bundle, _ = build_site_fixture(
            self.root,
            _FIXTURE_TTL,
            templates={
                "docs/Home.j2": "<h1>{{ title }}</h1>",
                "docs/PendingHome.j2": (
                    "{{ title }}:{{ termcount }}:"
                    "{% for cat in sectionterms %}{{ cat }}{% endfor %}"
                ),
                "docs/Schemas.j2": "Count={{ termcounts.Type }}",
                "docs/Full.j2": "{% for n in listings %}{{ n.id }}{% endfor %}",
                "docs/FullRelease.j2": "{{ version }}|{{ date }}|{{ types|length }}|{{ properties|length }}",
            },
        )

    def test_renders_docs_pages_pending_grouping_termfind_and_edge_cases(
        self,
    ) -> None:
        out = OutputLayout(self.out_dir)
        self.assertEqual(
            RenderDocsPagesTask(
                bundle=self.bundle,
                output_layout=out,
                build_opts=(),
                page_names=("",),
                progress=NullProgressReporter(),
            ).run(),
            0,
        )

        logger = logging.getLogger("test.render_docs")
        reporter = LogProgressReporter(logger=logger, log_steps=True)
        with self.assertLogs(logger, level=logging.INFO) as captured:
            written = RenderDocsPagesTask(
                bundle=self.bundle,
                output_layout=out,
                build_opts=(),
                page_names=(
                    "Home",
                    "PendingHome",
                    "Schemas",
                    "Full",
                    "FullRelease",
                    "TermFind",
                    "NoSuchPage",
                ),
                progress=reporter,
            ).run()

        self.assertEqual(written, 6)
        self.assertEqual(
            out.file(Domain.DOCS, "home.html").read_text(encoding="utf-8"),
            "<h1>Schema.org</h1>",
        )
        self.assertEqual(
            out.file(Domain.DOCS, "pending.home.html").read_text(
                encoding="utf-8"
            ),
            "Pending:1:issue-123",
        )
        self.assertEqual(
            out.file(Domain.DOCS, "fullrelease.html").read_text(
                encoding="utf-8"
            ),
            "next|Unreleased|6|1",
        )
        self.assertIn(
            "Thing t\n",
            out.file(Domain.DOCS_TERMFIND, "termlist.txt").read_text(
                encoding="utf-8"
            ),
        )
        joined = "\n".join(captured.output)
        self.assertIn("Unknown or missing page name: NoSuchPage", joined)
        self.assertIn("(7/7 pages)", joined)

        # Diamond inheritance marks second occurrence repeat=True.
        thing_view = self.bundle.catalog.get("Thing")
        assert thing_view is not None
        root_node = ListingNode.from_term(thing_view, "Types:", set())
        org_biz = root_node.subs[0].subs[0]
        place_biz = root_node.subs[1].subs[0]
        self.assertFalse(org_biz.repeat)
        self.assertTrue(place_biz.repeat)

        # notermfinder suppresses TermFind output.
        RenderDocsPagesTask(
            bundle=self.bundle,
            output_layout=out,
            build_opts=("notermfinder",),
            page_names=("TermFind",),
            progress=NullProgressReporter(),
        ).run()
        self.assertEqual(
            out.file(Domain.DOCS_TERMFIND, "termlist.txt").read_text(
                encoding="utf-8"
            ),
            "",
        )

    def test_real_docs_templates_render_cleanly(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            _, real_bundle, _ = build_site_fixture(
                tmp_root,
                _FIXTURE_TTL,
                use_real_templates=True,
                version_ref="30.1",
            )
            out = OutputLayout(tmp_root / "site")
            pages = ("Home", "Schemas", "Full", "FullRelease", "PendingHome")
            written = RenderDocsPagesTask(
                bundle=real_bundle,
                output_layout=out,
                build_opts=(),
                page_names=pages,
                progress=NullProgressReporter(),
            ).run()
            self.assertEqual(written, len(pages))
            self.assertIn(
                "2026-09-16",
                out.file(Domain.DOCS, "fullrelease.html").read_text(
                    encoding="utf-8"
                ),
            )
            self.assertIn(
                "LocalBiz",
                out.file(Domain.DOCS, "pending.home.html").read_text(
                    encoding="utf-8"
                ),
            )


if __name__ == "__main__":
    unittest.main()
