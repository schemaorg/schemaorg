from __future__ import annotations

import logging
from pathlib import Path
import tempfile
import unittest

from rdflib import URIRef

from schemaorg.model import SchemaProperty, SchemaType, Vocabulary
from schemaorg.progress import LogProgressReporter, NullProgressReporter
from schemaorg.tasks.export_term_list import ExportTermListTask
from schemaorg.term_view import TermViewCatalog


class TestExportTermListTask(unittest.TestCase):
    def setUp(self) -> None:
        person = SchemaType(
            uri=URIRef("https://schema.org/Person"), label="Person"
        )
        name = SchemaProperty(
            uri=URIRef("https://schema.org/name"), label="name"
        )
        vocab = Vocabulary(
            types={person.uri: person},
            properties={name.uri: name},
        )
        self.catalog = TermViewCatalog(vocab=vocab)

        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.root = Path(temp_dir.name)

    def test_writes_untagged_and_tagged_term_lists(self) -> None:
        plain_out = self.root / "plain.txt"
        ExportTermListTask(
            catalog=self.catalog,
            include_tags=False,
            output_path=plain_out,
            progress=NullProgressReporter(),
        ).run()
        self.assertEqual(plain_out.read_text(encoding="utf-8"), "Person\nname\n")

        tagged_out = self.root / "tagged.txt"
        logger = logging.getLogger("test.term_list")
        with self.assertLogs(logger, level=logging.INFO) as captured:
            ExportTermListTask(
                catalog=self.catalog,
                include_tags=True,
                output_path=tagged_out,
                progress=LogProgressReporter(logger=logger, log_steps=False),
            ).run()
        self.assertEqual(
            tagged_out.read_text(encoding="utf-8"), "Person t\nname p\n"
        )
        self.assertIn("(2/2 terms)", "\n".join(captured.output))


if __name__ == "__main__":
    unittest.main()
