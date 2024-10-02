#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""Module that handles the schema.org version information."""

import sys
import os
import json

###################################################
# VERSION INFO LOAD
###################################################

VERSION_DATA = None


def getVersionData():
    global VERSION_DATA
    if not VERSION_DATA:
        with open("versions.json") as json_file:
            VERSION_DATA = json.load(json_file)
    return VERSION_DATA


def getVersion():
    return getVersionData()["schemaversion"]


def getVersionDate(ver):
    return getVersionData()["releaseLog"].get(ver, None)


def getCurrentVersionDate():
    return getVersionDate(getVersion())


def setVersion(ver, date):
    versiondata = getVersionData()
    versiondata["schemaversion"] = ver
    versiondata["releaseLog"][ver] = date
    vers = versiondata["releaseLog"]
    vers = dict(sorted(vers.items(), key=lambda x: float(x[0]), reverse=True))
    versiondata["releaseLog"] = vers
    with open("versions.json", "w") as json_file:
        json_file.write(json.dumps(versiondata, indent=4))


if __name__ == "__main__":
    print(getVersion())
