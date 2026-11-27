from __future__ import annotations

import logging
from pathlib import Path
import tempfile
import unittest

import rdflib

from schemaorg.model import VocabularyLoader
from schemaorg.progress import LogProgressReporter, NullProgressReporter
from schemaorg.tasks.export_term_list import (
    ExportTermListTask,
    format_term_lines,
)
from schemaorg.term_view import TermViewCatalog


class TestExportTermListTask(unittest.TestCase):
    def setUp(self) -> None:
        graph = rdflib.Graph()
        graph.parse(
            data=(
                "@prefix : <https://schema.org/> .\n"
                "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .\n"
                "@prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .\n"
                ':DataType a rdfs:Class ; rdfs:label "DataType" ; rdfs:subClassOf rdfs:Class .\n'
                ':Text a :DataType, rdfs:Class ; rdfs:label "Text" .\n'
                ':Enumeration a rdfs:Class ; rdfs:label "Enumeration" .\n'
                ':Status a rdfs:Class ; rdfs:label "Status" ; rdfs:subClassOf :Enumeration .\n'
                ':Active a :Status ; rdfs:label "Active" .\n'
                ':Person a rdfs:Class ; rdfs:label "Person" .\n'
                ':name a rdf:Property ; rdfs:label "name" .\n'
            ),
            format="turtle",
        )
        vocab = VocabularyLoader(graph).load()
        self.catalog = TermViewCatalog.from_graph(graph, vocab)

        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.root = Path(temp_dir.name)

    def test_writes_untagged_and_all_tagged_term_kinds(self) -> None:
        plain_out = self.root / "plain.txt"
        ExportTermListTask(
            catalog=self.catalog,
            include_tags=False,
            output_path=plain_out,
            progress=NullProgressReporter(),
        ).run()
        self.assertEqual(
            plain_out.read_text(encoding="utf-8"),
            "Active\nDataType\nEnumeration\nPerson\nStatus\nText\nname\n",
        )

        tagged_out = self.root / "tagged.txt"
        logger = logging.getLogger("test.term_list")
        with self.assertLogs(logger, level=logging.INFO) as captured:
            ExportTermListTask(
                catalog=self.catalog,
                include_tags=True,
                output_path=tagged_out,
                progress=LogProgressReporter(logger=logger, log_steps=False),
            ).run()
        expected = (
            "Active v\nDataType d\nEnumeration e\nPerson t\n"
            "Status e\nText d\nname p\n"
        )
        self.assertEqual(tagged_out.read_text(encoding="utf-8"), expected)
        self.assertEqual(
            "".join(format_term_lines(self.catalog, include_tags=True)),
            expected,
        )
        self.assertIn("(7/7 terms)", "\n".join(captured.output))


if __name__ == "__main__":
    unittest.main()
