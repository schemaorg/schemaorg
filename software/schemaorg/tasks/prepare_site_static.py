"""Floating task that prepares static docs, inserts, and GCloud handlers."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path
import random
import re
import shutil

import markdown2  # type: ignore[import-untyped]

from schemaorg import constants
from schemaorg.layout import Domain, InputLayout, OutputLayout
from schemaorg.progress import ProgressReporter
from schemaorg.version import VersionItem

_HANDLER_TEMPLATE: str = "handlers-template.yaml"
_HANDLER_FILE: str = "handlers.yaml"

_STATIC_INSERT_MARKER_RE: re.Pattern[str] = re.compile(
    r"<!-- #### Static Doc Insert", re.IGNORECASE
)
_EMPTY_DATE_SEP_RE: re.Pattern[str] = re.compile(
    r'\s*<span class="sep">\|</span>\s*\{\{versiondate\}\}'
)

_MD_DOC_BEGIN: str = """<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>{title} - {sitename}</title>

<!-- #### Static Doc Insert Head goes here -->
</head><body>
<!-- #### Static Doc Insert PageHead goes here -->
<div id="mainContent" class="faq">"""

_MD_DOC_END: str = (
    """</div>\n<!-- #### Static Doc Insert Footer goes here -->\n</body>\n</html>"""
)


def _load_static_inserts(
    input_layout: InputLayout, target_version: VersionItem
) -> Iterator[tuple[re.Pattern[str], str]]:
    inserts_dir = input_layout.dir(Domain.STATIC_DOC_INSERTS)
    version_num = target_version.number()
    version_date = target_version.date()
    docs_dir = f"/{Domain.DOCS}"

    for f_path in inserts_dir.glob("*.html"):
        sub = re.escape(f_path.stem.lower().removeprefix("sdi-"))
        pattern = re.compile(
            rf"<!-- #### Static Doc Insert {sub} .* -->", re.IGNORECASE
        )
        raw = f_path.read_text(encoding="utf-8")
        if version_date is None:
            raw = _EMPTY_DATE_SEP_RE.sub("", raw)
        indata = (
            raw.replace("{{version}}", version_num)
            .replace("{{versiondate}}", version_date or "")
            .replace("{{docsdir}}", docs_dir)
        )
        yield pattern, indata


def _convert_md_docs(doc_dir: Path) -> None:
    for md_path in doc_dir.glob("*.md"):
        text = md_path.read_text(encoding="utf-8")
        rng_state = random.getstate()
        try:
            # Deterministic markdown2 email obfuscation across releases.
            random.seed(42)
            md_html = str(markdown2.markdown(text))
        finally:
            random.setstate(rng_state)

        header = _MD_DOC_BEGIN.format(
            title=md_path.stem.title(),
            sitename=constants.SITENAME,
        )
        output_path = doc_dir / f"{md_path.stem}.html"
        output_path.write_text(
            f"{header}{md_html}{_MD_DOC_END}",
            encoding="utf-8",
        )
        md_path.unlink()


class PrepareSiteStaticTask:
    """Clears site dir if requested, copies static docs, and renders GCloud config."""

    def __init__(
        self,
        input_layout: InputLayout,
        output_layout: OutputLayout,
        target_version: VersionItem,
        current_version: VersionItem,
        clear_first: bool,
        progress: ProgressReporter,
    ) -> None:
        self.input_layout: InputLayout = input_layout
        self.output_layout: OutputLayout = output_layout
        self.target_version: VersionItem = target_version
        self.current_version: VersionItem = current_version
        self.clear_first: bool = clear_first
        self.progress: ProgressReporter = progress

    def _clear_output_dir(self) -> None:
        out_dir = self.output_layout.output_dir
        if not out_dir.is_dir():
            return
        for item in out_dir.iterdir():
            if item.name == ".gitkeep":
                continue
            if item.is_dir():
                shutil.rmtree(item)
            else:
                item.unlink()

    def run(self) -> None:
        total_steps = 5 if self.clear_first else 4
        with self.progress.task(
            "Preparing static site files",
            total=total_steps,
            unit="steps",
        ) as p:
            if self.clear_first:
                p.step("clearing output directory")
                self._clear_output_dir()
                p.advance(1)

            self.output_layout.dir(Domain.EMPTY)

            p.step("copying static docs")
            docs_dest = self.output_layout.dir(Domain.DOCS)
            shutil.copytree(
                self.input_layout.dir(Domain.DOCS),
                docs_dest,
                dirs_exist_ok=True,
            )
            _convert_md_docs(docs_dest)
            p.advance(1)

            p.step("applying static doc inserts")
            inserts = list(
                _load_static_inserts(self.input_layout, self.target_version)
            )
            for doc_path in sorted(docs_dest.glob("*.html")):
                data = doc_path.read_text(encoding="utf-8")
                if _STATIC_INSERT_MARKER_RE.search(data):
                    for pattern, insert_content in inserts:
                        data = pattern.sub(insert_content, data)
                    doc_path.write_text(data, encoding="utf-8")
            p.advance(1)

            p.step("copying GCloud configs")
            gcloud_dest = self.output_layout.dir(Domain.GCLOUD)
            for path in self.input_layout.files(Domain.GCLOUD, "*.yaml"):
                shutil.copy(path, gcloud_dest)
            p.advance(1)

            p.step(f"rendering {_HANDLER_FILE}")
            template_file = self.input_layout.file(
                Domain.GCLOUD, _HANDLER_TEMPLATE
            )
            handler_data = template_file.read_text(encoding="utf-8").replace(
                "{{ver}}", self.current_version.number()
            )
            self.output_layout.file(Domain.GCLOUD, _HANDLER_FILE).write_text(
                handler_data, encoding="utf-8"
            )
            p.advance(1)
