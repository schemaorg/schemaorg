#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import unittest

import software

import SchemaExamples.schemaexamples as schemaexamples
import SchemaTerms.sdoterm as sdoterm
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
