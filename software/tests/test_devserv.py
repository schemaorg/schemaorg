from __future__ import annotations

import json
from pathlib import Path
import re
import tempfile
import unittest
from unittest.mock import patch

from schemaorg import constants as real_constants
from schemaorg.version import Version
import scripts.buildsite as buildsite
import scripts.devserv as devserv
import util.schema as schema


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


class TestHandlersTemplateRouting(unittest.TestCase):
    @staticmethod
    def _load_handlers(ver: str = "30.1") -> list[tuple[str, str]]:
        raw = (
            real_constants.PROJECT_ROOT / "software/gcloud/handlers-template.yaml"
        ).read_text(encoding="utf-8")
        rendered = raw.replace("{{ver}}", ver)
        handlers: list[tuple[str, str]] = []
        current_url: str | None = None
        for line in rendered.splitlines():
            stripped = line.strip()
            if stripped.startswith("- url:"):
                current_url = stripped.removeprefix("- url:").strip()
            elif current_url and stripped.startswith("static_files:"):
                target = stripped.removeprefix("static_files:").strip()
                handlers.append((current_url, target))
                current_url = None
            elif current_url and stripped.startswith("static_dir:"):
                current_url = None
        return handlers

    def _resolve(self, url_path: str, ver: str = "30.1") -> str | None:
        for pattern, static_files in self._load_handlers(ver=ver):
            m = re.match(f"^(?:{pattern})$", url_path)
            if m:
                out = static_files
                for idx, group in enumerate(m.groups(), start=1):
                    out = out.replace(f"\\{idx}", group)
                return out
        return None

    def test_version_routes_cover_owl_shapes_historical_and_next(self) -> None:
        self.assertEqual(
            self._resolve("/version/latest"), "docs/fullrelease.html"
        )
        self.assertEqual(
            self._resolve("/version/latest/schemaorg.owl"),
            "releases/30.1/schemaorg.owl",
        )
        self.assertEqual(
            self._resolve("/version/next/schemaorg.owl"),
            "releases/next/schemaorg.owl",
        )
        self.assertEqual(
            self._resolve("/version/next/schemaorg-shapes.shacl"),
            "releases/next/schemaorg-shapes.shacl",
        )
        self.assertEqual(
            self._resolve("/version/30.1/schemaorg-shapes.shexj"),
            "releases/30.1/schemaorg-shapes.shexj",
        )
        self.assertEqual(
            self._resolve("/version/15.0/"), "releases/15.0/schema-all.html"
        )
        self.assertEqual(
            self._resolve("/version/30.1"), "releases/30.1/schema-all.html"
        )
        self.assertEqual(
            self._resolve("/version/next"), "docs/fullrelease.html"
        )
        self.assertEqual(
            self._resolve("/version/next/"), "docs/fullrelease.html"
        )
        self.assertEqual(
            self._resolve("/version/31.0"), "docs/fullrelease.html"
        )

    def test_initdir_binds_latest_handler_to_published_version(self) -> None:
        orig_target = schema.config.TARGET_VERSION
        orig_output = schema.config.OUTPUTDIR
        self.addCleanup(setattr, schema.config, "TARGET_VERSION", orig_target)
        self.addCleanup(setattr, schema.config, "OUTPUTDIR", orig_output)

        with tempfile.TemporaryDirectory() as tmp:
            schema.config.TARGET_VERSION = "next"
            schema.config.OUTPUTDIR = tmp
            buildsite.args = buildsite.argparse.Namespace(
                clearfirst=False, autobuild=False
            )
            buildsite.initdir(tmp)

            rendered = (Path(tmp) / "gcloud/handlers.yaml").read_text(
                encoding="utf-8"
            )
            expected_ver = schema.VERSION.current().number()
            self.assertIn(f"releases/{expected_ver}/\\1", rendered)
            self.assertNotIn("releases/next/\\1", rendered)


if __name__ == "__main__":
    unittest.main()
