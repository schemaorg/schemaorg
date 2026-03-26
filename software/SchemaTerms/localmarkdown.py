#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import logging
import markdown2
import re
import threading
import typing
from typing import Any, Dict, List, Optional, Tuple, Union, Iterable, Sequence


WIKILINKPATTERN: str = r"\[\[([\w0-9_ -]+)\]\]"

log: logging.Logger = logging.getLogger(__name__)


class MarkdownTool(object):
    WCLASS: str = "localLink"
    WPRE: str = "/"
    WPOST: str = ""

    def __init__(self) -> None:
        # from markdown.extensions.wikilinks import WikiLinkExtension
        # self._md = markdown2.Markdown(extensions=[WikiLinkExtension(base_url='/', end_url='', html_class='localLink')])
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
            ret: str = self._md.convert(source)

        if not preservePara:
            # Remove wrapping <p> </p>\n that Markdown2 adds by default
            if len(ret) > 7 and ret.startswith("<p>") and ret.endswith("</p>\n"):
                ret = ret[3 : len(ret) - 5]

            ret = ret.replace("<p>", "")
            ret = ret.replace("</p>", "<br/><br/>")
            if ret.endswith("<br/><br/>"):
                ret = ret[: len(ret) - 10]

        return self.parseWiklinks(ret, wpre=wpre)

    def parseLines(self, lines: Iterable[str]) -> str:
        return self.parse("".join(lines))

    def parseWiklinks(self, source: str, wpre: Optional[str] = None) -> str:
        self.wpre = wpre
        return re.sub(WIKILINKPATTERN, self.wikilinksReplace, source)

    def wikilinksReplace(self, match: re.Match) -> str:
        # wpre = self.wpre # Assigned but unused in original code
        t: str = match.group(1)
        return '<a class="%s" href="%s%s%s">%s</a>' % (
            MarkdownTool.WCLASS,
            MarkdownTool.WPRE,
            t,
            MarkdownTool.WPOST,
            t,
        )

    @classmethod
    def setWikilinkCssClass(cls, c: str) -> None:
        cls.WCLASS = c

    @classmethod
    def setWikilinkPrePath(cls, p: str) -> None:
        MarkdownTool.WPRE = p

    @classmethod
    def setWikilinkPostPath(cls, p: str) -> None:
        cls.WPOST = p


Markdown: MarkdownTool = MarkdownTool()
