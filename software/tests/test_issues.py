#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Unit tests for schemaorg.layout.issues."""

from pathlib import Path
import tempfile
import unittest

from schemaorg.layout import ALL_ISSUES, Domain, InputLayout, Issues


class TestIssues(unittest.TestCase):
    """Test suite for Issues file discovery class."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.layout = InputLayout(self.root)
        self.issues = Issues(self.layout)

        # Create directory structure under data
        data_dir = self.root / "data"
        (data_dir / "ext" / "auto").mkdir(parents=True, exist_ok=True)
        (data_dir / "ext" / "bib").mkdir(parents=True, exist_ok=True)

        # Create core data files
        self.core_ttl = data_dir / "schema.ttl"
        self.core_examples = data_dir / "sdo-examples.txt"
        self.core_ttl.touch()
        self.core_examples.touch()

        # Create base extension files (non-issue)
        self.ext_ttl = data_dir / "ext" / "auto" / "auto.ttl"
        self.ext_examples = data_dir / "ext" / "auto" / "auto-examples.txt"
        self.ext_ttl.touch()
        self.ext_examples.touch()

        # Create issue files for issue 100
        self.issue100_ttl = data_dir / "ext" / "auto" / "issue-100.ttl"
        self.issue100_examples = data_dir / "ext" / "auto" / "issue-100-examples.txt"
        self.issue100_ttl.touch()
        self.issue100_examples.touch()

        # Create issue files for issue 200
        self.issue200_ttl = data_dir / "ext" / "bib" / "issue-200.ttl"
        self.issue200_examples = data_dir / "ext" / "bib" / "issue-200-examples.txt"
        self.issue200_ttl.touch()
        self.issue200_examples.touch()

    def tearDown(self):
        self.temp_dir.cleanup()


    def test_get_issue_numbers(self):
        numbers = self.issues.get_issue_numbers()
        self.assertEqual(numbers, ["100", "200"])

    def test_get_ttl_files_all(self):
        files = self.issues.get_ttl_files()
        expected = sorted([
            self.core_ttl,
            self.ext_ttl,
            self.issue100_ttl,
            self.issue200_ttl,
        ])
        self.assertEqual(files, expected)

    def test_get_ttl_files_filtered(self):
        files = self.issues.get_ttl_files(["100"])
        expected = sorted([
            self.core_ttl,
            self.ext_ttl,
            self.issue100_ttl,
        ])
        self.assertEqual(files, expected)

    def test_get_example_files_all(self):
        files = self.issues.get_example_files()
        expected = sorted([
            self.core_examples,
            self.ext_examples,
            self.issue100_examples,
            self.issue200_examples,
        ])
        self.assertEqual(files, expected)

    def test_get_example_files_filtered(self):
        files = self.issues.get_example_files(["200"])
        expected = sorted([
            self.core_examples,
            self.ext_examples,
            self.issue200_examples,
        ])
        self.assertEqual(files, expected)

    def test_get_ttl_files_nonexistent_issue(self):
        files = self.issues.get_ttl_files(["9999"])
        expected = sorted([
            self.core_ttl,
            self.ext_ttl,
        ])
        self.assertEqual(files, expected)

    def test_get_ttl_files_multiple_issues(self):
        files = self.issues.get_ttl_files(["100", "200"])
        expected = sorted([
            self.core_ttl,
            self.ext_ttl,
            self.issue100_ttl,
            self.issue200_ttl,
        ])
        self.assertEqual(files, expected)


if __name__ == "__main__":
    unittest.main()
