#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest

from schemaorg.version import Version
import util.schema as schema


class TestSchema(unittest.TestCase):
    """Unit tests for util.schema module."""

    def test_schema_version_instance(self):
        self.assertIsInstance(schema.VERSION, Version)
        self.assertTrue(schema.VERSION.current().number())

    def test_output_dirs(self):
        self.assertEqual(schema.getOutputDir(), "software/site")
        self.assertEqual(schema.getDocsOutputDir(), "software/site/docs")

    def test_has_opt(self):
        self.assertFalse(schema.hasOpt("nonexistent_opt"))


if __name__ == "__main__":
    unittest.main()
