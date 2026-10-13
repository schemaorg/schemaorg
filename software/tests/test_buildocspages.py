#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

import SchemaTerms.sdotermsource as sdotermsource
import util.buildocspages as buildocspages


class TestBuildDocs(unittest.TestCase):
    """Test the buildocspages package."""

    @classmethod
    def setUpClass(cls):
        sdotermsource.SdoTermSource.sourceGraph()

    def testJsonldtree(self):
        buildocspages.jsonldtree(page=None)


if __name__ == "__main__":
    unittest.main()
