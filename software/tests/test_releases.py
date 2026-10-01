#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Unit tests for schemaorg.layout.releases."""

import json
from pathlib import Path
import tempfile
import unittest

from schemaorg.constants import PROJECT_ROOT
from schemaorg.layout import (
    Domain,
    InputLayout,
    OutputLayout,
    Protocol,
    Releases,
    Scope,
)
from schemaorg.version import Version
import util.schema as schema

MODERN_FILES = (
    "schemaorg-all-https.ttl",
    "schemaorg-all-http.ttl",
    "schemaorg-current-https.ttl",
    "schemaorg-current-http.ttl",
)


def _make_release(root: Path, version: str, *names: str) -> Path:
    """Creates a release directory containing the named files."""
    release_dir = root / version
    release_dir.mkdir(parents=True, exist_ok=True)
    for name in names or MODERN_FILES:
        (release_dir / name).write_text("# ttl\n", encoding="utf-8")
    return release_dir


class TestReleases(unittest.TestCase):
    """Test suite for Releases."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        root = Path(self.temp_dir.name)

        self.input_layout = InputLayout(root / "source")
        self.output_layout = OutputLayout(root / "output")

        # Every expected path in this suite comes from a layout, never from
        # string surgery: the layouts are the thing under test.
        self.versions_file = self.input_layout.file(
            Domain.ROOT, Releases.VERSIONS_FILE
        )
        self.archive = self.input_layout.dir(Domain.RELEASE)
        self.built = self.output_layout.dir(Domain.RELEASE)

        self.releases = self._declare("29.0", "30.0", current="30.0")

    def tearDown(self):
        self.temp_dir.cleanup()

    def _declare(self, *versions: str, current: str) -> Releases:
        """Writes a versions.json and returns Releases reading it."""
        self.versions_file.parent.mkdir(parents=True, exist_ok=True)
        self.versions_file.write_text(
            json.dumps(
                {
                    "schemaversion": current,
                    "releaseLog": {v: "2020-01-01" for v in versions},
                }
            ),
            encoding="utf-8",
        )
        self.version = Version(self.versions_file)
        self.releases = Releases(self.output_layout, self.version)
        return self.releases

    # -- versions come from versions.json, not from the filesystem -------

    def test_versions_are_read_from_versions_file(self):
        releases = self._declare("9.0", "10.0", "30.0", current="30.0")
        self.assertEqual(
            {v.number() for v in releases.versions()}, {"9.0", "10.0", "30.0"}
        )

    def test_versions_passes_through_the_version_log(self):
        releases = self._declare("2.0", "10.0", "9.0", current="10.0")
        self.assertEqual(releases.versions(), releases.version.versions())

    def test_current_is_the_declared_current_version(self):
        releases = self._declare("29.0", "30.0", "31.0", current="30.0")
        self.assertEqual(releases.current().number(), "30.0")

    def test_resolve_accepts_string_item_and_none(self):
        item = self.releases.resolve("29.0")
        self.assertEqual(item.number(), "29.0")
        self.assertEqual(self.releases.resolve(item).number(), "29.0")
        self.assertEqual(self.releases.resolve().number(), "30.0")

    def test_resolve_rejects_undeclared_version(self):
        with self.assertRaises(ValueError) as context:
            self.releases.resolve("99.0")
        self.assertIn("not declared", str(context.exception))

    # -- locations: computed, never searched for -------------------------

    def test_dir_is_the_version_under_the_layouts_release_dir(self):
        self.assertEqual(self.releases.dir("29.0"), self.built / "29.0")
        self.assertEqual(
            Releases(self.input_layout, self.version).dir("29.0"),
            self.archive / "29.0",
        )

    def test_dir_defaults_to_current(self):
        self.assertEqual(self.releases.dir(), self.built / "30.0")

    def test_dir_does_not_require_the_release_to_exist(self):
        path = self.releases.dir("29.0")
        self.assertFalse(path.exists())

    def test_dir_ignores_the_other_tree(self):
        _make_release(self.archive, "30.0")
        self.assertNotEqual(self.releases.dir("30.0"), self.archive / "30.0")

    def test_dir_rejects_undeclared_version(self):
        with self.assertRaises(ValueError):
            self.releases.dir("99.0")

    # -- reading ---------------------------------------------------------

    def test_get_ttl_files_raises_for_declared_but_absent_release(self):
        with self.assertRaises(FileNotFoundError) as context:
            self.releases.get_ttl_files("29.0")
        self.assertIn("declared but not present", str(context.exception))

    def test_get_ttl_files_returns_exactly_one(self):
        _make_release(self.built, "30.0", *MODERN_FILES, "httpequivs.ttl")
        files = self.releases.get_ttl_files("30.0")
        self.assertEqual([f.name for f in files], ["schemaorg-all-https.ttl"])

    def test_get_ttl_files_honours_protocol_and_scope(self):
        _make_release(self.built, "30.0")
        files = self.releases.get_ttl_files(
            "30.0", protocol=Protocol.HTTP, scope=Scope.CURRENT
        )
        self.assertEqual(
            [f.name for f in files], ["schemaorg-current-http.ttl"]
        )

    def test_every_protocol_and_scope_combination_resolves(self):
        _make_release(self.built, "30.0")
        names = {
            self.releases.get_ttl_files("30.0", protocol=p, scope=s)[0].name
            for p in Protocol
            for s in Scope
        }
        self.assertEqual(names, set(MODERN_FILES))

    def test_get_ttl_files_rejects_legacy_layout(self):
        _make_release(self.built, "29.0", "schema.ttl", "ext-bib.ttl")
        with self.assertRaises(FileNotFoundError) as context:
            self.releases.get_ttl_files("29.0")
        self.assertIn("schemaorg-all-https.ttl", str(context.exception))

    # -- file: directory creation belongs to the layout ------------------

    def test_file_creates_the_release_directory_for_output_layout(self):
        target = self.releases.dir("30.0")
        self.assertFalse(target.exists())
        path = self.releases.file("30.0")
        self.assertEqual(path, target / "schemaorg-all-https.ttl")
        self.assertTrue(target.is_dir())

    def test_file_does_not_create_the_release_directory_for_input_layout(self):
        releases = Releases(self.input_layout, self.version)
        target = releases.dir("30.0")
        self.assertFalse(target.exists())
        path = releases.file("30.0")
        self.assertEqual(path, target / "schemaorg-all-https.ttl")
        self.assertFalse(target.exists())

    def test_file_honours_filename_override(self):
        target = self.releases.dir("30.0")
        path = self.releases.file("30.0", filename="schemaorg.owl")
        self.assertEqual(path, target / "schemaorg.owl")

    def test_file_defaults_to_the_current_https_ttl(self):
        path = self.releases.file()
        self.assertEqual(path, self.built / "30.0" / "schemaorg-all-https.ttl")

    def test_file_honours_the_extension(self):
        path = self.releases.file("30.0", extension=".nt")
        self.assertEqual(path.name, "schemaorg-all-https.nt")

    def test_file_honours_protocol_and_scope(self):
        path = self.releases.file(
            "30.0",
            protocol=Protocol.HTTP,
            scope=Scope.CURRENT,
            extension=".jsonld",
        )
        self.assertEqual(path.name, "schemaorg-current-http.jsonld")

    def test_file_never_writes_a_none_directory(self):
        self.releases.file()
        self.assertFalse((self.built / "None").exists())

    def test_file_is_what_get_ttl_files_reads_back(self):
        version, protocol, scope = "30.0", Protocol.HTTP, Scope.CURRENT
        _make_release(self.built, version)
        written = self.releases.file(version, protocol=protocol, scope=scope)
        read = self.releases.get_ttl_files(
            version, protocol=protocol, scope=scope
        )
        self.assertEqual([written], read)

    def test_file_drops_the_separator_for_empty_parts(self):
        path = self.releases.file(
            "30.0", protocol="", scope="shapes", extension=".shacl"
        )
        self.assertEqual(path.name, "schemaorg-shapes.shacl")

    def test_file_rejects_undeclared_version(self):
        with self.assertRaises(ValueError):
            self.releases.file("99.0")

    def test_file_does_not_declare_new_versions(self):
        with self.assertRaises(ValueError):
            self.releases.file("31.0")
        reread = Releases(self.input_layout, Version(self.versions_file))
        self.assertNotIn("31.0", [str(v) for v in reread.versions()])


class TestReleasesRealData(unittest.TestCase):
    """Checks Releases against the repository's declared releases."""

    def setUp(self):
        self.output_layout = OutputLayout(PROJECT_ROOT / schema.config.OUTPUTDIR)
        self.releases = Releases(self.output_layout, schema.VERSION)

    def test_versions_file_is_richly_populated(self):
        self.assertGreater(len(self.releases.versions()), 40)

    def test_current_is_declared(self):
        self.assertIn(self.releases.current(), self.releases.versions())

    def test_current_release_dir_is_computed_from_the_version(self):
        self.assertEqual(
            self.releases.dir(),
            self.output_layout.dir(Domain.RELEASE) / str(self.releases.current()),
        )

    def test_canonical_file_resolves_to_one_path(self):
        expected = self.releases.dir() / "schemaorg-all-https.ttl"
        if not expected.is_file():
            self.skipTest(f"site not built: no {expected}")

        self.assertEqual(self.releases.get_ttl_files(), [expected])


if __name__ == "__main__":
    unittest.main()
