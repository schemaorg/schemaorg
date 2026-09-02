#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module that handles loading and parsing of dynamic public stats providers."""

import csv
from dataclasses import dataclass
import datetime
from functools import lru_cache
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union
import unicodedata

import util.paths as paths

@dataclass
class StatsProvider:
    provider_id: str
    name: str
    description: str
    date: str
    stats_map: Dict[str, str]

class StatsLayout:
    """Handles layout and file discovery for public statistics."""

    def __init__(self, layout: paths.InputLayout) -> None:
        self.base_dir: Path = layout.domain_dir(paths.Domain.PUBLIC_STATS)

    def providers(self) -> List[str]:
        """Lists the providers (subdirs) present in the stats dir."""
        if not self.base_dir.is_dir(): return []
        return sorted([subdir.name for subdir in self.base_dir.iterdir()
                       if subdir.is_dir() and not subdir.name.startswith(".")])

    def _list_files(self, provider: str, ext: Optional[str] = None) -> List[Path]:
        """Private method to list the files in a provider's directory."""
        provider_dir = self.base_dir / provider
        if not provider_dir.is_dir(): return []
        return sorted([p for p in provider_dir.iterdir()
                       if p.is_file() and (not ext or p.suffix == f".{ext}")])

    def epochs(self, provider: str, ext: Optional[str] = "json") -> Dict[str, List[Path]]:
        """Provides the different sets of stats files found in a provider's directory."""
        def extract_epoch(filename):
            m = re.search(r"(\d{4}_\d{2})", filename.name)
            return datetime.datetime.strptime(m.group(1), "%Y_%m") if m else None

        return dict([(extract_epoch(f), f) for f in self._list_files(provider, ext)
                     if "summary" not in f.name])

    def _read_json(self, file_path: Union[Path, str]) -> Any:
        """Private method to read and parse a JSON file."""
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _read_csv(self, file_path: Union[Path, str]) -> Any:
        """Private method to read and parse a CSV file."""
        records = []
        with open(file_path, "r", encoding="utf-8", newline="") as f:
            for row in csv.DictReader(f):
                record = dict([(field.strip(), row[field]) for field in row.keys()])
                records.append(record)
        return records

    def get_stats(self, providers: Optional[Sequence[str]] = None) -> List[StatsProvider]:
        """Returns a list of StatsProvider objects."""
        providers = [p for p in self.providers() if not providers or p in providers]

        result: List[StatsProvider] = []
        for provider in providers:
            epochs = self.epochs(provider)
            latest_epoch = sorted(epochs.keys())[-1]
            json_file = epochs[latest_epoch]

            stats_map: Dict[str, str] = {}
            for entry in self._read_json(json_file):
                entry_name = entry.get("Name").strip()
                bucket = entry.get("Domain Bucket").strip()
                normalized_name = unicodedata.normalize("NFC", entry_name).replace("http://", "https://")
                stats_map[normalized_name] = bucket

            result.append(
                StatsProvider(
                    provider_id=provider,
                    name=provider.capitalize(),
                    description=f"Based on monthly aggregations from {provider}'s web index.",
                    date=latest_epoch.strftime("%B %Y"),
                    stats_map=stats_map,
                )
            )

        return result


@lru_cache(maxsize=1)
def get_stats_providers() -> List[StatsProvider]:
    """Lazily loads and parses all public stats providers from the filesystem."""
    stats_layout = StatsLayout(paths.DefaultInputLayout())
    return stats_layout.get_stats()
