#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from pathlib import Path
import tempfile
import unittest

from schemaorg import constants
from schemaorg.version import Version


class TestVersion(unittest.TestCase):
    """Unit tests for the Version class in schemaorg.version."""

    def test_init_default_path(self):
        """Test default initialization pointing to root versions.json."""
        v = Version()
        self.assertEqual(v.versions_path, constants.PROJECT_ROOT / "versions.json")
        self.assertTrue(v.versions_path.exists())
        self.assertEqual(v.current().number(), "30.0")
        self.assertTrue(len(v.versions()) > 0)

    def test_init_custom_path(self):
        """Test initialization with custom versions.json path."""
        data = {
            "schemaversion": "1.0",
            "releaseLog": {"1.0": "2020-01-01"},
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_file = Path(tmp_dir) / "versions.json"
            tmp_file.write_text(json.dumps(data), encoding="utf-8")

            v = Version(tmp_file)
            self.assertEqual(v.versions_path, tmp_file)
            self.assertEqual(v.current().number(), "1.0")

    def test_current(self):
        """Test current() returns a VersionItem with number() and date()."""
        v = Version()
        curr = v.current()
        self.assertEqual(curr.number(), "30.0")
        self.assertEqual(curr.date(), "2026-03-19")
        self.assertEqual(str(curr), "30.0")

    def test_versions(self):
        """Test versions() returns a list of VersionItem objects."""
        v = Version()
        all_vers = v.versions()
        self.assertIsInstance(all_vers, list)
        numbers = [item.number() for item in all_vers]
        self.assertIn("30.0", numbers)
        self.assertIn("2.0", numbers)
        for item in all_vers:
            self.assertIsInstance(item.number(), str)
            self.assertTrue(item.date() is None or isinstance(item.date(), str))

    def test_version_item(self):
        """Test VersionItem properties and methods."""
        from schemaorg.version import VersionItem

        item = VersionItem("30.0", "2026-03-19")
        self.assertEqual(item.number(), "30.0")
        self.assertEqual(item.date(), "2026-03-19")
        self.assertEqual(str(item), "30.0")


    def test_add_version_success(self):

        """Test adding a newer version updates releaseLog and schemaversion."""
        initial_data = {
            "schemaversion": "1.0",
            "releaseLog": {
                "1.0": "2020-01-01",
                "0.9": "2019-01-01",
            },
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_file = Path(tmp_dir) / "versions.json"
            tmp_file.write_text(json.dumps(initial_data), encoding="utf-8")

            v = Version(tmp_file)
            v.add_version("1.1", "2021-01-01")

            saved_data = json.loads(tmp_file.read_text(encoding="utf-8"))
            self.assertEqual(saved_data["schemaversion"], "1.1")
            self.assertEqual(saved_data["releaseLog"]["1.1"], "2021-01-01")

    def test_add_older_version(self):
        """Test adding an older version does not change schemaversion."""
        initial_data = {
            "schemaversion": "2.0",
            "releaseLog": {
                "2.0": "2022-01-01",
            },
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_file = Path(tmp_dir) / "versions.json"
            tmp_file.write_text(json.dumps(initial_data), encoding="utf-8")

            v = Version(tmp_file)
            v.add_version("1.5", "2021-06-01")

            saved_data = json.loads(tmp_file.read_text(encoding="utf-8"))
            self.assertEqual(saved_data["schemaversion"], "2.0")
            self.assertEqual(saved_data["releaseLog"]["1.5"], "2021-06-01")

    def test_add_version_exists_raises(self):
        """Test add_version raises when the version already exists."""
        initial_data = {
            "schemaversion": "1.0",
            "releaseLog": {
                "1.0": "2020-01-01",
            },
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_file = Path(tmp_dir) / "versions.json"
            tmp_file.write_text(json.dumps(initial_data), encoding="utf-8")

            v = Version(tmp_file)
            with self.assertRaises(Exception):
                v.add_version("1.0", "2020-01-01")

    def test_add_version_empty_raises(self):
        """Test add_version raises when version_number is empty."""
        initial_data = {
            "schemaversion": "1.0",
            "releaseLog": {
                "1.0": "2020-01-01",
            },
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_file = Path(tmp_dir) / "versions.json"
            tmp_file.write_text(json.dumps(initial_data), encoding="utf-8")

            v = Version(tmp_file)
            with self.assertRaises(Exception):
                v.add_version("", "2021-01-01")

    def test_add_version_invalid_date_raises(self):
        """Test add_version raises when date format is not YYYY-MM-DD."""
        initial_data = {
            "schemaversion": "1.0",
            "releaseLog": {
                "1.0": "2020-01-01",
            },
        }
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_file = Path(tmp_dir) / "versions.json"
            tmp_file.write_text(json.dumps(initial_data), encoding="utf-8")

            v = Version(tmp_file)
            with self.assertRaises(Exception):
                v.add_version("1.2", "01-01-2021")


if __name__ == "__main__":
    unittest.main()
