from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from schemaorg.layout import Domain, OutputLayout


class TestOutputLayout(unittest.TestCase):
    def setUp(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.output_root = Path(temp_dir.name) / "site"
        self.layout = OutputLayout(self.output_root)

    def test_dir_standard(self) -> None:
        docs_dir = self.layout.dir(Domain.DOCS)
        self.assertTrue(docs_dir.is_dir())
        self.assertEqual(docs_dir, self.output_root / "docs")

    def test_dir_gcloud(self) -> None:
        gcloud_dir = self.layout.dir(Domain.GCLOUD)
        self.assertTrue(gcloud_dir.is_dir())
        self.assertEqual(gcloud_dir, self.output_root / "gcloud")

    def test_dir_release_is_version_agnostic(self) -> None:
        release_dir = self.layout.dir(Domain.RELEASE)
        self.assertTrue(release_dir.is_dir())
        self.assertEqual(release_dir, self.output_root / "releases")

    def test_file(self) -> None:
        f = self.layout.file(Domain.DOCS_COLLAB, "w3c.html")
        self.assertTrue(f.parent.is_dir())
        self.assertEqual(f, self.output_root / "docs" / "collab" / "w3c.html")


if __name__ == "__main__":
    unittest.main()
