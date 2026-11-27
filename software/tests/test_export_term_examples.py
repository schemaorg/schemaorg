from __future__ import annotations

import csv
import logging
from pathlib import Path
import tempfile
import unittest

from schemaorg.graph_loader import GraphLoader
from schemaorg.layout import InputLayout, Issues
from schemaorg.model import VocabularyLoader
from schemaorg.progress import LogProgressReporter, NullProgressReporter
from schemaorg.tasks.export_term_examples import ExportTermExamplesTask
from SchemaExamples.schemaexamples import SchemaExamples


class TestExportTermExamplesTask(unittest.TestCase):
    def setUp(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.root = Path(temp_dir.name)
        data_dir = self.root / "data"
        data_dir.mkdir(parents=True)

        (data_dir / "schema.ttl").write_text(
            "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
            "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
            "@prefix schema: <https://schema.org/> .\n"
            'schema:CreativeWork a rdfs:Class ; rdfs:label "CreativeWork" .\n'
            'schema:Book a rdfs:Class ; rdfs:label "Book" ; rdfs:subClassOf schema:CreativeWork .\n'
            'schema:Media a rdfs:Class ; rdfs:label "Media" ; rdfs:subClassOf schema:CreativeWork .\n'
            'schema:AudioBook a rdfs:Class ; rdfs:label "AudioBook" ; rdfs:subClassOf schema:Book, schema:Media .\n',
            encoding="utf-8",
        )
        (data_dir / "examples.txt").write_text(
            "TYPES: #eg-0001 CreativeWork, Book\n"
            "PRE-MARKUP:\nA work.\n"
            'JSON:\n{"@context": "https://schema.org", "@type": "CreativeWork"}\n\n'
            "TYPES: #eg-0002 AudioBook\n"
            "PRE-MARKUP:\nAn audiobook.\n"
            'JSON:\n{"@context": "https://schema.org", "@type": "AudioBook"}\n',
            encoding="utf-8",
        )

        input_layout = InputLayout(self.root)
        graph = GraphLoader.load(Issues(input_layout).get_ttl_files())
        self.vocab = VocabularyLoader(graph).load()
        self.examples = SchemaExamples.from_layout(input_layout)

    def test_exports_direct_and_recursive_deduped_csv_columns(self) -> None:
        direct_out = self.root / "direct"
        written_direct = ExportTermExamplesTask(
            vocab=self.vocab,
            examples=self.examples,
            term_names=["CreativeWork"],
            recursive=False,
            output_path=direct_out,
            progress=NullProgressReporter(),
        ).run()

        self.assertEqual(written_direct, self.root / "direct.csv")
        with written_direct.open(encoding="utf-8", newline="") as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["Example Id"], "eg-0001")
        self.assertTrue(rows[0]["Source File"].endswith("examples.txt"))
        self.assertEqual(rows[0]["Linked to Terms"], "CreativeWork, Book")

        recursive_out = self.root / "recursive.csv"
        logger = logging.getLogger("test.term_examples")
        with self.assertLogs(logger, level=logging.WARNING) as captured:
            ExportTermExamplesTask(
                vocab=self.vocab,
                examples=self.examples,
                term_names=["CreativeWork", "Book", "MissingTerm"],
                recursive=True,
                output_path=recursive_out,
                progress=LogProgressReporter(logger=logger, log_steps=False),
            ).run()

        self.assertIn("No such term: MissingTerm", "\n".join(captured.output))
        with recursive_out.open(encoding="utf-8", newline="") as f:
            rec_rows = list(csv.DictReader(f))
        self.assertEqual(
            [r["Example Id"] for r in rec_rows], ["eg-0001", "eg-0002"]
        )


if __name__ == "__main__":
    unittest.main()
