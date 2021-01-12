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

def setVersion(ver,date):
    global versiondata
    if not versiondata:
        loadVersions()

    versiondata['schemaversion'] = ver
    versiondata['releaseLog'][ver] = date
    vers = versiondata['releaseLog']
    vers = dict(sorted(vers.items(), key=lambda x: float(x[0]), reverse=True))
    versiondata['releaseLog'] = vers
    with open('versions.json', "w") as json_file:
        json_file.write(json.dumps(versiondata,indent=4))



    
if __name__ == '__main__':
    print(getVersion())

