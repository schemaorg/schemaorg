#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys
import unittest
import tempfile

for path in [os.getcwd(),"software/util","software/SchemaTerms","software/SchemaExamples"]:
  sys.path.insert(1, path) #Pickup libs from local directories

import schemaexamples

THING_EXAMPLE = """TYPES: #eg-0999 Thing

PRE-MARKUP:
<p>This is a thing</p>

MICRODATA:
<p itemscope itemtype="https://schema.org/Thing">This is a thing</p>

RDFA:
<p vocab="https://schema.org/" typeof="Thing">This is a thing</p>

JSON:

{"@context": "https://schema.org/", "@type": "Thing", }

"""

class TestExampleFileParser(unittest.TestCase):
  """Test the example file parser logic."""

  def setUp(self):
    self.parser = schemaexamples.ExampleFileParser()
    self.temp_file = tempfile.NamedTemporaryFile()

  def test_empty_example(self):
    """Test parsing of an empty Example file."""
    with self.assertLogs() as cm:
      result = self.parser.parse(self.temp_file.name)
    self.assertTrue(cm.output)
    self.assertEqual(len(result), 1)
    self.assertFalse(result[0].hasValidId())
    self.assertFalse(result[0].terms)
    self.assertFalse(result[0].getMicrodata())
    self.assertFalse(result[0].getHtml())
    self.assertFalse(result[0].getRdfa())
    self.assertFalse(result[0].getJsonld())

  def test_single_example(self):
    """Test parsing of an Example file containing a single entry."""
    self.temp_file.write(THING_EXAMPLE.encode('utf8'))
    self.temp_file.seek(0)
    result = self.parser.parse(self.temp_file.name)
    self.assertEqual(len(result), 1)
    self.assertTrue(result[0].hasValidId())
    self.assertEqual(result[0].getIdNum(), 999)
    self.assertEqual(result[0].getMeta('file'), self.temp_file.name)
    self.assertCountEqual(result[0].terms, ['Thing'])
    self.assertEqual(
        result[0].getHtml().strip(), '<p>This is a thing</p>', result[0].serialize())
    self.assertEqual(
        result[0].getMicrodata().strip(),
        '<p itemscope itemtype="https://schema.org/Thing">This is a thing</p>',
        result[0].serialize())
    self.assertEqual(
        result[0].getRdfa().strip(),
        '<p vocab="https://schema.org/" typeof="Thing">This is a thing</p>',
        result[0].serialize())
    self.assertEqual(
        result[0].getJsonld().strip(),
        '{"@context": "https://schema.org/", "@type": "Thing", }',
        result[0].serialize())


  def test_two_examples(self):
    """Test parsing of an Example file containing two entries, one of them synthesized."""
    # Write one example
    self.temp_file.write(THING_EXAMPLE.encode('utf8'))
    self.temp_file.write('\n'.encode('utf8'))
    # Create a test example object.
    example = schemaexamples.Example(
          terms=['Offer'], original_html='<b>Offer</b>', microdata='', rdfa='', jsonld='',
          exmeta={'id': 'eg-777', 'file': '/bogus', 'filepos': -1})
    self.assertTrue(example.hasValidId())
    # Serialize it into second position.
    self.temp_file.write(example.serialize().encode('utf8'))
    self.temp_file.seek(0)
    # Try reading both.
    result = self.parser.parse(self.temp_file.name)
    self.assertEqual(len(result), 2)
    self.assertEqual(result[0].getIdNum(), 999)
    self.assertCountEqual(result[0].terms, ['Thing'])
    self.assertEqual(result[1].getIdNum(), 777)
    self.assertCountEqual(result[1].terms, ['Offer'])


if __name__ == '__main__':
    unittest.main()