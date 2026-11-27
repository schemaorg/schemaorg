"""Tests for example validation: the validator, and the shapes it runs on.

ValidateExampleTests drives ExampleValidator on a toy shapes graph, so it
needs no build. Payloads cover the four outcomes: valid, invalid,
untargeted, and unparseable.

ShaclGateLivenessTests feeds the committed data/releases/<version>/ shapes
a payload they are required to reject. Without it, shapes carrying no
constraints or targeting the wrong namespace still exit 0. Both have
happened here.
"""

from __future__ import annotations

from functools import partial
import json
import logging
import os
from pathlib import Path
import subprocess
import tempfile
import textwrap
import unittest
from unittest.mock import patch

import rdflib
from rdflib.namespace import SH

from schemaorg import constants
from schemaorg.layout import Domain, InputLayout, OutputLayout, Releases
from schemaorg.progress import LogProgressReporter, NullProgressReporter
from schemaorg.tasks.validate_examples import (
    ExampleResult,
    ExampleValidator,
    ShaclConfigError,
    ValidateExamplesTask,
)
from schemaorg.version import Version
import scripts.buildsite as buildsite
import scripts.validate_examples_shacl as validator


class FakeExample:
    """Stand-in for a SchemaExamples example. validate() needs these two."""

    def __init__(self, key: str, jsonld: str):
        self._key = key
        self._jsonld = jsonld

    def getKey(self) -> str:
        return self._key

    def getJsonldRaw(self) -> str:
        return self._jsonld


