from __future__ import annotations

import json
import unittest
from unittest.mock import patch

import SchemaTerms.sdoterm as sdoterm
import util.sdojsonldcontext as sdojsonldcontext


class SdoJsonLdContextTest(unittest.TestCase):
    @patch("SchemaTerms.sdotermsource.SdoTermSource.getAllTerms")
    def test_createcontextEmpty(self, mock_getAllTerms) -> None:
        mock_getAllTerms.return_value = []
        json_data = sdojsonldcontext.createcontext()
        parsed = json.loads(json_data)
        self.assertIn("@context", parsed)
        context = parsed["@context"]
        self.assertIn("type", context)
        self.assertIn("id", context)
        self.assertIn("@vocab", context)

    @patch("SchemaTerms.sdotermsource.SdoTermSource.getAllTerms")
    def test_createcontextOneProperty(self, mock_getAllTerms) -> None:
        self.maxDiff = None
        mock_id = "1234"
        mock_property = sdoterm.SdoProperty(
            term_id=mock_id, uri="http://schema.org/thang", label="thang"
        )
        mock_property.domainIncludes.setIds(["Thing"])
        mock_property.rangeIncludes.setIds(["Date", "Thing"])
        mock_getAllTerms.return_value = [mock_property]
        json_data = sdojsonldcontext.createcontext()
        parsed = json.loads(json_data)
        self.assertIn("@context", parsed)
        context = parsed["@context"]
        self.assertIn("type", context)
        self.assertIn("id", context)
        self.assertIn("@vocab", context)

        # Historically, @type=Date (or @type=id) was included for non-Text-related properties. Since we support multiple
        # datatypes/things for properties, this led to inaccurate datatype results and inconsistent usage of
        # datatypes/IRIs for property values (post-JSON-LD processing). This test helps ensure it is not unintentionally
        # re-introduced and to document a bit more of the background.
        self.assertEqual(
            context[mock_id], {"@id": "http://schema.org/thang"}
        )

    @patch("SchemaTerms.sdotermsource.SdoTermSource.getAllTerms")
    def test_createcontextOneDataType(self, mock_getAllTerms) -> None:
        self.maxDiff = None
        mock_id = "1234"
        mock_type = sdoterm.SdoDataType(
            term_id=mock_id, uri="http://schema.org/Fnubl", label="fnubl"
        )
        mock_type.properties.setIds(["thang"])
        mock_type.expectedTypeFor.setIds(["Thing"])
        mock_getAllTerms.return_value = [mock_type]
        json_data = sdojsonldcontext.createcontext()
        parsed = json.loads(json_data)
        self.assertIn("@context", parsed)
        context = parsed["@context"]
        self.assertIn("type", context)
        self.assertIn("id", context)
        self.assertIn("@vocab", context)
        self.assertEqual(context[mock_id], {"@id": "http://schema.org/Fnubl"})

    @patch("SchemaTerms.sdotermsource.SdoTermSource.getAllTerms")
    def test_createcontextOneEnumeration(self, mock_getAllTerms) -> None:
        self.maxDiff = None
        mock_id = "1234"
        mock_enumeration = sdoterm.SdoEnumeration(
            term_id=mock_id, uri="http://schema.org/Grabl", label="grabl"
        )
        mock_enumeration.expectedTypeFor.setIds(["Thing"])
        mock_getAllTerms.return_value = [mock_enumeration]
        json_data = sdojsonldcontext.createcontext()
        parsed = json.loads(json_data)
        self.assertIn("@context", parsed)
        context = parsed["@context"]
        self.assertIn("type", context)
        self.assertIn("id", context)
        self.assertIn("@vocab", context)
        self.assertEqual(context[mock_id], {"@id": "http://schema.org/Grabl"})

    @patch("SchemaTerms.sdotermsource.SdoTermSource.getAllTerms")
    def test_createcontextOneEnumerationValue(self, mock_getAllTerms) -> None:
        self.maxDiff = None
        mock_id = "1234"
        mock_enumeration = sdoterm.SdoEnumerationvalue(
            term_id=mock_id, uri="http://schema.org/Bobl", label="bobl"
        )
        mock_getAllTerms.return_value = [mock_enumeration]
        json_data = sdojsonldcontext.createcontext()
        parsed = json.loads(json_data)
        self.assertIn("@context", parsed)
        context = parsed["@context"]
        self.assertIn("type", context)
        self.assertIn("id", context)
        self.assertIn("@vocab", context)
        self.assertEqual(context[mock_id], {"@id": "http://schema.org/Bobl"})

    @patch("SchemaTerms.sdotermsource.SdoTermSource.getAllTerms")
    def test_createcontextOneReference(self, mock_getAllTerms) -> None:
        self.maxDiff = None
        mock_id = "1234"
        mock_reference = sdoterm.SdoReference(
            term_id=mock_id, uri="http://schema.org/Bobl", label="bobl"
        )
        mock_getAllTerms.return_value = [mock_reference]
        json_data = sdojsonldcontext.createcontext()
        parsed = json.loads(json_data)
        self.assertIn("@context", parsed)
        context = parsed["@context"]
        self.assertIn("type", context)
        self.assertIn("id", context)
        self.assertIn("@vocab", context)
        self.assertNotIn(mock_id, context)


if __name__ == "__main__":
    unittest.main()
