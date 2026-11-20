from __future__ import annotations

import unittest
from unittest.mock import patch

import SchemaTerms.sdoterm as sdoterm
import util.buildocspages as buildocspages


class TestBuildDocs(unittest.TestCase):
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
