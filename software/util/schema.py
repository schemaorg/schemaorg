"""Module that handles the schema.org version information and global constants."""

from __future__ import annotations

from schemaorg.constants import PROJECT_ROOT, VERSIONS_FILE
from schemaorg.version import NEXT_VERSION, Version, VersionItem


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
    TARGET_VERSION: str = NEXT_VERSION


def hasOpt(opt: str) -> bool:
    """Return true if `opt` is among the build options."""
    return opt in config.BUILDOPTS


VERSION = Version(PROJECT_ROOT / VERSIONS_FILE)


def target_version() -> VersionItem:
    """Return the active target VersionItem resolved from config.TARGET_VERSION."""
    return VERSION.resolve(config.TARGET_VERSION)
