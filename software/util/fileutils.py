from __future__ import annotations


def isAll(selector: str) -> bool:
    """Check if a selector string is a variation of the 'All' token."""
    return str(selector).lower() == "all"
