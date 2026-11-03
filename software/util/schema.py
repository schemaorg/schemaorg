"""Module that handles the schema.org version information and global constants."""

from __future__ import annotations

from schemaorg.constants import PROJECT_ROOT, VERSIONS_FILE
from schemaorg.version import Version


class constants:
    SITENAME: str = "Schema.org"
    DOCSDOCSDIR: str = "/docs"
    TERMDOCSDIR: str = DOCSDOCSDIR
    HANDLER_TEMPLATE: str = "handlers-template.yaml"
    HANDLER_FILE: str = "handlers.yaml"


class config:
    BUILDOPTS: list[str] = []
    TERMS: list[str] = []
    PAGES: list[str] = []
    FILES: list[str] = []
    OUTPUTDIR: str = "software/site"


def hasOpt(opt: str) -> bool:
    """Return true if `opt` is among the build options."""
    return opt in config.BUILDOPTS


VERSION = Version(PROJECT_ROOT / VERSIONS_FILE)
