#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module that handles loading and parsing of dynamic public stats providers."""

from functools import lru_cache
from typing import List

from schemaorg.layout import StatsLayout, StatsProvider
import util.paths as paths


@lru_cache(maxsize=1)
def get_stats_providers() -> List[StatsProvider]:
    """Lazily loads and parses all public stats providers from the filesystem."""
    stats_layout = StatsLayout(paths.DefaultInputLayout())
    return stats_layout.get_stats()

