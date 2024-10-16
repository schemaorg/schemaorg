#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import os
import sys
import tempfile

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software
import software.util.fileutils as fileutils

class FileUtilsTest(unittest.TestCase):


    def test_checkFilePath(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            fileutils.checkFilePath(tmp_dir)

    def test_ensureAbsolutePath(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = fileutils.ensureAbsolutePath(output_dir=tmp_dir, relative_path='fnord/fnuble')
            self.assertEqual(os.path.basename(path), 'fnuble')
            self.assertEqual(os.path.split(os.path.dirname(path))[-1], 'fnord')

    def test_releaseFilePath(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            path = fileutils.releaseFilePath(output_dir=tmp_dir, version='42', selector='all', protocol='http', output_format='json-ld')
            self.assertEqual(os.path.basename(path), 'schemaorg-all-http.jsonld')
            self.assertEqual(os.path.split(os.path.dirname(path))[-1], '42')


if __name__ == "__main__":
    unittest.main()
