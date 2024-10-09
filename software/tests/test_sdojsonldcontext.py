#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import json
import unittest
import unittest.mock
import logging

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software
import software.SchemaTerms.sdotermsource as sdotermsource
import software.util.sdojsonldcontext as sdojsonldcontext
import software.SchemaTerms.sdoterm as sdoterm


class SdoJsonLdContextTest(unittest.TestCase):
    """Tests for the sdojsonldcontext library."""

    @unittest.skip(
        "createcontext outputs invalid JSON when getAllTerms returns an empty list."
    )
    @unittest.mock.patch("software.SchemaTerms.sdotermsource.SdoTermSource.getAllTerms")
    def test_createcontextEmpty(self, mock_getAllTerms):
        """Test that createcontext outputs valid JSON data"""
        mock_getAllTerms.return_value = []
        json_data = sdojsonldcontext.createcontext()
        parsed = json.loads(json_data)
        self.assertIn("@context", parsed)
        context = parsed["@context"]
        self.assertIn("type", context)
        self.assertIn("id", context)
        self.assertIn("@vocab", context)

    @unittest.mock.patch("software.SchemaTerms.sdotermsource.SdoTermSource.getAllTerms")
    def test_createcontextOneProperty(self, mock_getAllTerms):
        """Test that createcontext outputs valid JSON data"""
        self.maxDiff = None
        mock_id = "1234"
        mock_property = sdoterm.SdoProperty(
            term_id=mock_id, uri="http://schema.org/thang", label="thang"
        )
        mock_property.domainIncludes.setIds(["Thing"])
        mock_property.rangeIncludes.setIds(["Date", "URL", "Thing"])
        mock_getAllTerms.return_value = [mock_property]
        json_data = sdojsonldcontext.createcontext()
        parsed = json.loads(json_data)
        self.assertIn("@context", parsed)
        context = parsed["@context"]
        self.assertIn("type", context)
        self.assertIn("id", context)
        self.assertIn("@vocab", context)
        self.assertEqual(
            context[mock_id], {"@id": "http://schema.org/thang", "@type": "Date"}
        )

    @unittest.mock.patch("software.SchemaTerms.sdotermsource.SdoTermSource.getAllTerms")
    def test_createcontextOneDataType(self, mock_getAllTerms):
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

    @unittest.mock.patch("software.SchemaTerms.sdotermsource.SdoTermSource.getAllTerms")
    def test_createcontextOneEnumeration(self, mock_getAllTerms):
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

    @unittest.mock.patch("software.SchemaTerms.sdotermsource.SdoTermSource.getAllTerms")
    def test_createcontextOneEnumerationValue(self, mock_getAllTerms):
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

    @unittest.skip(
        "createcontext outputs invalid JSON when getAllTerms returns an empty list."
    )
    @unittest.mock.patch("software.SchemaTerms.sdotermsource.SdoTermSource.getAllTerms")
    def test_createcontextOneReference(self, mock_getAllTerms):
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
        self.assertEqual(context[mock_id], {"@id": "http://schema.org/Bobl"})

    @unittest.mock.patch("software.SchemaTerms.sdotermsource.SdoTermSource.getAllTerms")
    def test_createcontextMultiple(self, mock_getAllTerms):
        self.maxDiff = None
        mock_property = sdoterm.SdoProperty(
            term_id="aa", uri="http://schema.org/a", label="a"
        )
        mock_property.domainIncludes.setIds(["Thing"])
        mock_property.rangeIncludes.setIds(["Date", "URL", "Thing"])
        mock_enumeration = sdoterm.SdoEnumeration(
            term_id="bb", uri="http://schema.org/b", label="b"
        )
        mock_enumeration_value = sdoterm.SdoEnumerationvalue(
            term_id="cc", uri="http://schema.org/c", label="c"
        )
        mock_getAllTerms.return_value = [
            mock_property,
            mock_enumeration,
            mock_enumeration_value,
        ]
        json_data = sdojsonldcontext.createcontext()
        parsed = json.loads(json_data)
        self.assertIn("@context", parsed)
        self.assertEqual(
            dict([(k, v) for k, v in parsed["@context"].items() if k in ["aa", "bb", "cc"]]),
            {
                "aa": {"@id": "http://schema.org/a", "@type": "Date"},
                "bb": {"@id": "http://schema.org/b"},
                "cc": {"@id": "http://schema.org/c"},
            },
        )


if __name__ == "__main__":
    unittest.main()
