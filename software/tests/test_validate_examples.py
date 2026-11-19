from __future__ import annotations

import json
import logging
from pathlib import Path
import tempfile
import textwrap
import unittest

from schemaorg.layout import OutputLayout, Releases
from schemaorg.progress import LogProgressReporter, NullProgressReporter
from schemaorg.tasks.validate_examples import (
    ShaclConfigError,
    ValidateExamplesTask,
)
from schemaorg.version import Version
import SchemaExamples.schemaexamples as schemaexamples


def _make_example(key: str, jsonld: str) -> schemaexamples.Example:
    return schemaexamples.Example(
        terms=["Person"],
        original_html="",
        microdata="",
        rdfa="",
        jsonld=jsonld,
        exmeta={"id": key, "file": "examples.txt", "filepos": 1},
    )


class TestValidateExamplesTask(unittest.TestCase):
    def setUp(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.root = Path(temp_dir.name)

        versions_path = self.root / "versions.json"
        versions_path.write_text(
            json.dumps({
                "schemaversion": "30.1",
                "releaseLog": {"30.1": "2026-09-16"},
            }),
            encoding="utf-8",
        )
        self.version = Version(versions_path)
        self.releases = Releases(OutputLayout(self.root / "out"), self.version)

        shapes = self.releases.file(
            self.version.next(), protocol="", scope="shapes", extension=".shacl"
        )
        shapes.parent.mkdir(parents=True, exist_ok=True)
        shapes.write_text(
            textwrap.dedent("""\
                @prefix sh: <http://www.w3.org/ns/shacl#> .
                @prefix schema: <http://schema.org/> .
                @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .
                @prefix ex: <http://example.org/> .
                ex:PersonShape a sh:NodeShape ;
                    sh:targetClass schema:Person ;
                    sh:property [ sh:path schema:name ; sh:datatype xsd:string ] .
            """),
            encoding="utf-8",
        )
        subclasses = self.releases.file(
            self.version.next(),
            protocol="",
            scope="subclasses",
            extension=".shacl",
        )
        subclasses.write_text("", encoding="utf-8")

    def test_validates_examples_and_returns_structured_summary(self) -> None:
        good = _make_example(
            "eg-0001",
            '{"@context": "http://schema.org/", "@type": "Person", "name": "Ada"}',
        )
        bad = _make_example(
            "eg-0002",
            '{"@context": "http://schema.org/", "@type": "Person", '
            '"name": {"@type": "Person", "name": "bad"}}',
        )
        logger = logging.getLogger("test.validate_task")
        reporter = LogProgressReporter(logger=logger, log_steps=True)
        with self.assertLogs(logger, level=logging.INFO) as captured:
            summary = ValidateExamplesTask(
                releases=self.releases,
                version=self.version.next(),
                examples=(good, bad),
                invalid_only=False,
                source_output=True,
                progress=reporter,
            ).run()

        self.assertEqual(summary.total_count, 2)
        self.assertEqual(summary.targeted_count, 2)
        self.assertEqual(summary.error_count, 1)
        self.assertEqual(summary.failures[0].name, "eg-0002")
        self.assertIn("(2/2 examples)", "\n".join(captured.output))

    def test_raises_shacl_config_error_when_examples_empty(self) -> None:
        with self.assertRaises(ShaclConfigError):
            ValidateExamplesTask(
                releases=self.releases,
                version=self.version.next(),
                examples=(),
                invalid_only=True,
                source_output=False,
                progress=NullProgressReporter(),
            ).run()


if __name__ == "__main__":
    unittest.main()
