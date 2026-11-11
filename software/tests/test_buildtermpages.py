from __future__ import annotations

from pathlib import Path
import unittest

import SchemaExamples.schemaexamples as schemaexamples
import SchemaTerms.sdoterm as sdoterm
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
        term = sdoterm.SdoType(
            term_id="42",
            uri="http://example.com/whatchicallit",
            label="whatchicallit",
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
        term = sdoterm.SdoType(
            term_id="42",
            uri="http://example.com/thingamabob",
            label="Thingamabob",
        )
        output = self.renderer.termtemplateRender(
            term=term, examples=examples, json="[42]"
        )
        self.assertIn("Thingamabob", output)
        self.assertIn("http://example.com/thingamabob", output)
        self.assertIn("Awesome &amp; Thingamabob", output)
        self.assertNotIn('class="google-public-stats-badge-container"', output)


if __name__ == "__main__":
    unittest.main()
