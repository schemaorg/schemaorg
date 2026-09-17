#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Layout package managing filesystem paths and domains for schema.org."""

from schemaorg.layout.domain import Domain
from schemaorg.layout.input_layout import InputLayout, checkDataDirectories
from schemaorg.layout.issues import ALL_ISSUES, Issues
from schemaorg.layout.output_layout import OutputLayout
from schemaorg.layout.releases import (
    CURRENT_VERSION,
    Protocol,
    Releases,
    Scope,
)
from schemaorg.layout.stats_layout import StatsLayout, StatsProvider

__all__ = [
    "ALL_ISSUES",
    "Domain",
    "InputLayout",
    "Issues",
    "CURRENT_VERSION",
    "OutputLayout",
    "Protocol",
    "Releases",
    "Scope",
    "StatsLayout",
    "StatsProvider",
    "checkDataDirectories",
]
