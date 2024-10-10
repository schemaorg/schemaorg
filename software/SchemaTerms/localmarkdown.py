#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import logging
import markdown2
import re
import threading


WIKILINKPATTERN = r"\[\[([\w0-9_ -]+)\]\]"

log = logging.getLogger(__name__)


class MarkdownTool(object):
    WCLASS = "localLink"
    WPRE = "/"
    WPOST = ""

    def __init__(self):
        # from markdown.extensions.wikilinks import WikiLinkExtension
        # self._md = markdown2.Markdown(extensions=[WikiLinkExtension(base_url='/', end_url='', html_class='localLink')])
        self._md = markdown2.Markdown()
        self._parselock = threading.Lock()

    def setPre(self, pre="./"):
        self.wpre = pre

    def setPost(self, post=""):
        self.wpost = post

    def parse(self, source, preservePara=False, wpre=None):
        source = source.strip()
        if not source:
            return ""

        source = source.replace("\\n", "\n")
        with self._parselock:
            ret = self._md.convert(source)

        if not preservePara:
            # Remove wrapping <p> </p>\n that Markdown2 adds by default
            if len(ret) > 7 and ret.startswith("<p>") and ret.endswith("</p>\n"):
                ret = ret[3 : len(ret) - 5]

            ret = ret.replace("<p>", "")
            ret = ret.replace("</p>", "<br/><br/>")
            if ret.endswith("<br/><br/>"):
                ret = ret[: len(ret) - 10]

        return self.parseWiklinks(ret, wpre=wpre)

    def parseLines(self, lines):
        return self.parse(''.join(lines))

    def parseWiklinks(self, source, wpre=None):
        self.wpre = wpre
        return re.sub(WIKILINKPATTERN, self.wikilinksReplace, source)

    def wikilinksReplace(self, match):
        wpre = self.wpre
        t = match.group(1)
        return '<a class="%s" href="%s%s%s">%s</a>' % (
            MarkdownTool.WCLASS,
            MarkdownTool.WPRE,
            t,
            MarkdownTool.WPOST,
            t,
        )

    @classmethod
    def setWikilinkCssClass(cls, c):
        cls.WCLASS = c

    @classmethod
    def setWikilinkPrePath(cls, p):
        MarkdownTool.WPRE = p

    @classmethod
    def setWikilinkPostPath(cls, p):
        cls.WPOST = p


Markdown = MarkdownTool()
