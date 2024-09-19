#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys

for path in [os.getcwd(),"software/Util","software/SchemaTerms","software/SchemaExamples"]:
  sys.path.insert(1, path ) #Pickup libs from local  directories

import unittest
import sdocollaborators

TEST_DESCRIPTION = """---
img: http://example.com/logo.png
title: Test Foundation
url: http://example.com
--- DescriptionText.md
--- AcknowledgementText.md
This is a test.
"""


class SdoCollaboratorTest(unittest.TestCase):
  """Tests for the dodcollaborators library."""

  def test_collaborator(self):
    """Test the collaborator instance parsing."""
    collab = sdocollaborators.collaborator(ref="/tmp/test", desc=TEST_DESCRIPTION)
    self.assertEqual(collab.uri, 'https://schema.org/tmp/test')
    self.assertEqual(collab.description, '--- DescriptionText.md')
    self.assertEqual(collab.acknowledgement, '--- AcknowledgementText.md')


if __name__ == "__main__":
    unittest.main()
