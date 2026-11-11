from __future__ import annotations

import re

_HTML_TAG_RE: re.Pattern[str] = re.compile(r"<[^<]+?>")
_SENTENCE_END_RE: re.Pattern[str] = re.compile(r"[.!?](\s|$)")


def StripHtmlTags(source: str) -> str:
    """Strip all HTML tags from source."""
    return _HTML_TAG_RE.sub("", source) if source else ""


def ShortenOnSentence(source: str, lengthHint: int = 250) -> str:
    """Shorten source at a sentence boundary near the lengthHint."""
    if not source:
        return ""
    source = source.strip()
    if len(source) <= lengthHint:
        return source

    for match in _SENTENCE_END_RE.finditer(source):
        end_pos = match.start() + 1
        if end_pos > lengthHint:
            return f"{source[:end_pos]}.."

    return f"{source[:lengthHint]}.."
