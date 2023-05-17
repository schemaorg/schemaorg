#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(1)


import os
import io
for path in [os.getcwd(),"software/Util","software/SchemaTerms","software/SchemaExamples"]:
  sys.path.insert( 1, path ) #Pickup libs from local  directories

from buildsite import *
from sdotermsource import SdoTermSource, VOCABURI
from sdoterm import SdoTerm

def buildlist(tag=False):
    list = []
    for t in SdoTermSource.getAllTerms(expanded=True):
        label = ""
        if tag:
            if t.termType == SdoTerm.PROPERTY:
                label = " p"
            elif t.termType == SdoTerm.TYPE:
                label = " t"
            elif t.termType == SdoTerm.DATATYPE:
                label = " d"
            elif t.termType == SdoTerm.ENUMERATION:
                label = " e"
            elif t.termType == SdoTerm.ENUMERATIONVALUE:
                label = " v"
        list.append(t.id + label + "\n")
    return ''.join(list)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-t","--tagtype", default=False, action='store_true', help="Add a termtype to name")
    parser.add_argument("-o","--output", required=True, help="output file")
    args = parser.parse_args()

    out = buildlist(tag=args.tagtype)

    print("buildtermlist: Writing to: %s" % fname)
    file = open(fname, "w",encoding='utf8')
    file.write(out)



