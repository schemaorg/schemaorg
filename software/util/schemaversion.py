#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module that handles the schema.org version information."""

import json
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

if Path.cwd() not in [Path(p).resolve() for p in sys.path]:
    sys.path.insert(1, str(Path.cwd()))

from software.util.sort_dict import sort_dict

VERSION_DATA: Optional[Dict[str, Any]] = None

def getVersionData() -> Dict[str, Any]:
    global VERSION_DATA
    if VERSION_DATA is None:
        VERSION_DATA = json.loads(Path("versions.json").read_text())
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
    
    Path("versions.json").write_text(json.dumps(sort_dict(versiondata), indent=4))


if __name__ == "__main__":
    print(getVersion())
