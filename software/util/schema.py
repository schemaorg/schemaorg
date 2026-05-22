#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module that handles the schema.org version information and global constants."""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import software

import util.paths as paths
from util.sort_dict import sort_dict


class constants:
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
    return opt in constants.BUILDOPTS


def getOutputDir() -> str:
    return constants.OUTPUTDIR


def getDocsOutputDir() -> str:
    return str(Path(constants.OUTPUTDIR) / "docs")


VERSION_DATA: Optional[Dict[str, Any]] = None


def getVersionData() -> Dict[str, Any]:
    global VERSION_DATA
    if VERSION_DATA is None:
        VERSION_DATA = json.loads(
            paths.DefaultInputLayout()
            .domain_file(paths.Domain.ROOT, "versions.json")
            .read_text()
        )
    assert VERSION_DATA is not None
    return VERSION_DATA


def getVersion() -> str:
    return str(getVersionData()["schemaversion"])


def getVersionDate(ver: str) -> Optional[str]:
    ret: Optional[str] = getVersionData()["releaseLog"].get(ver)
    return ret


def getCurrentVersionDate() -> Optional[str]:
    return getVersionDate(getVersion())


def setVersion(ver: str, date: str) -> None:
    versiondata: Dict[str, Any] = getVersionData()
    versiondata["schemaversion"] = ver
    versiondata["releaseLog"][ver] = date

    logs: Dict[str, str] = versiondata["releaseLog"]
    versiondata["releaseLog"] = dict(
        sorted(logs.items(), key=lambda x: float(x[0]), reverse=True)
    )

    paths.DefaultInputLayout().domain_file(
        paths.Domain.ROOT, "versions.json"
    ).write_text(json.dumps(sort_dict(versiondata), indent=4))
