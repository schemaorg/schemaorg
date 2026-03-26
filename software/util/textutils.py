#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import typing
from typing import Any, Dict, List, Optional, Tuple, Union, Iterable, Sequence, Set, Callable


def StripHtmlTags(source: str) -> str:
    """Strip all HTML tags from source."""
    if source and len(source) > 0:
        return re.sub("<[^<]+?>", "", source)
    return ""


def ShortenOnSentence(source: str, lengthHint: int = 250) -> str:
    """Shorten source at a sentence boundary.

    Args:
      source: input text to shorten.
      lengthHint: length at which the input should be shortened.
    Returns:
      shortened text
    """
    if source and len(source) > lengthHint:
        source = source.strip()
        sentEnd: re.Pattern = re.compile("[.!?]")
        sentList: List[str] = sentEnd.split(source)
        com: str = ""
        count: int = 0
        while count < len(sentList):
            if count > 0:
                if len(com) < len(source):
                    com += source[len(com)]
            com += sentList[count]
            count += 1
            if count == len(sentList):
                if len(com) < len(source):
                    com += source[len(source) - 1]
            if len(com) > lengthHint:
                if len(com) < len(source):
                    com += source[len(com)]
                break

        if len(source) > len(com) + 1:
            com += ".."
        source = com
    return source
