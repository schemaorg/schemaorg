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
            json.dumps({
                "schemaversion": "2.0",
                "releaseLog": {"2.0": "2026-02-01", "1.0": "2026-01-01"},
            }),
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
            "    schema:isPartOf <https://pending.schema.org> .\n"
            "schema:AtticType a rdfs:Class ;\n"
            '    rdfs:label "AtticType" ;\n'
            "    schema:isPartOf <https://attic.schema.org> .\n",
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
        self.assertEqual(report.current_count, 4)
        self.assertEqual(
            report.added,
            (
                "https://schema.org/AtticType",
                "https://schema.org/NewType",
                "https://schema.org/PendingType",
            ),
        )
        self.assertEqual(report.dropped, ("https://schema.org/OldType",))
        self.assertEqual(report.changed_count, 1)
        self.assertIn(
            "Dropped term https://schema.org/OldType", report.formatted_report
        )
        self.assertIn(
            "New term https://schema.org/NewType", report.formatted_report
        )
        self.assertIn(
            "Changed term: https://schema.org/Thing", report.formatted_report
        )
        self.assertIn("New comment", report.formatted_report)

    def test_layer_filtering_supports_extensions_with_include_override_and_core(
        self,
    ) -> None:
        # -e extensions -i pending keeps core + pending and drops attic.
        ext_with_pending = CompareVocabularyTask(
            input_layout=self.input_layout,
            previous_spec=None,
            current_spec="source",
            exclude_layers=["extensions"],
            include_layers=["pending"],
            show_names=False,
            show_triples=False,
            progress=NullProgressReporter(),
        ).run()
        self.assertEqual(
            ext_with_pending.added,
            (
                "https://schema.org/NewType",
                "https://schema.org/PendingType",
            ),
        )

        # -e core keeps only extensions.
        only_extensions = CompareVocabularyTask(
            input_layout=self.input_layout,
            previous_spec=None,
            current_spec="source",
            exclude_layers=["core"],
            include_layers=[],
            show_names=False,
            show_triples=False,
            progress=NullProgressReporter(),
        ).run()
        self.assertEqual(only_extensions.previous_count, 0)
        self.assertEqual(
            only_extensions.added,
            (
                "https://schema.org/AtticType",
                "https://schema.org/PendingType",
            ),
        )

    def test_loads_nquads_http_ttl_and_rejects_empty_dir(self) -> None:
        nq_path = self.root / "hist.nq"
        nq_path.write_text(
            "<http://schema.org/Thing> <http://www.w3.org/1999/02/22-rdf-syntax-ns#type> "
            "<http://www.w3.org/2000/01/rdf-schema#Class> <http://schema.org/3.9> .\n",
            encoding="utf-8",
        )
        http_ttl = self.root / "http.ttl"
        http_ttl.write_text(
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
            "@prefix schema: <http://schema.org/> .\n"
            "schema:Thing a rdfs:Class .\n",
            encoding="utf-8",
        )
        report = CompareVocabularyTask(
            input_layout=self.input_layout,
            previous_spec=str(nq_path),
            current_spec=str(http_ttl),
            exclude_layers=[],
            include_layers=[],
            show_names=False,
            show_triples=False,
            progress=NullProgressReporter(),
        ).run()
        self.assertEqual(report.previous_count, 1)
        self.assertEqual(report.current_count, 1)
        self.assertEqual(report.added, ())
        self.assertEqual(report.dropped, ())
        self.assertEqual(report.changed_count, 0)

        empty_dir = self.root / "empty"
        empty_dir.mkdir()
        with self.assertRaises(FileNotFoundError):
            CompareVocabularyTask(
                input_layout=self.input_layout,
                previous_spec=str(empty_dir),
                current_spec=str(http_ttl),
                exclude_layers=[],
                include_layers=[],
                show_names=False,
                show_triples=False,
                progress=NullProgressReporter(),
            ).run()


if __name__ == "__main__":
    unittest.main()
