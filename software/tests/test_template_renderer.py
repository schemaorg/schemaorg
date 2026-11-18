from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from schemaorg.layout import Domain, InputLayout
from schemaorg.template_renderer import TemplateRenderer
from schemaorg.version import VersionItem


class TestTemplateRenderer(unittest.TestCase):
    def setUp(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.layout = InputLayout(Path(temp_dir.name))
        self.templates_dir = self.layout.dir(Domain.TEMPLATES)
        self.templates_dir.mkdir(parents=True)

    def _write_template(self, rel_path: str, content: str) -> Path:
        path = self.templates_dir / rel_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    def test_renders_release_version_and_site_defaults(self) -> None:
        self._write_template(
            "page.j2",
            "{{ sitename }}|V{{ version }}|{{ versiondate }}|"
            "{{ docsdir }}|{{ TERMHREFPREFIX }}Thing{{ TERMHREFSUFFIX }}",
        )
        renderer = TemplateRenderer(
            self.layout,
            VersionItem("30.1", "2026-09-16"),
            (),
        )
        self.assertEqual(
            renderer.render("page.j2", {}),
            "Schema.org|V30.1|2026-09-16|/docs|/Thing",
        )

    def test_next_version_renders_empty_versiondate(self) -> None:
        self._write_template("ver.j2", "V{{ version }}[{{ versiondate }}]")
        renderer = TemplateRenderer(self.layout, VersionItem("next"), ())
        self.assertEqual(renderer.render("ver.j2", {}), "Vnext[]")

    def test_autoescapes_and_merges_extra_vars_and_build_opts(self) -> None:
        self._write_template(
            "opts.j2",
            "{{ title }}|{% if 'goto' in BUILDOPTS %}GOTO{% endif %}",
        )
        renderer = TemplateRenderer(
            self.layout,
            VersionItem("next"),
            ("goto",),
        )
        compiled = renderer.get_template("opts.j2")
        self.assertEqual(
            renderer.render(compiled, {"title": "A & B"}),
            "A &amp; B|GOTO",
        )

    def test_local_vars_do_not_leak_between_renders(self) -> None:
        self._write_template(
            "vars.j2",
            "{% if flag %}{{ set_local_var(local_vars, 'seen', True) }}{% endif %}"
            "{{ local_vars.get('seen', False) }}",
        )
        renderer = TemplateRenderer(self.layout, VersionItem("next"), ())
        self.assertEqual(renderer.render("vars.j2", {"flag": True}), "True")
        self.assertEqual(renderer.render("vars.j2", {"flag": False}), "False")


if __name__ == "__main__":
    unittest.main()
