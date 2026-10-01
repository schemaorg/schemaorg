#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Unit tests for schemaorg.layout.input_layout."""

import io
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from schemaorg.layout.domain import Domain
from schemaorg.layout.input_layout import (
    InputLayout,
    checkDataDirectories,
)


class TestInputLayout(unittest.TestCase):
    """Test suite for InputLayout."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.layout = InputLayout(self.root)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_dir_standard(self):
        self.assertEqual(
            self.layout.dir(Domain.DATA),
            self.root / "data"
        )
        self.assertEqual(
            self.layout.dir(Domain.STATIC_DOC_INSERTS),
            self.root / "templates" / "static-doc-inserts"
        )
        self.assertEqual(
            self.layout.dir(Domain.GCLOUD),
            self.root / "software" / "gcloud"
        )
        self.assertEqual(
            self.layout.dir(Domain.ROOT),
            self.root
        )

    def test_dir_release_is_the_unversioned_archive(self):
        self.assertEqual(
            self.layout.dir(Domain.RELEASE),
            self.root / "data" / "releases"
        )

    def test_file(self):
        self.assertEqual(
            self.layout.file(Domain.DOCS, "index.html"),
            self.root / "docs" / "index.html"
        )

    def test_relative_file(self):
        sub_file = self.root / "data" / "sub" / "file.txt"
        self.assertEqual(self.layout.relative_file(sub_file), Path("data/sub/file.txt"))

    def test_files_glob(self):
        data_dir = self.root / "data"
        data_dir.mkdir(parents=True, exist_ok=True)
        f1 = data_dir / "a.ttl"
        f2 = data_dir / "b.ttl"
        f3 = data_dir / "c.txt"
        hidden = data_dir / ".hidden.ttl"
        f1.touch()
        f2.touch()
        f3.touch()
        hidden.touch()

        found = self.layout.files(Domain.DATA, "*.ttl")
        self.assertEqual(found, [f1, f2])

        found_multi = self.layout.files(Domain.DATA, ["*.ttl", "*.txt"])
        self.assertEqual(found_multi, [f1, f2, f3])

        found_reversed = self.layout.files(Domain.DATA, ["*.txt", "*.ttl"])
        self.assertEqual(found_reversed, [f3, f1, f2])

    def test_is_complete(self):
        with self.assertRaises(FileNotFoundError) as ctx:
            self.layout._is_complete()
        for dom in (Domain.DOCS, Domain.GCLOUD, Domain.DATA, Domain.TEMPLATES):
            self.assertIn(str(self.layout.dir(dom)), str(ctx.exception))

        for dom in (Domain.DOCS, Domain.GCLOUD, Domain.DATA, Domain.TEMPLATES):
            self.layout.dir(dom).mkdir(parents=True, exist_ok=True)
        self.assertTrue(self.layout._is_complete())

    @patch("sys.stderr", new_callable=io.StringIO)
    @patch("schemaorg.layout.input_layout.InputLayout._is_complete")
    def test_check_data_directories_fails_on_exception(
        self, mock_is_complete, mock_stderr
    ):
        expected_msg = (
            f'Required directory "{self.root / "docs"}" not found - Exiting\n'
        )
        mock_is_complete.side_effect = FileNotFoundError(expected_msg)
        with self.assertRaises(SystemExit) as ctx:
            checkDataDirectories()
        self.assertEqual(ctx.exception.code, os.EX_CONFIG)
        self.assertIn(expected_msg, mock_stderr.getvalue())

    @patch("schemaorg.layout.input_layout.InputLayout._is_complete")
    def test_check_data_directories_succeeds_when_complete(self, mock_is_complete):
        mock_is_complete.return_value = True
        # Should not raise SystemExit
        checkDataDirectories()


if __name__ == "__main__":
    unittest.main()
