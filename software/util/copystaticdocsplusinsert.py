"""Tool that handles Markdown conversion and HTML includes in static doc pages."""

from collections.abc import Iterator
import logging
from pathlib import Path
import random
import re
import shutil

import markdown2

import util.paths as paths
import util.schema as schema

log: logging.Logger = logging.getLogger(__name__)

_STATIC_INSERT_MARKER_RE: re.Pattern[str] = re.compile(
    r"<!-- #### Static Doc Insert", re.IGNORECASE
)

_MD_DOC_BEGIN: str = """<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xml:lang="en" lang="en">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<title>{title} - Schema.org</title>

<!-- #### Static Doc Insert Head goes here -->
</head><body>
<!-- #### Static Doc Insert PageHead goes here -->
<div id="mainContent" class="faq">"""

_MD_DOC_END: str = """</div>\n<!-- #### Static Doc Insert Footer goes here -->\n </html>"""


def _getInserts() -> Iterator[tuple[re.Pattern[str], str]]:
    template_dir: Path = paths.DefaultInputLayout().dir(paths.Domain.STATIC_DOC_INSERTS)
    version = schema.VERSION.current()
    version_num = version.number()
    version_date = str(version.date() or "")
    for f_path in template_dir.glob("*.html"):
        sub = re.escape(f_path.stem.lower().removeprefix("sdi-"))
        pattern = re.compile(
            rf"<!-- #### Static Doc Insert {sub} .* -->", re.IGNORECASE
        )
        indata = (
            f_path.read_text(encoding="utf-8")
            .replace("{{version}}", version_num)
            .replace("{{versiondate}}", version_date)
            .replace("{{docsdir}}", "/docs")
        )
        yield pattern, indata


def _convert_md_docs(doc_dir: Path) -> None:
    """Convert all Markdown files in doc_dir to HTML in place and remove the .md copies."""
    for md_path in doc_dir.glob("*.md"):
        text = md_path.read_text(encoding="utf-8")
        rng_state = random.getstate()
        try:
            # Deterministic markdown2 email obfuscation across releases.
            random.seed(42)
            md_html = str(markdown2.markdown(text))
        finally:
            random.setstate(rng_state)

        output_path = doc_dir / f"{md_path.stem}.html"
        output_path.write_text(
            f"{_MD_DOC_BEGIN.format(title=md_path.stem.title())}{md_html}{_MD_DOC_END}",
            encoding="utf-8",
        )
        md_path.unlink()


def htmlinserts(destdir: str | Path) -> None:
    """Perform static header/footer substitutions on all HTML files in destdir."""
    log.info("Adding header/footer templates to all html files")
    dest_path = Path(destdir)
    docs = sorted(dest_path.glob("*.html"))
    inserts = list(_getInserts())
    for doc_path in docs:
        data = doc_path.read_text(encoding="utf-8")
        if _STATIC_INSERT_MARKER_RE.search(data):
            for pattern, insert_content in inserts:
                data = pattern.sub(insert_content, data)
            doc_path.write_text(data, encoding="utf-8")
    log.info("Added to %d files", len(docs))


def copyFiles(srcdir: str | Path, destdir: str | Path) -> None:
    """Copy and complete all the static document pages."""
    dest_path = Path(destdir)
    shutil.copytree(srcdir, dest_path, dirs_exist_ok=True)
    log.info("Converting .md docs to html")
    _convert_md_docs(dest_path)
    htmlinserts(dest_path)
    log.info("Done")


if __name__ == "__main__":
    copyFiles("./docs", "./software/site/docs")
