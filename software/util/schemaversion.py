#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module that handles the schema.org version information."""

import json
import os
import sys
from typing import Any, Dict, List, Optional, Tuple

if os.getcwd() not in sys.path:
    sys.path.insert(1, os.getcwd())
import software

import util.paths as paths
from util.sort_dict import sort_dict


VERSION_DATA: Optional[Dict[str, Any]] = None

def getVersionData() -> Dict[str, Any]:
    global VERSION_DATA
    if VERSION_DATA is None:
        VERSION_DATA = json.loads(paths.DefaultInputLayout().domain_file(paths.Domain.ROOT, "versions.json").read_text())
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
    versiondata["releaseLog"] = dict(sorted(logs.items(), key=lambda x: float(x[0]), reverse=True))

    paths.DefaultInputLayout().domain_file(paths.Domain.ROOT, "versions.json").write_text(json.dumps(sort_dict(versiondata), indent=4))


if __name__ == "__main__":
    print(getVersion())
