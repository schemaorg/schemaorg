#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(1)

import os
import json
###################################################
#VERSION INFO LOAD
###################################################
versiondata = None
def loadVersions():
    global versiondata
    import json
    with open('versions.json') as json_file:
        versiondata = json.load(json_file)

def getVersion():
    global versiondata
    if not versiondata:
        loadVersions()
    return versiondata['schemaversion']
def getVersionDate(ver):
    global versiondata
    if not versiondata:
        loadVersions()
    return versiondata['releaseLog'].get(ver,None)

def getCurrentVersionDate():
    return getVersionDate(getVersion())
    
if __name__ == '__main__':
    print(getVersion())

