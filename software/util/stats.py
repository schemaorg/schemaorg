#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module that handles loading and parsing of dynamic public stats providers."""

from dataclasses import dataclass
import datetime
import json
import unicodedata
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import util.paths as paths

@dataclass
class StatsProvider:
    provider_id: str
    name: str
    description: str
    date: str
    stats_map: Dict[str, str]

@lru_cache(maxsize=1)
def get_stats_providers() -> List[StatsProvider]:
    """Lazily loads and parses all public stats providers from the filesystem."""
    providers: List[StatsProvider] = []
    
    try:
        base_dir = paths.DefaultInputLayout().domain_dir(paths.Domain.PUBLIC_STATS)
        if base_dir.is_dir():
            for subdir in sorted(base_dir.iterdir()):
                if not subdir.is_dir():
                    continue
                
                provider_id = subdir.name
                name = provider_id.capitalize()
                description = f"Based on monthly aggregations from {name}'s web index."
                
                json_files = list(subdir.glob("????_??.json"))
                json_files = [f for f in json_files if "summary" not in f.name]
                
                if json_files:
                    latest_file = sorted(json_files)[-1]
                    date_str = "Recent"
                    try:
                        date_part = latest_file.stem
                        dt = datetime.datetime.strptime(date_part, "%Y_%m")
                        date_str = dt.strftime("%B %Y")
                    except Exception:
                        pass
                        
                    stats_map: Dict[str, str] = {}
                    try:
                        with open(latest_file, "r", encoding="utf-8") as f:
                            stats_data = json.load(f)
                        if isinstance(stats_data, list):
                            for entry in stats_data:
                                if not isinstance(entry, dict):
                                    continue
                                entry_name = entry.get("Name")
                                bucket = entry.get("Domain Bucket")
                                if isinstance(entry_name, str) and isinstance(bucket, str):
                                    entry_name = entry_name.strip()
                                    bucket = bucket.strip()
                                    normalized_name = unicodedata.normalize("NFC", entry_name)
                                    stats_map[normalized_name.replace("https://", "http://")] = bucket
                                    stats_map[normalized_name.replace("http://", "https://")] = bucket
                    except Exception:
                        continue
                        
                    providers.append(
                        StatsProvider(
                            provider_id=provider_id,
                            name=name,
                            description=description,
                            date=date_str,
                            stats_map=stats_map
                        )
                    )
    except Exception:
        pass
        
    return providers
