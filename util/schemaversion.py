#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
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

