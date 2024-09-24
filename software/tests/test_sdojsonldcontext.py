#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

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

    @unittest.skip("createcontext outputs invalid JSON when getAllTerms returns an empty list.")
    @unittest.mock.patch('software.SchemaTerms.sdotermsource.SdoTermSource.getAllTerms')
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


    @unittest.mock.patch('software.SchemaTerms.sdotermsource.SdoTermSource.getAllTerms')
    def test_createcontextOneProperty(self, mock_getAllTerms):
        """Test that createcontext outputs valid JSON data"""
        self.maxDiff = None
        mock_id = '1234'
        mock_property = sdoterm.SdoProperty(Id=mock_id, uri='http://schema.org/thang', label='thang')
        mock_property.domainIncludes = ['Thing']
        mock_property.rangeIncludes = ['Date', 'URL', 'Thing']
        mock_getAllTerms.return_value = [mock_property]
        json_data = sdojsonldcontext.createcontext()
        parsed = json.loads(json_data)
        self.assertIn("@context", parsed)
        context = parsed["@context"]
        self.assertIn("type", context)
        self.assertIn("id", context)
        self.assertIn("@vocab", context)
        self.assertEqual(context[mock_id], {'@id': 'http://schema.org/thang', '@type': 'Date'})

    @unittest.mock.patch('software.SchemaTerms.sdotermsource.SdoTermSource.getAllTerms')
    def test_createcontextOneDataType(self, mock_getAllTerms):
        self.maxDiff = None
        mock_id = '1234'
        mock_type = sdoterm.SdoDataType(Id=mock_id, uri='http://schema.org/Fnubl', label='fnubl')
        mock_type.properties = ['thang']
        mock_type.expectedTypeFor = ['Thing']
        mock_getAllTerms.return_value = [mock_type]
        json_data = sdojsonldcontext.createcontext()
        parsed = json.loads(json_data)
        self.assertIn("@context", parsed)
        context = parsed["@context"]
        self.assertIn("type", context)
        self.assertIn("id", context)
        self.assertIn("@vocab", context)
        self.assertEqual(context[mock_id], {'@id': 'http://schema.org/Fnubl'})

    @unittest.mock.patch('software.SchemaTerms.sdotermsource.SdoTermSource.getAllTerms')
    def test_createcontextOneEnumeration(self, mock_getAllTerms):
        self.maxDiff = None
        mock_id = '1234'
        mock_enumeration = sdoterm.SdoEnumeration(Id=mock_id, uri='http://schema.org/Grabl', label='grabl')
        mock_enumeration.expectedTypeFor = ['Thing']
        mock_getAllTerms.return_value = [mock_enumeration]
        json_data = sdojsonldcontext.createcontext()
        parsed = json.loads(json_data)
        self.assertIn("@context", parsed)
        context = parsed["@context"]
        self.assertIn("type", context)
        self.assertIn("id", context)
        self.assertIn("@vocab", context)
        self.assertEqual(context[mock_id], {'@id': 'http://schema.org/Grabl'})

    @unittest.mock.patch('software.SchemaTerms.sdotermsource.SdoTermSource.getAllTerms')
    def test_createcontextOneEnumerationValue(self, mock_getAllTerms):
        self.maxDiff = None
        mock_id = '1234'
        mock_enumeration = sdoterm.SdoEnumerationvalue(Id=mock_id, uri='http://schema.org/Bobl', label='bobl')
        mock_getAllTerms.return_value = [mock_enumeration]
        json_data = sdojsonldcontext.createcontext()
        parsed = json.loads(json_data)
        self.assertIn("@context", parsed)
        context = parsed["@context"]
        self.assertIn("type", context)
        self.assertIn("id", context)
        self.assertIn("@vocab", context)
        self.assertEqual(context[mock_id], {'@id': 'http://schema.org/Bobl'})

    @unittest.skip("createcontext outputs invalid JSON when getAllTerms returns an empty list.")
    @unittest.mock.patch('software.SchemaTerms.sdotermsource.SdoTermSource.getAllTerms')
    def test_createcontextOneReference(self, mock_getAllTerms):
        self.maxDiff = None
        mock_id = '1234'
        mock_reference = sdoterm.SdoReference(Id=mock_id, uri='http://schema.org/Bobl', label='bobl')
        mock_getAllTerms.return_value = [mock_reference]
        json_data = sdojsonldcontext.createcontext()
        parsed = json.loads(json_data)
        self.assertIn("@context", parsed)
        context = parsed["@context"]
        self.assertIn("type", context)
        self.assertIn("id", context)
        self.assertIn("@vocab", context)
        self.assertEqual(context[mock_id], {'@id': 'http://schema.org/Bobl'})

    @unittest.mock.patch('software.SchemaTerms.sdotermsource.SdoTermSource.getAllTerms')
    def test_createcontextMultiple(self, mock_getAllTerms):
        self.maxDiff = None
        mock_property = sdoterm.SdoProperty(Id='aa', uri='http://schema.org/a', label='a')
        mock_property.domainIncludes = ['Thing']
        mock_property.rangeIncludes = ['Date', 'URL', 'Thing']
        mock_enumeration = sdoterm.SdoEnumeration(Id='bb', uri='http://schema.org/b', label='b')
        mock_enumeration_value = sdoterm.SdoEnumerationvalue(Id='cc', uri='http://schema.org/c', label='c')
        mock_getAllTerms.return_value = [mock_property, mock_enumeration, mock_enumeration_value]
        json_data = sdojsonldcontext.createcontext()
        parsed = json.loads(json_data)
        self.assertEqual(parsed,
            {'@context': {
                '@vocab': 'http://schema.org/',
                'HTML': {'@id': 'rdf:HTML'},
                'aa': {'@id': 'http://schema.org/a', '@type': 'Date'},
                'bb': {'@id': 'http://schema.org/b'},
                'cc': {'@id': 'http://schema.org/c'},
                'csvw': 'http://www.w3.org/ns/csvw#',
                'dc': 'http://purl.org/dc/elements/1.1/',
                'dcam': 'http://purl.org/dc/dcam/',
                'dcat': 'http://www.w3.org/ns/dcat#',
                'dcmitype': 'http://purl.org/dc/dcmitype/',
                'dct': 'http://purl.org/dc/terms/',
                'dcterms': 'http://purl.org/dc/terms/',
                'dctype': 'http://purl.org/dc/dcmitype/',
                'doap': 'http://usefulinc.com/ns/doap#',
                'foaf': 'http://xmlns.com/foaf/0.1/',
                'id': '@id',
                'odrl': 'http://www.w3.org/ns/odrl/2/',
                'org': 'http://www.w3.org/ns/org#',
                'owl': 'http://www.w3.org/2002/07/owl#',
                'prof': 'http://www.w3.org/ns/dx/prof/',
                'prov': 'http://www.w3.org/ns/prov#',
                'qb': 'http://purl.org/linked-data/cube#',
                'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
                'rdfs': 'http://www.w3.org/2000/01/rdf-schema#',
                'schema': 'http://schema.org/',
                'sh': 'http://www.w3.org/ns/shacl#',
                'skos': 'http://www.w3.org/2004/02/skos/core#',
                'sosa': 'http://www.w3.org/ns/sosa/',
                'ssn': 'http://www.w3.org/ns/ssn/',
                'time': 'http://www.w3.org/2006/time#',
                'type': '@type',
                'vann': 'http://purl.org/vocab/vann/',
                'void': 'http://rdfs.org/ns/void#',
                'xml': 'http://www.w3.org/XML/1998/namespace',
                'xsd': 'http://www.w3.org/2001/XMLSchema#'}})

if __name__ == "__main__":
    unittest.main()
