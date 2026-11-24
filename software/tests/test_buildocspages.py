from __future__ import annotations

import unittest

from rdflib import URIRef

from schemaorg.model import SchemaProperty, SchemaType, Vocabulary
from schemaorg.term_view import TermViewCatalog
import util.buildocspages as buildocspages


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


if __name__ == "__main__":
    unittest.main()
