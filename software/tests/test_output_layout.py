#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Unit tests for schemaorg.layout.output_layout."""

from pathlib import Path
import tempfile
import unittest

from schemaorg.layout.domain import Domain
from schemaorg.layout.output_layout import OutputLayout


class TestOutputLayout(unittest.TestCase):
    """Test suite for OutputLayout."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_root = Path(self.temp_dir.name) / "site"
        self.layout = OutputLayout(self.output_root)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_dir_standard(self):
        docs_dir = self.layout.dir(Domain.DOCS)
        self.assertTrue(docs_dir.is_dir())
        self.assertEqual(docs_dir, self.output_root / "docs")

    def test_dir_gcloud(self):
        gcloud_dir = self.layout.dir(Domain.GCLOUD)
        self.assertTrue(gcloud_dir.is_dir())
        self.assertEqual(gcloud_dir, self.output_root / "gcloud")

    def test_dir_release_is_version_agnostic(self):
        release_dir = self.layout.dir(Domain.RELEASE)
        self.assertTrue(release_dir.is_dir())
        self.assertEqual(release_dir, self.output_root / "releases")

    def test_file(self):
        f = self.layout.file(Domain.DOCS_COLLAB, "w3c.html")
        self.assertTrue(f.parent.is_dir())
        self.assertEqual(f, self.output_root / "docs" / "collab" / "w3c.html")


if __name__ == "__main__":
    unittest.main()
