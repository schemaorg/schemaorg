from __future__ import annotations

from datetime import datetime
import json
from pathlib import Path
import tempfile
from typing import Any
import unittest

from schemaorg import constants
from schemaorg.version import Version, VersionItem


class TestVersion(unittest.TestCase):
    def _write_versions(self, data: dict[str, Any]) -> Path:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        tmp_file = Path(temp_dir.name) / constants.VERSIONS_FILE
        tmp_file.write_text(json.dumps(data), encoding="utf-8")
        return tmp_file

    def test_init_explicit_path(self) -> None:
        """The shipped versions.json parses into a non-empty Version."""
        v = Version(constants.PROJECT_ROOT / constants.VERSIONS_FILE)
        self.assertEqual(
            v.versions_path, constants.PROJECT_ROOT / constants.VERSIONS_FILE
        )
        self.assertTrue(v.versions_path.exists())
        self.assertTrue(v.versions())
        self.assertTrue(v.current().number())

    def test_init_missing_path_raises(self) -> None:
        with self.assertRaises(TypeError):
            Version()  # type: ignore[call-arg]

    def test_init_missing_file_raises(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            with self.assertRaises(FileNotFoundError):
                Version(Path(tmp_dir) / constants.VERSIONS_FILE)

    def test_init_custom_path(self) -> None:
        tmp_file = self._write_versions(
            {
                "schemaversion": "1.0",
                "releaseLog": {"1.0": "2020-01-01"},
            }
        )
        v = Version(tmp_file)
        self.assertEqual(v.versions_path, tmp_file)
        self.assertEqual(v.current().number(), "1.0")
        self.assertEqual(v.current().date(), "2020-01-01")
        self.assertEqual(str(v.current()), "1.0")

    def test_init_missing_schemaversion_in_releaselog_raises(self) -> None:
        tmp_file = self._write_versions(
            {
                "schemaversion": "2.0",
                "releaseLog": {"1.0": "2020-01-01"},
            }
        )
        with self.assertRaises(ValueError) as ctx:
            Version(tmp_file)
        self.assertIn("2.0", str(ctx.exception))

    def test_current(self) -> None:
        """current() is one of versions(), with a parseable date."""
        v = Version(constants.PROJECT_ROOT / constants.VERSIONS_FILE)
        curr = v.current()
        self.assertIn(curr, v.versions())
        self.assertTrue(curr.number())
        self.assertEqual(str(curr), curr.number())
        datetime.strptime(curr.date(), "%Y-%m-%d")

    def test_versions(self) -> None:
        """Every entry in the shipped versions.json parses."""
        v = Version(constants.PROJECT_ROOT / constants.VERSIONS_FILE)
        all_vers = v.versions()
        self.assertIsInstance(all_vers, list)
        self.assertTrue(all_vers)
        for item in all_vers:
            self.assertIsInstance(item.number(), str)
            self.assertTrue(item.number())
            datetime.strptime(item.date(), "%Y-%m-%d")

    def test_version_item(self) -> None:
        item = VersionItem("30.0", "2026-03-19")
        self.assertEqual(item.number(), "30.0")
        self.assertEqual(item.date(), "2026-03-19")
        self.assertEqual(str(item), "30.0")

    def test_add_version_success(self) -> None:
        tmp_file = self._write_versions(
            {
                "schemaversion": "1.0",
                "releaseLog": {
                    "1.0": "2020-01-01",
                    "0.9": "2019-01-01",
                },
            }
        )
        v = Version(tmp_file)
        v.add_version("1.1", "2021-01-01")

        saved_data = json.loads(tmp_file.read_text(encoding="utf-8"))
        self.assertEqual(saved_data["schemaversion"], "1.1")
        self.assertEqual(saved_data["releaseLog"]["1.1"], "2021-01-01")

    def test_add_older_version(self) -> None:
        tmp_file = self._write_versions(
            {
                "schemaversion": "2.0",
                "releaseLog": {"2.0": "2022-01-01"},
            }
        )
        v = Version(tmp_file)
        v.add_version("1.5", "2021-06-01")

        saved_data = json.loads(tmp_file.read_text(encoding="utf-8"))
        self.assertEqual(saved_data["schemaversion"], "2.0")
        self.assertEqual(saved_data["releaseLog"]["1.5"], "2021-06-01")

    def test_add_version_exists_raises(self) -> None:
        tmp_file = self._write_versions(
            {
                "schemaversion": "1.0",
                "releaseLog": {"1.0": "2020-01-01"},
            }
        )
        v = Version(tmp_file)
        with self.assertRaises(ValueError):
            v.add_version("1.0", "2020-01-01")

    def test_add_version_empty_raises(self) -> None:
        tmp_file = self._write_versions(
            {
                "schemaversion": "1.0",
                "releaseLog": {"1.0": "2020-01-01"},
            }
        )
        v = Version(tmp_file)
        with self.assertRaises(ValueError):
            v.add_version("", "2021-01-01")

    def test_add_version_invalid_date_raises(self) -> None:
        tmp_file = self._write_versions(
            {
                "schemaversion": "1.0",
                "releaseLog": {"1.0": "2020-01-01"},
            }
        )
        v = Version(tmp_file)
        with self.assertRaises(ValueError):
            v.add_version("1.2", "01-01-2021")


if __name__ == "__main__":
    unittest.main()
