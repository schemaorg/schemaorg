#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(1)

import os
import glob
import re

for path in [os.getcwd(),"software/SchemaTerms","software/SchemaExamples","software/util"]:
  sys.path.insert( 1, path ) #Pickup libs from local  directories
  
if os.path.basename(os.getcwd()) != "schemaorg":
    print("\nScript should be run from within the 'schemaorg' directory! - Exiting\n")
    sys.exit(1)

for dir in ["software/util","docs","software/site","templates/static-doc-inserts"]:
    if not os.path.isdir(dir):
        print("\nRequired directory '%s' not found - Exiting\n" % dir)
        sys.exit(1)

from shutil import *
from schemaversion import *
import convertmd2htmldocs


ins = glob.glob('./templates/static-doc-inserts/*.html')
INSERTS = {}
for f in ins:
    fn = os.path.basename(f).lower()
    fn = os.path.splitext(fn)[0]
    with open(f) as ind:
        indata = ind.read()
    fn = fn[4:] #drop sdi- from file name
    indata = indata.replace('{{version}}',getVersion())
    indata = indata.replace('{{versiondate}}',getCurrentVersionDate())

    INSERTS[fn] = indata

def mycopytree(src, dst, symlinks=False, ignore=None):
    #copes with already existing directories
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = set()

    if not os.path.isdir(dst): 
        os.makedirs(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                mycopytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except Error as err:
            errors.extend(err.args[0])
        except EnvironmentError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        copystat(src, dst)
    except OSError as why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise Error (errors)


SRCDIR = './docs'
DESTDIR = './software/site/docs'
def copydocs():
    mycopytree(SRCDIR,DESTDIR)

def htmlinserts():
    docs = glob.glob(DESTDIR +'/*.html')
    for d in docs:
        insertcopy(d)

def insertcopy(doc, docdata=None):
    if not docdata:
        with open(doc) as docfile:
            docdata = docfile.read()
    
    if re.search('<!-- #### Static Doc Insert',docdata,re.IGNORECASE):
        for sub in INSERTS:
            subpattern = re.compile("<!-- #### Static Doc Insert %s .* -->" % sub,re.IGNORECASE)
            docdata = subpattern.sub(INSERTS.get(sub),docdata,re.IGNORECASE)

        targetfile = DESTDIR + '/' + os.path.basename(doc)
        with open(targetfile,"w") as outfile:
            outfile.write(docdata)
        #print("adding inserts to: " + targetfile)    






if __name__ == '__main__':
    copydocs()
    print("Converting .md docs to html")
    convertmd2htmldocs.mddocs(DESTDIR,DESTDIR)
    print("Adding header/footer templates")
    htmlinserts()