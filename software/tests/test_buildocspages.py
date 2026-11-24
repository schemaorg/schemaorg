from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from rdflib import URIRef

from schemaorg.model import SchemaProperty, SchemaType, Vocabulary
from schemaorg.term_view import TermViewCatalog
import util.buildocspages as buildocspages
import util.schema as schema


class TestBuildDocs(unittest.TestCase):
    def testGenerateTerms(self) -> None:
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
        catalog = TermViewCatalog(vocab=vocab)

        self.assertEqual(
            list(buildocspages.generate_terms(tags=False, catalog=catalog)),
            ["Person\n", "name\n"],
        )
        self.assertEqual(
            list(buildocspages.generate_terms(tags=True, catalog=catalog)),
            ["Person t\n", "name p\n"],
        )

    def testBuildDocsResetsSharedRendererAfterRun(self) -> None:
        orig_output = schema.config.OUTPUTDIR
        self.addCleanup(setattr, schema.config, "OUTPUTDIR", orig_output)
        with tempfile.TemporaryDirectory() as tmp:
            schema.config.OUTPUTDIR = tmp
            buildocspages.buildDocs(["Home"], catalog=TermViewCatalog())
            self.assertTrue((Path(tmp) / "docs/home.html").is_file())
        self.assertIsNone(buildocspages._SHARED_DOCS_RENDERER)


if __name__ == "__main__":
    unittest.main()
