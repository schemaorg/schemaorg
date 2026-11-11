from __future__ import annotations

import json
from typing import Any
import unittest
from unittest.mock import patch

import SchemaTerms.sdoterm as sdoterm
import util.sdojsonldcontext as sdojsonldcontext


class SdoJsonLdContextTest(unittest.TestCase):
    maxDiff = None

    def _create_and_check_base_context(self) -> dict[str, Any]:
        parsed = json.loads(sdojsonldcontext.createcontext())
        self.assertIn("@context", parsed)
        context = parsed["@context"]
        self.assertIn("type", context)
        self.assertIn("id", context)
        self.assertIn("@vocab", context)
        return context

    @patch("SchemaTerms.sdotermsource.SdoTermSource.getAllTerms")
    def test_createcontextEmpty(self, mock_get_all_terms) -> None:
        mock_get_all_terms.return_value = []
        self._create_and_check_base_context()

    @patch("SchemaTerms.sdotermsource.SdoTermSource.getAllTerms")
    def test_createcontextOneProperty(self, mock_get_all_terms) -> None:
        mock_id = "1234"
        mock_property = sdoterm.SdoProperty(
            term_id=mock_id, uri="http://schema.org/thang", label="thang"
        )
        mock_property.domainIncludes.setIds(["Thing"])
        mock_property.rangeIncludes.setIds(["Date", "Thing"])
        mock_get_all_terms.return_value = [mock_property]
        context = self._create_and_check_base_context()

        # Historically, @type=Date (or @type=id) was included for non-Text-related
        # properties. Since we support multiple datatypes/things for properties,
        # this led to inaccurate datatype results and inconsistent usage of
        # datatypes/IRIs for property values (post-JSON-LD processing).
        self.assertEqual(context[mock_id], {"@id": "http://schema.org/thang"})

    @patch("SchemaTerms.sdotermsource.SdoTermSource.getAllTerms")
    def test_createcontextOneDataType(self, mock_get_all_terms) -> None:
        mock_id = "1234"
        mock_type = sdoterm.SdoDataType(
            term_id=mock_id, uri="http://schema.org/Fnubl", label="fnubl"
        )
        mock_type.properties.setIds(["thang"])
        mock_type.expectedTypeFor.setIds(["Thing"])
        mock_get_all_terms.return_value = [mock_type]
        context = self._create_and_check_base_context()
        self.assertEqual(context[mock_id], {"@id": "http://schema.org/Fnubl"})

    @patch("SchemaTerms.sdotermsource.SdoTermSource.getAllTerms")
    def test_createcontextOneEnumeration(self, mock_get_all_terms) -> None:
        mock_id = "1234"
        mock_enumeration = sdoterm.SdoEnumeration(
            term_id=mock_id, uri="http://schema.org/Grabl", label="grabl"
        )
        mock_enumeration.expectedTypeFor.setIds(["Thing"])
        mock_get_all_terms.return_value = [mock_enumeration]
        context = self._create_and_check_base_context()
        self.assertEqual(context[mock_id], {"@id": "http://schema.org/Grabl"})

    @patch("SchemaTerms.sdotermsource.SdoTermSource.getAllTerms")
    def test_createcontextOneEnumerationValue(self, mock_get_all_terms) -> None:
        mock_id = "1234"
        mock_enumeration = sdoterm.SdoEnumerationvalue(
            term_id=mock_id, uri="http://schema.org/Bobl", label="bobl"
        )
        mock_get_all_terms.return_value = [mock_enumeration]
        context = self._create_and_check_base_context()
        self.assertEqual(context[mock_id], {"@id": "http://schema.org/Bobl"})

    @patch("SchemaTerms.sdotermsource.SdoTermSource.getAllTerms")
    def test_createcontextOneReference(self, mock_get_all_terms) -> None:
        mock_id = "1234"
        mock_reference = sdoterm.SdoReference(
            term_id=mock_id, uri="http://schema.org/Bobl", label="bobl"
        )
        mock_get_all_terms.return_value = [mock_reference]
        context = self._create_and_check_base_context()
        self.assertNotIn(mock_id, context)


if __name__ == "__main__":
    unittest.main()
