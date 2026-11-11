from __future__ import annotations

from collections.abc import Iterable
import re
import threading

import markdown2

_WIKILINK_RE: re.Pattern[str] = re.compile(r"\[\[([\w0-9_ -]+)\]\]")


class MarkdownTool:
    WCLASS: str = "localLink"
    WPRE: str = "/"
    WPOST: str = ""

    def __init__(self) -> None:
        self._md: markdown2.Markdown = markdown2.Markdown()
        self._parselock: threading.Lock = threading.Lock()

    def parse(
        self, source: str, preservePara: bool = False, wpre: str | None = None
    ) -> str:
        source = source.strip()
        if not source:
            return ""

        source = source.replace("\\n", "\n")
        with self._parselock:
            ret: str = str(self._md.convert(source))

        if not preservePara:
            if len(ret) > 7 and ret.startswith("<p>") and ret.endswith("</p>\n"):
                ret = ret.removeprefix("<p>").removesuffix("</p>\n")

            ret = ret.replace("<p>", "").replace("</p>", "<br/><br/>")
            ret = ret.removesuffix("<br/><br/>")

        return self.parseWiklinks(ret, wpre=wpre)

    def parseLines(self, lines: Iterable[str]) -> str:
        return self.parse("".join(lines))

    def parseWiklinks(self, source: str, wpre: str | None = None) -> str:
        prefix = self.WPRE if wpre is None else wpre
        return _WIKILINK_RE.sub(
            lambda m: (
                f'<a class="{self.WCLASS}" href="{prefix}{m.group(1)}{self.WPOST}">'
                f"{m.group(1)}</a>"
            ),
            source,
        )

    @classmethod
    def setWikilinkCssClass(cls, c: str) -> None:
        cls.WCLASS = c

    @classmethod
    def setWikilinkPrePath(cls, p: str) -> None:
        cls.WPRE = p

    @classmethod
    def setWikilinkPostPath(cls, p: str) -> None:
        cls.WPOST = p


Markdown: MarkdownTool = MarkdownTool()
