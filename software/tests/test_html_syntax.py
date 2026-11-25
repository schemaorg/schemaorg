"""Structural HTML syntax regression checks for docs/ and templates/."""

from __future__ import annotations

from html.parser import HTMLParser
import re
import unittest

from schemaorg import constants
from util import copystaticdocsplusinsert

_VOID_TAGS: frozenset[str] = frozenset({
    "area",
    "base",
    "br",
    "col",
    "embed",
    "hr",
    "img",
    "input",
    "link",
    "meta",
    "param",
    "source",
    "track",
    "wbr",
})
_NO_SELF_NEST: frozenset[str] = frozenset({"p", "a"})
_JINJA_TAG_RE: re.Pattern[str] = re.compile(r"\{%.*?%\}", re.S)
_JINJA_EXPR_RE: re.Pattern[str] = re.compile(r"\{\{.*?\}\}", re.S)
_JINJA_COMMENT_RE: re.Pattern[str] = re.compile(r"\{#.*?#\}", re.S)


class _StrictHTMLAuditor(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.stack: list[tuple[str, int]] = []
        self.issues: list[str] = []
        self.head_count: int = 0
        self.body_count: int = 0
        self.stylesheets: list[tuple[str, int]] = []

    def _check_start(
        self,
        tag: str,
        attrs: list[tuple[str, str | None]],
        *,
        self_closing: bool,
    ) -> None:
        t = tag.lower()
        line = self.getpos()[0]
        raw = self.get_starttag_text() or ""
        if "<" in raw[1:]:
            self.issues.append(f"L{line}: unclosed start tag <{t}>")
        if t in _NO_SELF_NEST and any(s[0] == t for s in self.stack):
            prev = [s[1] for s in self.stack if s[0] == t][-1]
            self.issues.append(
                f"L{line}: nested <{t}> inside unclosed <{t}> from L{prev}"
            )
        if t == "head":
            self.head_count += 1
        elif t == "body":
            self.body_count += 1
        elif t == "link":
            attr_map = dict(attrs)
            href = attr_map.get("href")
            if attr_map.get("rel") == "stylesheet" and href:
                self.stylesheets.append((href, line))
        if t not in _VOID_TAGS and not self_closing:
            self.stack.append((t, line))

    def handle_starttag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self._check_start(tag, attrs, self_closing=False)

    def handle_startendtag(
        self, tag: str, attrs: list[tuple[str, str | None]]
    ) -> None:
        self._check_start(tag, attrs, self_closing=True)

    def handle_endtag(self, tag: str) -> None:
        t = tag.lower()
        line = self.getpos()[0]
        if t in _VOID_TAGS:
            self.issues.append(f"L{line}: stray closing tag </{t}>")
            return
        if not self.stack:
            self.issues.append(f"L{line}: unexpected closing tag </{t}>")
            return
        if self.stack[-1][0] == t:
            self.stack.pop()
            return
        names = [name for name, _ in self.stack]
        if t in names:
            idx = len(names) - 1 - names[::-1].index(t)
            unclosed = [(u, f"L{ln}") for u, ln in self.stack[idx + 1 :]]
            self.issues.append(
                f"L{line}: </{t}> closes past unclosed {unclosed}"
            )
            self.stack = self.stack[:idx]
        else:
            top_tag, top_line = self.stack[-1]
            self.issues.append(
                f"L{line}: mismatched </{t}> (top is <{top_tag}> at L{top_line})"
            )

    def finalize(self) -> list[str]:
        if self.head_count > 1:
            self.issues.append(f"duplicate <head> ({self.head_count}x)")
        if self.body_count > 1:
            self.issues.append(f"duplicate <body> ({self.body_count}x)")
        seen: dict[str, int] = {}
        for href, line in self.stylesheets:
            if href in seen:
                self.issues.append(
                    f"L{line}: duplicate stylesheet {href!r} (first at L{seen[href]})"
                )
            seen[href] = line
        for t, line in self.stack:
            self.issues.append(f"EOF: unclosed <{t}> opened at L{line}")
        return self.issues


def _audit_html(raw: str, *, strip_jinja: bool = False) -> list[str]:
    text = raw
    issues: list[str] = []
    if strip_jinja:
        text = _JINJA_COMMENT_RE.sub("", text)
        text = _JINJA_TAG_RE.sub("", text)
        text = _JINJA_EXPR_RE.sub("X", text)
        if re.search(r"<head\b", text, re.I) and "DocsHead.j2" in raw:
            issues.append("defines <head> and also includes DocsHead.j2")
    auditor = _StrictHTMLAuditor()
    auditor.feed(text)
    issues.extend(auditor.finalize())
    return issues


class TestHtmlSyntax(unittest.TestCase):
    def test_static_docs_have_valid_html_structure(self) -> None:
        docs_dir = constants.PROJECT_ROOT / "docs"
        failures: list[str] = []
        for path in sorted(docs_dir.glob("*.html")):
            if path.name == "full_md.html":
                continue
            issues = _audit_html(path.read_text(encoding="utf-8"))
            if issues:
                failures.append(f"{path.name}: {'; '.join(issues)}")
        self.assertEqual(failures, [])

    def test_templates_have_valid_html_structure(self) -> None:
        templates_dir = constants.PROJECT_ROOT / "templates"
        failures: list[str] = []
        for pattern in ("**/*.html", "**/*.j2"):
            for path in sorted(templates_dir.glob(pattern)):
                issues = _audit_html(
                    path.read_text(encoding="utf-8"),
                    strip_jinja=path.suffix == ".j2",
                )
                if issues:
                    rel = path.relative_to(templates_dir)
                    failures.append(f"{rel}: {'; '.join(issues)}")
        self.assertEqual(failures, [])

    def test_markdown_doc_wrapper_has_valid_html_structure(self) -> None:
        wrapped = (
            f"{copystaticdocsplusinsert._MD_DOC_BEGIN.format(title='Test')}"
            "<p>Body</p>"
            f"{copystaticdocsplusinsert._MD_DOC_END}"
        )
        self.assertEqual(_audit_html(wrapped), [])


if __name__ == "__main__":
    unittest.main()
