from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from schemaorg.layout import InputLayout
from schemaorg.progress import NullProgressReporter
from schemaorg.tasks.compare_vocabulary import CompareVocabularyTask


class TestCompareVocabularyTask(unittest.TestCase):
    def setUp(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.root = Path(temp_dir.name)
        self.input_layout = InputLayout(self.root)

        (self.root / "versions.json").write_text(
            json.dumps(
                {"schemaversion": "2.0", "releaseLog": {"2.0": "2026-02-01", "1.0": "2026-01-01"}}
            ),
            encoding="utf-8",
        )
        rel_dir = self.root / "data" / "releases" / "1.0"
        rel_dir.mkdir(parents=True)
        (rel_dir / "schemaorg-all-https.ttl").write_text(
            "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
            "@prefix schema: <https://schema.org/> .\n"
            'schema:Thing a rdfs:Class ; rdfs:label "Thing" ; rdfs:comment "Old comment" .\n'
            'schema:OldType a rdfs:Class ; rdfs:label "OldType" .\n',
            encoding="utf-8",
        )

        src_dir = self.root / "data"
        (src_dir / "schema.ttl").write_text(
            "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
            "@prefix schema: <https://schema.org/> .\n"
            'schema:Thing a rdfs:Class ; rdfs:label "Thing" ; rdfs:comment "New comment" .\n'
            'schema:NewType a rdfs:Class ; rdfs:label "NewType" .\n'
            "schema:PendingType a rdfs:Class ;\n"
            '    rdfs:label "PendingType" ;\n'
            "    schema:isPartOf <https://pending.schema.org> .\n",
            encoding="utf-8",
        )

    def test_compares_default_source_against_previous_release(self) -> None:
        report = CompareVocabularyTask(
            input_layout=self.input_layout,
            previous_spec=None,
            current_spec=None,
            exclude_layers=[],
            include_layers=[],
            show_names=True,
            show_triples=True,
            progress=NullProgressReporter(),
        ).run()

        self.assertEqual(report.previous_count, 2)
        self.assertEqual(report.current_count, 3)
        self.assertEqual(
            report.added,
            (
                "https://schema.org/NewType",
                "https://schema.org/PendingType",
            ),
        )
        self.assertEqual(report.dropped, ("https://schema.org/OldType",))
        self.assertEqual(report.changed_count, 1)
        self.assertIn("Dropped term https://schema.org/OldType", report.formatted_report)
        self.assertIn("New term https://schema.org/NewType", report.formatted_report)
        self.assertIn("Changed term: https://schema.org/Thing", report.formatted_report)
        self.assertIn("New comment", report.formatted_report)

    def test_layer_filtering_excludes_and_reincludes_layers(self) -> None:
        excluded = CompareVocabularyTask(
            input_layout=self.input_layout,
            previous_spec=None,
            current_spec="source",
            exclude_layers=["pending"],
            include_layers=[],
            show_names=False,
            show_triples=False,
            progress=NullProgressReporter(),
        ).run()
        self.assertEqual(excluded.added, ("https://schema.org/NewType",))

        reincluded = CompareVocabularyTask(
            input_layout=self.input_layout,
            previous_spec=None,
            current_spec="source",
            exclude_layers=["pending"],
            include_layers=["pending"],
            show_names=False,
            show_triples=False,
            progress=NullProgressReporter(),
        ).run()
        self.assertEqual(
            reincluded.added,
            (
                "https://schema.org/NewType",
                "https://schema.org/PendingType",
            ),
        )


if __name__ == "__main__":
    unittest.main()
