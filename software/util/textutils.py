#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Iterable, Match, Optional, Sequence
import os
import re
import sys

import software


def StripHtmlTags(source: str) -> str:
    """Strip all HTML tags from source."""
    return re.sub(r"<[^<]+?>", "", source) if source else ""


def ShortenOnSentence(source: str, lengthHint: int = 250) -> str:
    """Shorten source at a sentence boundary near the lengthHint."""
    if not source or len(source) <= lengthHint:
        return source or ""

    source: str = source.strip()
    pattern: re.Pattern = re.compile(r"[.!?](\s|$)")

    match: Match[str]
    for match in pattern.finditer(source):
        end_pos: int = match.start() + 1
        if end_pos > lengthHint:
            return source[:end_pos] + ".."

    return source[:lengthHint] + ".."


def Array2String(values: Optional[Sequence[str]]) -> str:
    """Convert a sequence of strings into a single comma-separated string."""
    return ", ".join(values) if values else ""
