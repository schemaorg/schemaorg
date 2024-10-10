#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import sys
import unittest


# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software.SchemaTerms.sdocollaborators as sdocollaborators

TEST_DESCRIPTION = """---
img: http://example.com/logo.png
title: Test Foundation
url: http://example.com
--- DescriptionText.md
This is a _test_ description.
--- AcknowledgementText.md
This is a `test` acknowledgement.
"""


class SdoCollaboratorTest(unittest.TestCase):
    """Tests for the dodcollaborators library."""

    def test_collaborator(self):
        """Test the collaborator instance parsing."""
        collab = sdocollaborators.collaborator(ref="/tmp/test", desc=TEST_DESCRIPTION)
        self.assertEqual(collab.uri, "https://schema.org/tmp/test")
        self.assertEqual(collab.title, "Test Foundation")
        self.assertEqual(collab.img, "http://example.com/logo.png")
        self.assertEqual(collab.description, "This is a <em>test</em> description.")
        self.assertEqual(collab.acknowledgement, "This is a <code>test</code> acknowledgement.")


if __name__ == "__main__":
    unittest.main()
