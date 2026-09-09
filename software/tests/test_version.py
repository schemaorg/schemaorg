#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from datetime import datetime
import json
from pathlib import Path
import tempfile
import unittest

from schemaorg import constants
from schemaorg.version import Version


class TestVersion(unittest.TestCase):
    """Unit tests for the Version class in schemaorg.version."""

    def test_init_explicit_path(self):
        """The shipped versions.json parses into a non-empty Version."""
        v = Version(constants.PROJECT_ROOT / "versions.json")
        self.assertEqual(v.versions_path, constants.PROJECT_ROOT / "versions.json")
        self.assertTrue(v.versions_path.exists())
        self.assertTrue(v.versions())
        self.assertTrue(v.current().number())

    def test_init_missing_path_raises(self):
        """Test initialization without path raises TypeError."""
        with self.assertRaises(TypeError):
            Version()  # type: ignore

    def test_init_missing_path_raises(self):
        """Test initialization without path raises TypeError."""
        with self.assertRaises(TypeError):
            Version()  # type: ignore

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
            self.assertEqual(v.current().date(), "2020-01-01")
            self.assertEqual(str(v.current()), "1.0")

    def test_current(self):
        """current() is one of versions(), with a parseable date."""
        v = Version(constants.PROJECT_ROOT / "versions.json")
        curr = v.current()
        self.assertIn(curr, v.versions())
        self.assertTrue(curr.number())
        self.assertEqual(str(curr), curr.number())
        datetime.strptime(curr.date(), "%Y-%m-%d")

    def test_versions(self):
        """Every entry in the shipped versions.json parses."""
        v = Version(constants.PROJECT_ROOT / "versions.json")
        all_vers = v.versions()
        self.assertIsInstance(all_vers, list)
        self.assertTrue(all_vers)
        for item in all_vers:
            self.assertIsInstance(item.number(), str)
            self.assertTrue(item.number())
            datetime.strptime(item.date(), "%Y-%m-%d")

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
