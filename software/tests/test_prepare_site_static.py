from __future__ import annotations

import logging
from pathlib import Path
import tempfile
import unittest

from schemaorg.layout import Domain, InputLayout, OutputLayout
from schemaorg.progress import LogProgressReporter, NullProgressReporter
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
        (docs_in / "page.html").write_text(
            "<!-- #### Static Doc Insert Head goes here --><p>Hi</p>",
            encoding="utf-8",
        )

        inserts_in = self.in_dir / Domain.STATIC_DOC_INSERTS.value
        inserts_in.mkdir(parents=True)
        (inserts_in / "sdi-footer.html").write_text(
            '<footer>V{{version}} <span class="sep">|</span> {{versiondate}} {{docsdir}}</footer>',
            encoding="utf-8",
        )
        # Backslash in insert verifies regex-escape safety in pattern.sub().
        (inserts_in / "sdi-head.html").write_text(
            r"<script>const re = /\d+/; const s = '\n';</script>",
            encoding="utf-8",
        )
        (inserts_in / "sdi-pagehead.html").write_text("", encoding="utf-8")

        gcloud_in = self.in_dir / Domain.GCLOUD.value
        gcloud_in.mkdir(parents=True)
        (gcloud_in / "app.yaml").write_text("runtime: python311\n", encoding="utf-8")
        (gcloud_in / "handlers-template.yaml").write_text(
            "releases/{{ver}}/\\1\n", encoding="utf-8"
        )

    def test_clears_preserves_gitkeep_handles_dir_symlink_and_inserts(
        self,
    ) -> None:
        self.out_dir.mkdir(parents=True)
        gitkeep = self.out_dir / ".gitkeep"
        gitkeep.write_text("", encoding="utf-8")
        stale = self.out_dir / "stale.html"
        stale.write_text("old", encoding="utf-8")
        stale_dir = self.out_dir / "old_sub"
        stale_dir.mkdir()
        (stale_dir / "x.txt").write_text("x", encoding="utf-8")
        ext_target = self.root / "external_dir"
        ext_target.mkdir()
        (ext_target / "keep.txt").write_text("precious", encoding="utf-8")
        dir_link = self.out_dir / "linked_dir"
        dir_link.symlink_to(ext_target)

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
        self.assertFalse(stale_dir.exists())
        self.assertFalse(dir_link.exists())
        self.assertTrue((ext_target / "keep.txt").is_file())

        guide_html = out_layout.file(Domain.DOCS, "guide.html").read_text(
            encoding="utf-8"
        )
        self.assertIn("<h1>Hello</h1>", guide_html)
        self.assertIn("<footer>Vnext /docs</footer>", guide_html)
        self.assertNotIn("2026-09-16", guide_html)
        self.assertIn(r"const re = /\d+/; const s = '\n';", guide_html)

        page_html = out_layout.file(Domain.DOCS, "page.html").read_text(
            encoding="utf-8"
        )
        self.assertIn(r"const re = /\d+/;", page_html)

        self.assertTrue(out_layout.file(Domain.GCLOUD, "app.yaml").is_file())
        handlers = out_layout.file(Domain.GCLOUD, "handlers.yaml").read_text(
            encoding="utf-8"
        )
        self.assertEqual(handlers, "releases/30.1/\\1\n")
        self.assertIn("(5/5 steps)", "\n".join(captured.output))

    def test_dated_version_retains_date_and_clear_first_false_preserves_files(
        self,
    ) -> None:
        self.out_dir.mkdir(parents=True)
        keep_me = self.out_dir / "keep.txt"
        keep_me.write_text("stay", encoding="utf-8")
        out_layout = OutputLayout(self.out_dir)
        PrepareSiteStaticTask(
            input_layout=InputLayout(self.in_dir),
            output_layout=out_layout,
            target_version=VersionItem("30.1", "2026-09-16"),
            current_version=VersionItem("30.1", "2026-09-16"),
            clear_first=False,
            progress=NullProgressReporter(),
        ).run()
        self.assertTrue(keep_me.is_file())
        guide_html = out_layout.file(Domain.DOCS, "guide.html").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            '<footer>V30.1 <span class="sep">|</span> 2026-09-16 /docs</footer>',
            guide_html,
        )

    def test_refuses_clearing_dir_containing_input_root_and_rejects_missing_inserts(
        self,
    ) -> None:
        with self.assertRaises(ValueError):
            PrepareSiteStaticTask(
                input_layout=InputLayout(self.in_dir),
                output_layout=OutputLayout(self.root),
                target_version=VersionItem("next"),
                current_version=VersionItem("30.1", "2026-09-16"),
                clear_first=True,
                progress=NullProgressReporter(),
            ).run()
        self.assertTrue(self.in_dir.is_dir())

        for f in (self.in_dir / Domain.STATIC_DOC_INSERTS.value).glob("*.html"):
            f.unlink()
        with self.assertRaises(FileNotFoundError):
            PrepareSiteStaticTask(
                input_layout=InputLayout(self.in_dir),
                output_layout=OutputLayout(self.out_dir),
                target_version=VersionItem("next"),
                current_version=VersionItem("30.1", "2026-09-16"),
                clear_first=False,
                progress=NullProgressReporter(),
            ).run()


if __name__ == "__main__":
    unittest.main()
