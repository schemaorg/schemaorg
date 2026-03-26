#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module that handles the schema.org version information."""

import json
import os
import sys
from typing import Dict, Any, Optional

if os.getcwd() not in sys.path:
    sys.path.insert(1, os.getcwd())

from software.util.sort_dict import sort_dict

###################################################
# VERSION INFO LOAD
###################################################

VERSION_DATA: Optional[Dict[str, Any]] = None


def getVersionData() -> Dict[str, Any]:
    global VERSION_DATA
    if not VERSION_DATA:
        with open("versions.json") as json_file:
            VERSION_DATA = json.load(json_file)
    assert VERSION_DATA is not None
    return VERSION_DATA


def getVersion() -> str:
    return str(getVersionData()["schemaversion"])


def getVersionDate(ver: str) -> Optional[str]:
    return getVersionData()["releaseLog"].get(ver, None)


def getCurrentVersionDate() -> Optional[str]:
    return getVersionDate(getVersion())


def setVersion(ver: str, date: str) -> None:
    versiondata: Dict[str, Any] = getVersionData()
    versiondata["schemaversion"] = ver
    versiondata["releaseLog"][ver] = date
    vers: Dict[str, str] = versiondata["releaseLog"]
    sorted_vers: Dict[str, str] = dict(sorted(vers.items(), key=lambda x: float(x[0]), reverse=True))
    versiondata["releaseLog"] = sorted_vers
    with open("versions.json", "w") as json_file:
        json_file.write(json.dumps(sort_dict(versiondata), indent=4))


if __name__ == "__main__":
    print(getVersion())
