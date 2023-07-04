#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys
import unittest

for path in (os.getcwd(), "software/util", "software/SchemaTerms"):
  sys.path.insert(1, path) #Pickup libs from local directories

import buildtermpages
import schemaexamples
import sdoterm


class TestTermFileName(unittest.TestCase):
  """Test the utility function that creates paths for terms."""
  def testEmpty(self):
    with self.assertRaises(ValueError):
      buildtermpages.termFileName("")

  def testUnicode(self):
    with self.assertRaises(ValueError):
      buildtermpages.termFileName("🟪")

  def testUpper(self):
    self.assertEqual(
        buildtermpages.termFileName("Thingamabob"),
        "software/site/terms/types/T/Thingamabob.html")
  def testLower(self):
    self.assertEqual(
        buildtermpages.termFileName("thingamabob"),
        "software/site/terms/properties/t/thingamabob.html"
    )

  def testDigit(self):
    self.assertEqual(
        buildtermpages.termFileName("4DStatue"),
        "software/site/terms/types/4/4DStatue.html"
    )


class TestBuildTermPages(unittest.TestCase):
  """Test the term page rendering logic."""

  def testTemplateRenderNoExample(self):
    term = sdoterm.SdoTerm(termType=sdoterm.SdoTerm.TYPE, Id=42, uri="http://example.com/whatchicallit", label="whatchicallit")
    output = buildtermpages.termtemplateRender(term=term, examples=[], json='')
    self.assertRegex(output, ".*whatchicallit.*")
    self.assertRegex(output, ".*http://example\.com/whatchicallit.*")

  def testTemplateRenderOneExample(self):
    """Test rendering of one term page."""
    examples = [
      schemaexamples.Example(
          terms=["Thingamabob"], original_html="Awesome & Thingamabob", microdata="", rdfa="", jsonld="",
          exmeta={"file": __file__, "filepos": 0 })
    ]
    json = "[42]"
    term = sdoterm.SdoTerm(termType=sdoterm.SdoTerm.TYPE, Id=42, uri="http://example.com/thingamabob", label="Thingamabob")
    output = buildtermpages.termtemplateRender(term=term, examples=examples, json=json)
    self.assertRegex(output, ".*Thingamabob.*")
    self.assertRegex(output, ".*http://example\.com/thingamabob.*")
    self.assertRegex(output, ".Awesome &amp; Thingamabob.*")



