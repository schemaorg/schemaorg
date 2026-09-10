#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module that handles the schema.org version information and global constants."""

from pathlib import Path
from typing import List

from schemaorg.constants import PROJECT_ROOT
from schemaorg.version import Version


class constants:
    SITENAME: str = "Schema.org"
    DOCSDOCSDIR: str = "/docs"
    TERMDOCSDIR: str = "/docs"
    HANDLER_TEMPLATE: str = "handlers-template.yaml"
    HANDLER_FILE: str = "handlers.yaml"
    RELEASE_DIR: str = "software/site/releases"
    HOMEPAGE: str = "https://schema.org"


class config:
    BUILDOPTS: List[str] = []
    TERMS: List[str] = []
    PAGES: List[str] = []
    FILES: List[str] = []
    OUTPUTDIR: str = "software/site"


def hasOpt(opt: str) -> bool:
    """Return true if `opt` is among the build options"""
    return opt in config.BUILDOPTS


def getOutputDir() -> str:
    return config.OUTPUTDIR


def getDocsOutputDir() -> str:
    return str(Path(config.OUTPUTDIR) / "docs")


VERSION = Version(PROJECT_ROOT / "versions.json")
