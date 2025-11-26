#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
import sys

LIB_PATHS = ()
DATA_PATHS = ("docs", "software/gcloud", "data")
REQUIRED_VERSION = (3, 11)
_INITIALIZED = None


def Setup():
    """Setup the import path for the project and check the validity of the runtime."""
    global _INITIALIZED
    if _INITIALIZED:
        return

    if sys.version_info < REQUIRED_VERSION:
        sys.stderr.write(
            f"Python version {sys.version_info.major}.{sys.version_info.minor} "
            "not supported version {REQUIRED_VERSION[0]}.{REQUIRED_VERSION[1]} "
            "or above required - Exiting\n"
            )
        sys.exit(os.EX_CONFIG)

    for path in LIB_PATHS:
        absolute_path = os.path.join(os.getcwd(), path)
        if not os.path.isdir(absolute_path):
            sys.stderr.write(
                f'Required directory "{absolute_path}" not found - Exiting\n'
            )
            sys.exit(os.EX_CONFIG)
        sys.path.insert(1, absolute_path)

    _INITIALIZED = True


def CheckWorkingDirectory():
    """Check that the working directory is correct and contains the right directories."""
    if os.path.basename(os.getcwd()) != "schemaorg":
        sys.stderr.write(
            'Script should be run from within the "schemaorg" '
            'directory! - Exiting\n'
        )
        sys.exit(os.EX_USAGE)

    for directory_name in DATA_PATHS:
        if not os.path.isdir(directory_name):
            sys.stderr.write(
                'Required directory {directory_name} not found - Exiting\n'
            )
            sys.exit(os.EX_CONFIG)


Setup()