class ValidateExampleTests(unittest.TestCase):
    shapes: rdflib.Graph
    ontology: rdflib.Graph
    engine: ExampleValidator
    GOOD = '{"@context":"http://schema.org/","@type":"Person","name":"Jane"}'
    BAD = (
        '{"@context":"http://schema.org/","@type":"Person",'
        '"name":{"@type":"Person","name":"not a string"}}'
    )

    @classmethod
    def setUpClass(cls) -> None:
        shapes_turtle = textwrap.dedent("""\
            @prefix sh:     <http://www.w3.org/ns/shacl#> .
            @prefix schema: <http://schema.org/> .
            @prefix xsd:    <http://www.w3.org/2001/XMLSchema#> .
            @prefix ex:     <http://example.org/> .

            ex:PersonShape a sh:NodeShape ;
                sh:targetClass schema:Person ;
                sh:property [ sh:path schema:name ; sh:datatype xsd:string ] .
            """)
        cls.shapes = rdflib.Graph()
        cls.shapes.parse(data=shapes_turtle, format="turtle")
        cls.ontology = rdflib.Graph()
        cls.engine = ExampleValidator(
            shacl_graph=cls.shapes, ont_graph=cls.ontology
        )

    def validate(self, name: str, jsonld: str) -> ExampleResult:
        return self.engine.validate(FakeExample(name, jsonld))

    def testResultCarriesItsExample(self) -> None:
        example = FakeExample("some-key", self.GOOD)

        result = self.engine.validate(example)
        self.assertIs(result.example, example)
        self.assertEqual(result.name, "some-key")

    def testTargetClassesAreIndexed(self) -> None:
        self.assertEqual(
            self.engine.target_classes, frozenset({"http://schema.org/Person"})
        )

    def testShapesWithoutTargetsCannotBuildAValidator(self) -> None:
        with self.assertRaises(ValueError):
            ExampleValidator(
                shacl_graph=rdflib.Graph(), ont_graph=rdflib.Graph()
            )

    def testValidExampleConforms(self) -> None:
        result = self.validate("good", self.GOOD)
        self.assertTrue(result.targeted)
        self.assertTrue(result.conforms)
        self.assertIsNone(result.error)
        self.assertIsNone(result.report, "clean examples carry no report")

    def testInvalidExampleIsRejectedWithAReport(self) -> None:
        result = self.validate("bad", self.BAD)
        self.assertTrue(result.targeted)
        self.assertFalse(result.conforms)
        self.assertIsNone(result.error, "a violation is not an error")
        self.assertTrue(result.report, "a failure must explain itself")

    def testUntargetedExampleConformsButIsNotTargeted(self) -> None:
        recipe = '{"@context":"http://schema.org/","@type":"Recipe","name":"Soup"}'

        result = self.validate("untargeted", recipe)
        self.assertFalse(result.targeted, "no shape targets Recipe")
        self.assertTrue(result.conforms, "vacuously true, not inspected")

    def testMalformedInputIsReportedNotRaised(self) -> None:
        result = self.validate("malformed", "{ this is not json")
        self.assertIsNotNone(result.error)
        self.assertFalse(result.conforms)

    def testNameIsCarriedThrough(self) -> None:
        self.assertEqual(self.validate("some-key", self.GOOD).name, "some-key")

    def testRepeatedValidationDoesNotGrowTheGraphs(self) -> None:
        """Shared graphs must converge, not accumulate.

        pyshacl injects two RDFS axioms into the shapes graph on first use.
        Idempotent, so reuse is safe, but it is a real write.
        """
        self.validate("warmup", self.GOOD)
        shapes_before = len(self.shapes)
        ontology_before = len(self.ontology)

        for name, payload in (
            ("good", self.GOOD),
            ("bad", self.BAD),
            ("good2", self.GOOD),
        ):
            self.validate(name, payload)

        self.assertEqual(len(self.shapes), shapes_before)
        self.assertEqual(len(self.ontology), ontology_before)

    def _write_temp_releases(self, root: Path) -> tuple[Releases, Version]:
        versions_path = root / "versions.json"
        versions_path.write_text(
            json.dumps({
                "schemaversion": "30.1",
                "releaseLog": {"30.1": "2026-09-16"},
            }),
            encoding="utf-8",
        )
        version = Version(versions_path)
        releases = Releases(OutputLayout(root / "out"), version)
        shapes = releases.file(
            version.next(), protocol="", scope="shapes", extension=".shacl"
        )
        shapes.write_text(self.shapes.serialize(format="turtle"), encoding="utf-8")
        releases.file(
            version.next(), protocol="", scope="subclasses", extension=".shacl"
        ).write_text("", encoding="utf-8")
        return releases, version

    def testTaskValidatesExamplesAndSourceOutputOnlyLogsFailures(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            releases, version = self._write_temp_releases(Path(tmp))
            logger = logging.getLogger("test.validate_task")
            reporter = LogProgressReporter(logger=logger, log_steps=True)
            with self.assertLogs(logger, level=logging.INFO) as captured:
                summary = ValidateExamplesTask(
                    releases=releases,
                    version=version.next(),
                    examples=(
                        FakeExample("eg-good", self.GOOD),
                        FakeExample("eg-bad", self.BAD),
                    ),
                    invalid_only=False,
                    source_output=True,
                    progress=reporter,
                ).run()

        joined = "\n".join(captured.output)
        self.assertEqual(summary.total_count, 2)
        self.assertEqual(summary.targeted_count, 2)
        self.assertEqual(summary.error_count, 1)
        self.assertEqual(summary.failures[0].name, "eg-bad")
        self.assertIn("(2/2 examples)", joined)
        self.assertNotIn("Jane", joined)
        self.assertIn("not a string", joined)

    def testTaskReportsMalformedJsonAsFailureNotConfigError(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            releases, version = self._write_temp_releases(Path(tmp))
            summary = ValidateExamplesTask(
                releases=releases,
                version=version.next(),
                examples=(FakeExample("eg-broken", "{ not json"),),
                invalid_only=True,
                source_output=False,
                progress=NullProgressReporter(),
            ).run()
        self.assertEqual(summary.error_count, 1)
        self.assertEqual(summary.targeted_count, 0)
        self.assertIsNotNone(summary.failures[0].error)

        with tempfile.TemporaryDirectory() as tmp:
            releases, version = self._write_temp_releases(Path(tmp))
            with self.assertRaises(ShaclConfigError):
                ValidateExamplesTask(
                    releases=releases,
                    version=version.next(),
                    examples=(),
                    invalid_only=True,
                    source_output=False,
                    progress=NullProgressReporter(),
                ).run()

    def testEmptyExamplesExitsConfigError(self) -> None:
        with (
            self.assertLogs(validator.log, level="ERROR") as logs,
            self.assertRaises(SystemExit) as cm,
        ):
            validator.validate_examples([], invalid_only=True, source_output=False)
        self.assertEqual(cm.exception.code, os.EX_CONFIG)
        self.assertIn("No JSON-LD examples found", "\n".join(logs.output))

    def testMissingShaclFilesExitsConfigErrorWithoutMkdir(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            input_layout = InputLayout(constants.PROJECT_ROOT)
            version_registry = Version(
                input_layout.file(Domain.ROOT, constants.VERSIONS_FILE)
            )
            fresh_out = Path(tmp) / "fresh"
            empty_releases = Releases(OutputLayout(fresh_out), version_registry)
            with (
                self.assertLogs(validator.log, level="ERROR") as logs,
                self.assertRaises(SystemExit) as cm,
            ):
                validator.validate_examples(
                    [FakeExample("k", self.GOOD)],
                    invalid_only=True,
                    source_output=False,
                    releases=empty_releases,
                )
            self.assertEqual(cm.exception.code, os.EX_CONFIG)
            self.assertIn("SHACL files not found", "\n".join(logs.output))
            self.assertFalse(fresh_out.exists())

    def testRunShaclTestsFailsWhenShaclMissing(self) -> None:
        quiet_run = partial(subprocess.run, capture_output=True)
        with (
            tempfile.TemporaryDirectory() as tmp,
            patch.object(buildsite.subprocess, "run", side_effect=quiet_run),
            self.assertLogs(buildsite.log, level="INFO") as logs,
            self.assertRaises(SystemExit) as cm,
        ):
            buildsite.runShaclTests(releases_output_dir=tmp)
        self.assertEqual(cm.exception.code, os.EX_CONFIG)
        self.assertIn("SHACL validation reported errors", "\n".join(logs.output))


class ShaclGateLivenessTests(unittest.TestCase):
    """The shipped shapes must be able to reject something.

    Drives the real ExampleValidator: a canary validated under different
    settings than production proves nothing about production.
    """

    SHAPES_FILENAME = "schemaorg-shapes.shacl"
    SUBCLASSES_FILENAME = "schemaorg-subclasses.shacl"
    result: ExampleResult | None
    shapes: rdflib.Graph

    @classmethod
    def setUpClass(cls) -> None:
        shapes = cls._load(cls.SHAPES_FILENAME)
        ontology = cls._load(cls.SUBCLASSES_FILENAME)

        cls.result = None
        if shapes is None or ontology is None:
            return

        cls.shapes = shapes
        engine = ExampleValidator(shacl_graph=shapes, ont_graph=ontology)
        cls.result = engine.validate(FakeExample("canary", cls.canary_payload()))

    @classmethod
    def _load(cls, filename: str) -> rdflib.Graph | None:
        input_layout = InputLayout(constants.PROJECT_ROOT)
        version_registry = Version(
            input_layout.file(Domain.ROOT, constants.VERSIONS_FILE)
        )
        path = Releases(input_layout, version_registry).file(filename=filename)
        if not path.is_file():
            return None
        graph = rdflib.Graph()
        graph.parse(source=path, format="turtle")
        return graph

    @staticmethod
    def canary_payload() -> str:
        """A payload the shapes are required to reject.

        schema:name ranges over Text, so a nested Person is a type error.
        https context, as the real examples write it: namespace drift shows
        up here as "the canary conformed".
        """
        return textwrap.dedent("""\
            {
              "@context": "https://schema.org",
              "@type": "Person",
              "name": { "@type": "Person", "name": "a Person is not a name" }
            }
            """)

    def setUp(self) -> None:
        if self.result is None:
            self.skipTest("release shapes not built")

    def testCanaryParses(self) -> None:
        """Usually fails when the schema.org context cannot be fetched."""
        assert self.result is not None
        self.assertIsNone(self.result.error)

    def testCanaryIsTargetedByTheShapes(self) -> None:
        assert self.result is not None
        targets = {str(t) for t in self.shapes.objects(None, SH.targetClass)}

        self.assertTrue(
            self.result.targeted,
            "no canary type matches any sh:targetClass, so nothing would be "
            "inspected. Signature of a namespace mismatch.\n"
            f"  sample targets: {sorted(targets)[:3]}",
        )

    def testCanaryIsRejected(self) -> None:
        assert self.result is not None
        self.assertFalse(
            self.result.conforms,
            "the canary is deliberately invalid (a Person used as a "
            "schema:name) yet it conformed. The shapes constrain nothing.",
        )


if __name__ == "__main__":
    unittest.main()
