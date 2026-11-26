from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from rdflib import URIRef

from schemaorg import constants
from schemaorg.jsonld_slice import TermJsonLdIndex
from schemaorg.layout import InputLayout
from schemaorg.model import SchemaType, Vocabulary
from schemaorg.template_renderer import TemplateRenderer
from schemaorg.term_view import TermView, TermViewCatalog
from schemaorg.version import VersionItem
import SchemaExamples.schemaexamples as schemaexamples
import util.buildtermpages as buildtermpages
import util.schema as schema


class TestTermFileName(unittest.TestCase):
    def testEmpty(self) -> None:
        with self.assertRaises(ValueError):
            buildtermpages.termFileName("")

    def testUnicode(self) -> None:
        with self.assertRaises(ValueError):
            buildtermpages.termFileName("🟪")

    def testUpper(self) -> None:
        self.assertEqual(
            buildtermpages.termFileName("Thingamabob"),
            Path(schema.config.OUTPUTDIR).resolve() / "terms/types/T/Thingamabob.html",
        )

    def testLower(self) -> None:
        self.assertEqual(
            buildtermpages.termFileName("thingamabob"),
            Path(schema.config.OUTPUTDIR).resolve()
            / "terms/properties/t/thingamabob.html",
        )

    def testDigit(self) -> None:
        self.assertEqual(
            buildtermpages.termFileName("4DStatue"),
            Path(schema.config.OUTPUTDIR).resolve() / "terms/types/4/4DStatue.html",
        )


class TestBuildTermPages(unittest.TestCase):
    def setUp(self) -> None:
        self.renderer = buildtermpages.TermPageRenderer(
            stats_providers=[],
            build_opts=[],
            term_docs_dir="/docs",
        )

    def testTemplateRenderNoExample(self) -> None:
        term = TermView(
            SchemaType(
                uri=URIRef("http://example.com/whatchicallit"),
                label="whatchicallit",
            ),
            TermViewCatalog(),
        )
        output = self.renderer.termtemplateRender(term=term, examples=[], json="")
        self.assertIn("whatchicallit", output)
        self.assertIn("http://example.com/whatchicallit", output)
        self.assertNotIn('class="google-public-stats-badge-container"', output)

    def testTemplateRenderOneExample(self) -> None:
        examples = [
            schemaexamples.Example(
                terms=["Thingamabob"],
                original_html="Awesome & Thingamabob",
                microdata="",
                rdfa="",
                jsonld="",
                exmeta={"id": "eg-0042", "file": __file__, "filepos": 0},
            )
        ]
        term = TermView(
            SchemaType(
                uri=URIRef("http://example.com/thingamabob"),
                label="Thingamabob",
            ),
            TermViewCatalog(),
        )
        output = self.renderer.termtemplateRender(
            term=term, examples=examples, json="[42]"
        )
        self.assertIn("Thingamabob", output)
        self.assertIn("http://example.com/thingamabob", output)
        self.assertIn("Awesome &amp; Thingamabob", output)
        self.assertNotIn('class="google-public-stats-badge-container"', output)

    def testExplicitTemplateRendererOverridesGlobalVersionAndBuildOpts(
        self,
    ) -> None:
        custom_renderer = TemplateRenderer(
            InputLayout(constants.PROJECT_ROOT),
            VersionItem("99.0", "2099-12-31"),
            ("goto",),
        )
        page_renderer = buildtermpages.TermPageRenderer(
            stats_providers=[],
            term_docs_dir="/docs",
            template_renderer=custom_renderer,
        )
        term = TermView(
            SchemaType(
                uri=URIRef("http://example.com/FloatingType"),
                label="FloatingType",
            ),
            TermViewCatalog(),
        )
        output = page_renderer.termtemplateRender(term=term, examples=[], json="")
        self.assertIn("V99.0", output)
        self.assertIn("2099-12-31", output)
        self.assertIn("jumpmenu.js", output)

        with self.assertRaises(ValueError):
            buildtermpages.TermPageRenderer(
                stats_providers=[],
                term_docs_dir="/docs",
                build_opts=["goto"],
                template_renderer=custom_renderer,
            )

    def testBuildTermsHonorsExplicitTemplateRenderer(self) -> None:
        orig_output = schema.config.OUTPUTDIR
        orig_target = schema.config.TARGET_VERSION
        custom_renderer = TemplateRenderer(
            InputLayout(constants.PROJECT_ROOT),
            VersionItem("99.0", "2099-12-31"),
            ("goto",),
        )
        term = SchemaType(
            uri=URIRef("https://schema.org/FloatingType"),
            label="FloatingType",
        )
        catalog = TermViewCatalog(vocab=Vocabulary(types={term.uri: term}))
        jsonld_index = TermJsonLdIndex(context={}, nodes_by_id={})
        with tempfile.TemporaryDirectory() as tmp:
            out_dir = Path(tmp) / "site"
            buildtermpages.buildTerms(
                ["FloatingType"],
                config={
                    "stats_providers": [],
                    "term_docs_dir": "/docs",
                    "examples": schemaexamples.SchemaExamples.from_files([]),
                    "template_renderer": custom_renderer,
                    "output_dir": str(out_dir),
                },
                catalog=catalog,
                jsonld_index=jsonld_index,
            )
            html = (out_dir / "terms/types/F/FloatingType.html").read_text(
                encoding="utf-8"
            )
        self.assertIn("V99.0", html)
        self.assertIn("2099-12-31", html)
        self.assertIn("jumpmenu.js", html)
        self.assertEqual(schema.config.OUTPUTDIR, orig_output)
        self.assertEqual(schema.config.TARGET_VERSION, orig_target)

    def testBuildTermsAppliesTargetVersionOutputDirAndReleaseFile(
        self,
    ) -> None:
        orig_target = schema.config.TARGET_VERSION
        orig_output = schema.config.OUTPUTDIR
        self.addCleanup(setattr, schema.config, "TARGET_VERSION", orig_target)
        self.addCleanup(setattr, schema.config, "OUTPUTDIR", orig_output)

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            ttl_path = root / "release.ttl"
            ttl_path.write_text(
                "@prefix : <https://schema.org/> .\n"
                "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
                ':WorkerOnlyType a rdfs:Class ; rdfs:label "WorkerOnlyType" ; '
                'rdfs:comment "Loaded from release_file." .\n',
                encoding="utf-8",
            )
            out_dir = root / "custom_site"

            schema.config.TARGET_VERSION = "next"
            schema.config.OUTPUTDIR = "software/site"

            published = schema.VERSION.current()
            buildtermpages.buildTerms(
                ["WorkerOnlyType"],
                config={
                    "stats_providers": [],
                    "build_opts": [],
                    "term_docs_dir": "/docs",
                    "examples": schemaexamples.SchemaExamples.from_files([]),
                    "target_version": published.number(),
                    "output_dir": str(out_dir),
                    "release_file": str(ttl_path),
                },
            )

            rendered_file = out_dir / "terms/types/W/WorkerOnlyType.html"
            self.assertTrue(rendered_file.is_file())
            html = rendered_file.read_text(encoding="utf-8")
            self.assertIn("Loaded from release_file.", html)
            self.assertIn(f"V{published.number()}", html)
            self.assertIn(str(published.date()), html)
            self.assertNotIn("Vnext", html)
            self.assertEqual(schema.config.TARGET_VERSION, "next")
            self.assertEqual(schema.config.OUTPUTDIR, "software/site")


if __name__ == "__main__":
    unittest.main()
