#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Layout package managing filesystem paths and domains for schema.org."""

from schemaorg.layout.domain import Domain
from schemaorg.layout.input_layout import InputLayout, checkDataDirectories
from schemaorg.layout.output_layout import OutputLayout

__all__ = [
    "Domain",
    "InputLayout",
    "OutputLayout",
    "checkDataDirectories",
]
