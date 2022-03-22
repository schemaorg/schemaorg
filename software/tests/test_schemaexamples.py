#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys
import unittest
import tempfile

for path in [os.getcwd(),"software/util","software/SchemaTerms","software/SchemaExamples"]:
  sys.path.insert( 1, path ) #Pickup libs from local directories

import schemaexamples

THING_EXAMPLE = """TYPES: #eg-0999 Thing

PRE-MARKUP:
<p>This is a thing</p>

MICRODATA:
<p itemscope itemtype="https://schema.org/Thing">This is a thing</p>

RDFA:

JSON:

{"@context": "https://schema.org/", "@type": "Thing", }

"""

class TestExampleFileParser(unittest.TestCase):
  """Test the example file parser logic"""

  def setUp(self):
    self.parser = schemaexamples.ExampleFileParser()
    self.temp_file = tempfile.NamedTemporaryFile()

  def test_empty(self):
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

  def test_thing(self):
    self.temp_file.write(THING_EXAMPLE.encode('utf8'))
    self.temp_file.seek(0)
    result = self.parser.parse(self.temp_file.name)
    self.assertEqual(len(result), 1)
    self.assertTrue(result[0].hasValidId())
    self.assertEqual(result[0].getIdNum(), 999)
    self.assertCountEqual(result[0].terms, ['Thing'])
    self.assertEqual(
        result[0].getHtml().strip(), '<p>This is a thing</p>', result[0].serialize())
    self.assertEqual(
        result[0].getMicrodata().strip(),
        '<p itemscope itemtype="https://schema.org/Thing">This is a thing</p>',
        result[0].serialize())
    self.assertEqual(
        result[0].getJsonld().strip(),
        '{"@context": "https://schema.org/", "@type": "Thing", }',
        result[0].serialize())


if __name__ == '__main__':
    unittest.main()