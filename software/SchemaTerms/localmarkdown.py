#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import logging
import markdown2
import re
import threading
from typing import Optional, Iterable

WIKILINKPATTERN: str = r"\[\[([\w0-9_ -]+)\]\]"

log: logging.Logger = logging.getLogger(__name__)


class MarkdownTool:
    WCLASS: str = "localLink"
    WPRE: str = "/"
    WPOST: str = ""

    def __init__(self) -> None:
        self._md: markdown2.Markdown = markdown2.Markdown()
        self._parselock: threading.Lock = threading.Lock()
        self.wpre: Optional[str] = None
        self.wpost: Optional[str] = None

    def setPre(self, pre: str = "./") -> None:
        self.wpre = pre

    def setPost(self, post: str = "") -> None:
        self.wpost = post

    def parse(self, source: str, preservePara: bool = False, wpre: Optional[str] = None) -> str:
        source = source.strip()
        if not source:
            return ""

        source = source.replace("\\n", "\n")
        with self._parselock:
            ret: str = str(self._md.convert(source))

        if not preservePara:
            if len(ret) > 7 and ret.startswith("<p>") and ret.endswith("</p>\n"):
                ret = ret[3:-5]

            ret = ret.replace("<p>", "").replace("</p>", "<br/><br/>")
            if ret.endswith("<br/><br/>"):
                ret = ret[:-10]

        return self.parseWiklinks(ret, wpre=wpre)

    def parseLines(self, lines: Iterable[str]) -> str:
        return self.parse("".join(lines))

    def parseWiklinks(self, source: str, wpre: Optional[str] = None) -> str:
        self.wpre = wpre
        return re.sub(WIKILINKPATTERN, self.wikilinksReplace, source)

    def wikilinksReplace(self, match: re.Match) -> str:
        t: str = match.group(1)
        return f'<a class="{self.WCLASS}" href="{self.WPRE}{t}{self.WPOST}">{t}</a>'

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
