#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Input layout management and data directory verification for schema.org."""

import os
import sys

from schemaorg.constants import PROJECT_ROOT


def checkDataDirectories() -> None:
    """Check that the project root contains the required data directories."""
    data_paths = ("docs", "software/gcloud", "data", "templates")
    for dir_name in data_paths:
        if not (PROJECT_ROOT / dir_name).is_dir():
            sys.stderr.write(
                f'Required directory "{dir_name}" not found in {PROJECT_ROOT} - Exiting\n'
            )
            sys.exit(os.EX_CONFIG)
