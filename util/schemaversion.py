#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
import os
import json
for path in [os.getcwd()]:
  sys.path.insert( 1, path ) #Pickup libs from local  directories
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

