from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

import rdflib

from schemaorg.progress import NullProgressReporter
from schemaorg.sdo_uri import SDO, SdoUri
from schemaorg.tasks.turtle_tasks import (
    AnnotateTurtleTask,
    LintTurtleTask,
    MergeTurtleTask,
)


class TestTurtleTasks(unittest.TestCase):
    def setUp(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.root = Path(temp_dir.name)

    def test_lint_orders_classes_before_properties(self) -> None:
        src = self.root / "unordered.ttl"
        src.write_text(
            "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
            "@prefix schema: <https://schema.org/> .\n\n"
            "schema:zeta a rdf:Property ;\n"
            '    rdfs:label "zeta" .\n\n'
            "schema:Alpha a rdfs:Class ;\n"
            '    rdfs:label "Alpha" .\n',
            encoding="utf-8",
        )
        out = self.root / "linted.ttl"
        written = LintTurtleTask(
            files=[src],
            output=out,
            progress=NullProgressReporter(),
        ).run()

        self.assertEqual(written, [out])
        text = out.read_text(encoding="utf-8")
        self.assertLess(text.index("schema:Alpha"), text.index("schema:zeta"))

    def test_lint_rejects_output_with_multiple_files(self) -> None:
        a = self.root / "a.ttl"
        b = self.root / "b.ttl"
        a.write_text("", encoding="utf-8")
        b.write_text("", encoding="utf-8")
        with self.assertRaises(ValueError):
            LintTurtleTask(
                files=[a, b],
                output=self.root / "out.ttl",
                progress=NullProgressReporter(),
            )

    def test_merge_combines_multiple_files(self) -> None:
        first = self.root / "first.ttl"
        second = self.root / "second.ttl"
        first.write_text(
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
            "@prefix schema: <https://schema.org/> .\n"
            'schema:Person a rdfs:Class ; rdfs:label "Person" .\n',
            encoding="utf-8",
        )
        second.write_text(
            "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
            "@prefix schema: <https://schema.org/> .\n"
            'schema:name a rdf:Property ; rdfs:label "name" .\n',
            encoding="utf-8",
        )
        merged_path = self.root / "merged.ttl"
        result = MergeTurtleTask(
            files=[first, second],
            output=merged_path,
            progress=NullProgressReporter(),
        ).run()

        self.assertEqual(result, merged_path)
        parsed = rdflib.Graph().parse(merged_path, format="turtle")
        self.assertIn((SDO.Person, rdflib.RDF.type, rdflib.RDFS.Class), parsed)
        self.assertIn((SDO.name, rdflib.RDF.type, rdflib.RDF.Property), parsed)

    def test_annotate_sets_and_clears_is_part_of(self) -> None:
        src = self.root / "terms.ttl"
        src.write_text(
            "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
            "@prefix schema: <https://schema.org/> .\n"
            'schema:Widget a rdfs:Class ; rdfs:label "Widget" .\n'
            'schema:widgetCode a rdf:Property ; rdfs:label "widgetCode" .\n',
            encoding="utf-8",
        )

        AnnotateTurtleTask(
            files=[src],
            output=None,
            part_of="pending",
            progress=NullProgressReporter(),
        ).run()

        pending_uri = SdoUri.for_layer("pending").uri
        after_pending = rdflib.Graph().parse(src, format="turtle")
        self.assertIn((SDO.Widget, SDO.isPartOf, pending_uri), after_pending)
        self.assertIn(
            (SDO.widgetCode, SDO.isPartOf, pending_uri), after_pending
        )

        AnnotateTurtleTask(
            files=[src],
            output=None,
            part_of="GA",
            progress=NullProgressReporter(),
        ).run()

        after_ga = rdflib.Graph().parse(src, format="turtle")
        self.assertEqual(list(after_ga.triples((None, SDO.isPartOf, None))), [])

        with self.assertRaises(ValueError):
            AnnotateTurtleTask(
                files=[src],
                output=None,
                part_of="bogus",
                progress=NullProgressReporter(),
            )


if __name__ == "__main__":
    unittest.main()
