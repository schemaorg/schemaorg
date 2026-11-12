from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from schemaorg.version import Version
import scripts.devserv as devserv


class TestDevservVersionRoutes(unittest.TestCase):
    def setUp(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.root = Path(temp_dir.name)
        self.site_dir = self.root / "site"
        (self.site_dir / "docs").mkdir(parents=True)
        (self.site_dir / "docs" / "fullrelease.html").write_text(
            "<html>fullrelease</html>", encoding="utf-8"
        )

        versions_path = self.root / "versions.json"
        versions_path.write_text(
            json.dumps(
                {
                    "schemaversion": "30.1",
                    "releaseLog": {
                        "30.1": "2026-09-16",
                        "15.0": "2022-10-25",
                    },
                }
            ),
            encoding="utf-8",
        )
        self.version = Version(versions_path)

        next_dir = self.root / "data" / "releases" / "next"
        next_dir.mkdir(parents=True)
        (next_dir / "schemaorg-all-https.ttl").write_text(
            "# next ttl\n", encoding="utf-8"
        )

        latest_dir = self.root / "data" / "releases" / "30.1"
        latest_dir.mkdir(parents=True)
        (latest_dir / "schemaorg-all-https.ttl").write_text(
            "# 30.1 ttl\n", encoding="utf-8"
        )

        legacy_dir = self.root / "data" / "releases" / "15.0"
        legacy_dir.mkdir(parents=True)
        (legacy_dir / "schema-all.html").write_text(
            "<html>legacy 15.0</html>", encoding="utf-8"
        )

        orig_static = devserv.app.static_folder
        devserv.app.static_folder = str(self.site_dir)
        self.addCleanup(setattr, devserv.app, "static_folder", orig_static)

        self.patches = (
            patch.object(devserv.constants, "PROJECT_ROOT", self.root),
            patch.object(devserv, "VERSION", self.version),
        )
        for p in self.patches:
            p.start()
            self.addCleanup(p.stop)

        self.client = devserv.app.test_client()

    def test_serves_next_release_directly_from_data_releases(self) -> None:
        with self.client.get("/version/next/schemaorg-all-https.ttl") as resp:
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.get_data(as_text=True), "# next ttl\n")

    def test_resolves_latest_to_published_release(self) -> None:
        with self.client.get("/version/latest/schemaorg-all-https.ttl") as resp:
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(resp.get_data(as_text=True), "# 30.1 ttl\n")

    def test_empty_path_falls_back_to_docs_fullrelease_when_no_schema_all(
        self,
    ) -> None:
        with self.client.get("/version/next") as resp:
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(
                resp.get_data(as_text=True), "<html>fullrelease</html>"
            )

    def test_empty_path_serves_historical_schema_all_when_present(self) -> None:
        with self.client.get("/version/15.0/") as resp:
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(
                resp.get_data(as_text=True), "<html>legacy 15.0</html>"
            )

    def test_undeclared_version_returns_404(self) -> None:
        with self.client.get("/version/99.9/schemaorg-all-https.ttl") as resp:
            self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
