#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys

for path in [os.getcwd(),"software/Util","software/SchemaTerms","software/SchemaExamples"]:
  sys.path.insert(1, path ) #Pickup libs from local  directories

import json
import unittest
import logging
import sdojsonldcontext

class SdoJsonLdContextTest(unittest.TestCase):
  """Tests for the sdojsonldcontext library."""

  @classmethod
  def setUpClass(cls):
    cls.log = logging.getLogger(__name__)
    cls.log.info("Creating SDO Json-LD Context")
    cls.json_data = sdojsonldcontext.createcontext()
    cls.log.info("Done")

  def test_createcontext(self):
    """Test that createcontext outputs valid JSON data"""
    parsed = json.loads(self.json_data)
    self.assertIn("@context", parsed)
    context = parsed["@context"]
    self.assertIn("type", context)
    self.assertIn("id", context)
    self.assertIn("@vocab", context)


if __name__ == "__main__":
  unittest.main()
