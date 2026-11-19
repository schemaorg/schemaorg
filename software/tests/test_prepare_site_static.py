from __future__ import annotations

import logging
from pathlib import Path
import tempfile
import unittest

from schemaorg.layout import Domain, InputLayout, OutputLayout
from schemaorg.progress import LogProgressReporter
from schemaorg.tasks.prepare_site_static import PrepareSiteStaticTask
from schemaorg.version import VersionItem


class TestPrepareSiteStaticTask(unittest.TestCase):
    def setUp(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.root = Path(temp_dir.name)
        self.in_dir = self.root / "in"
        self.out_dir = self.root / "site"

        docs_in = self.in_dir / Domain.DOCS.value
        docs_in.mkdir(parents=True)
        (docs_in / "guide.md").write_text("# Hello\nWorld\n", encoding="utf-8")

        inserts_in = self.in_dir / Domain.STATIC_DOC_INSERTS.value
        inserts_in.mkdir(parents=True)
        (inserts_in / "sdi-footer.html").write_text(
            '<footer>V{{version}} <span class="sep">|</span> {{versiondate}} {{docsdir}}</footer>',
            encoding="utf-8",
        )
        (inserts_in / "sdi-head.html").write_text("", encoding="utf-8")
        (inserts_in / "sdi-pagehead.html").write_text("", encoding="utf-8")

        gcloud_in = self.in_dir / Domain.GCLOUD.value
        gcloud_in.mkdir(parents=True)
        (gcloud_in / "handlers-template.yaml").write_text(
            "releases/{{ver}}/\\1\n", encoding="utf-8"
        )

    def test_clears_preserves_gitkeep_converts_md_and_renders_handlers(
        self,
    ) -> None:
        self.out_dir.mkdir(parents=True)
        gitkeep = self.out_dir / ".gitkeep"
        gitkeep.write_text("", encoding="utf-8")
        stale = self.out_dir / "stale.html"
        stale.write_text("old", encoding="utf-8")

        logger = logging.getLogger("test.prepare_static")
        reporter = LogProgressReporter(logger=logger, log_steps=True)
        out_layout = OutputLayout(self.out_dir)

        with self.assertLogs(logger, level=logging.INFO) as captured:
            PrepareSiteStaticTask(
                input_layout=InputLayout(self.in_dir),
                output_layout=out_layout,
                target_version=VersionItem("next"),
                current_version=VersionItem("30.1", "2026-09-16"),
                clear_first=True,
                progress=reporter,
            ).run()

        self.assertTrue(gitkeep.is_file())
        self.assertFalse(stale.exists())
        guide_html = out_layout.file(Domain.DOCS, "guide.html").read_text(
            encoding="utf-8"
        )
        self.assertIn("<h1>Hello</h1>", guide_html)
        self.assertIn("<footer>Vnext /docs</footer>", guide_html)
        self.assertNotIn("2026-09-16", guide_html)

        handlers = out_layout.file(Domain.GCLOUD, "handlers.yaml").read_text(
            encoding="utf-8"
        )
        self.assertEqual(handlers, "releases/30.1/\\1\n")
        self.assertIn("(5/5 steps)", "\n".join(captured.output))


if __name__ == "__main__":
    unittest.main()
