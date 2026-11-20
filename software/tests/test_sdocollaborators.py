from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from rdflib import URIRef

from schemaorg.collaborators import Collaborator, CollaboratorRegistry
from schemaorg.layout import InputLayout
from schemaorg.model import SchemaType, Vocabulary

TEST_DESCRIPTION = """---
img: http://example.com/logo.png
title: Test Foundation
url: http://example.com
--- DescriptionText.md
This is a _test_ description.
--- AcknowledgementText.md
This is a `test` acknowledgement.
"""


class SdoCollaboratorTest(unittest.TestCase):
    def test_collaborator(self) -> None:
        collab = Collaborator(ref="/tmp/test", desc=TEST_DESCRIPTION)
        self.assertEqual(collab.uri, "https://schema.org/tmp/test")
        self.assertEqual(collab.title, "Test Foundation")
        self.assertEqual(collab.img, "http://example.com/logo.png")
        self.assertEqual(collab.description, "This is a <em>test</em> description.")
        self.assertEqual(
            collab.acknowledgement, "This is a <code>test</code> acknowledgement."
        )

    def test_registry_marks_contributors_and_indexes_terms(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            collab_dir = root / "data" / "collab"
            collab_dir.mkdir(parents=True)
            (collab_dir / "TestOrg.md").write_text(
                TEST_DESCRIPTION, encoding="utf-8"
            )
            term = SchemaType(
                uri=URIRef("https://schema.org/Widget"),
                label="Widget",
                contributor=[URIRef("https://schema.org/docs/collab/TestOrg")],
            )
            vocab = Vocabulary(types={term.uri: term})
            registry = CollaboratorRegistry.from_layout(InputLayout(root), vocab)

            coll = registry.get("TestOrg")
            self.assertIsNotNone(coll)
            assert coll is not None
            self.assertEqual(coll.code, "TestOrg")
            self.assertEqual(coll.urirel, "/docs/collab/TestOrg")
            self.assertEqual(coll.docurl, "/docs/collab/TestOrg")
            self.assertEqual(coll.uri, "https://schema.org/docs/collab/TestOrg")
            self.assertTrue(coll.contributor)
            self.assertEqual(registry.term_uris("TestOrg"), (term.uri,))
            self.assertEqual(registry.for_term(term), (coll,))


if __name__ == "__main__":
    unittest.main()
