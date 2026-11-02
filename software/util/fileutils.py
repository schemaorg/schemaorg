import enum

EXTENSIONS_FOR_FORMAT: dict[str, str] = {
    "xml": "xml",
    "rdf": "rdf",
    "nquads": "nq",
    "nt": "nt",
    "json-ld": "jsonld",
    "turtle": "ttl",
    "csv": "csv",
}


class FileSelector(enum.StrEnum):
    """Selector for schema release file sets."""

    ALL = "all"
    CURRENT = "current"


FILESET_SELECTORS: frozenset[str] = frozenset(FileSelector)
FILESET_PROTOCOLS: frozenset[str] = frozenset(("http", "https"))


def isAll(selector: str | FileSelector) -> bool:
    """Check if a selector string is a variation of the 'All' token."""
    return str(selector).lower() == FileSelector.ALL
