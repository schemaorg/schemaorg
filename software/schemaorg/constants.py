#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Global constants for the schema.org project."""

from pathlib import Path
import pyprojroot

SCHEMA_URI: str = "https://schema.org/"
PROJECT_ROOT: Path = Path(pyprojroot.find_root(pyprojroot.has_file("versions.json"),
                                               Path(__file__).parent))
