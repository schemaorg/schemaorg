#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


import os
import sys

LIB_PATHS = ('software/util', 'software/SchemaTerms','software/SchemaExamples')
DATA_PATHS = ('docs', 'software/gcloud','data')
_INITIALIZED = None

def Setup():
    """Setup the import path for the project and check the validity of the runtime."""
    global _INITIALIZED
    if _INITIALIZED:
        return

    if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
        sys.stderr.write("Python version %s.%s not supported version 3.6 or above required - Exiting" % (sys.version_info.major,sys.version_info.minor))
        sys.exit(os.EX_CONFIG)

    for path in LIB_PATHS:
        absolute_path = os.path.join(os.getcwd(), path)
        if not os.path.isdir(absolute_path):
            sys.stderr.write('Required directory "%s" not found - Exiting\n' % absolute_path)
            sys.exit(os.EX_CONFIG)
        sys.path.insert(1, absolute_path)

    _INITIALIZED = True


def CheckWorkingDirectory():
    """Check that the working directory is correct and contains the right directories."""
    if os.path.basename(os.getcwd()) != 'schemaorg':
        sys.stderr.write('Script should be run from within the "schemaorg" directory! - Exiting\n')
        sys.exit(os.EX_USAGE)

    for directory_name in DATA_PATHS:
        if not os.path.isdir(directory_name):
            sys.stderr.write('Required directory "%s" not found - Exiting\n' % directory_name)
            sys.exit(os.EX_CONFIG)

Setup()

