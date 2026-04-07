#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from typing import Optional, Match, Iterable

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
