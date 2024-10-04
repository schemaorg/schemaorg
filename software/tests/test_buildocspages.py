#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys
import unittest


# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software
import software.SchemaExamples.schemaexamples as schemaexamples
import software.SchemaTerms.sdoterm as sdoterm
import software.SchemaTerms.sdotermsource as sdotermsource

import software.util.buildocspages as buildocspages


class TestBuildDocs(unittest.TestCase):
    """Test the buildocspages package."""

    @classmethod
    def setUpClass(cls):
        sdotermsource.SdoTermSource.sourceGraph()

    def testJsonldtree(self):
        buildocspages.jsonldtree(page=None)


if __name__ == "__main__":
    unittest.main()