from __future__ import annotations

import json
import unittest
from unittest.mock import patch

import SchemaTerms.sdoterm as sdoterm
import SchemaTerms.sdotermsource as sdotermsource
import util.buildocspages as buildocspages


class TestBuildDocs(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        sdotermsource.SdoTermSource.sourceGraph()

    def testJsonldtree(self) -> None:
        raw = buildocspages.jsonldtree(page=None)
        tree = json.loads(raw)
        self.assertIn("@context", tree)
        self.assertEqual(tree["@id"], "schema:Thing")
        self.assertEqual(tree["@type"], "rdfs:Class")
        self.assertEqual(tree["name"], "Thing")
        children = tree.get("children", [])
        self.assertTrue(children)
        self.assertTrue(any(child["@id"] == "schema:Person" for child in children))

    @patch("SchemaTerms.sdotermsource.SdoTermSource.getAllTerms")
    def testGenerateTerms(self, mock_get_all_terms) -> None:
        mock_get_all_terms.return_value = [
            sdoterm.SdoType(
                term_id="Person", uri="https://schema.org/Person", label="Person"
            ),
            sdoterm.SdoProperty(
                term_id="name", uri="https://schema.org/name", label="name"
            ),
            "ignored-raw-id",
        ]
        self.assertEqual(
            list(buildocspages.generate_terms(tags=False)),
            ["Person\n", "name\n"],
        )
        self.assertEqual(
            list(buildocspages.generate_terms(tags=True)),
            ["Person t\n", "name p\n"],
        )


if __name__ == "__main__":
    unittest.main()
