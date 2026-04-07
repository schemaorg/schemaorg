#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
from typing import List

SITENAME: str = "Schema.org"
BUILDOPTS: List[str] = []
TERMS: List[str] = []
PAGES: List[str] = []
FILES: List[str] = []
OUTPUTDIR: str = "software/site"
DOCSDOCSDIR: str = "/docs"
TERMDOCSDIR: str = "/docs"
HANDLER_TEMPLATE: str = "handlers-template.yaml"
HANDLER_FILE: str = "handlers.yaml"
RELEASE_DIR: str = "software/site/releases"
HOMEPAGE: str = "https://schema.org"


def hasOpt(opt: str) -> bool:
    """Return true if `opt` is among the build options"""
    return opt in BUILDOPTS


def getOutputDir() -> str:
    return OUTPUTDIR


def getDocsOutputDir() -> str:
    return str(Path(OUTPUTDIR) / "docs")
