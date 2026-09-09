#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Module that handles layout and parsing of dynamic public stats providers."""

import csv
from dataclasses import dataclass
import datetime
import json
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Sequence, Union
import unicodedata

from schemaorg.layout.domain import Domain
from schemaorg.layout.input_layout import InputLayout


@dataclass
class StatsProvider:
    provider_id: str
    name: str
    description: str
    date: str
    stats_map: Dict[str, str]


class StatsLayout:
    """Handles layout and file discovery for public statistics."""

    def __init__(self, layout: InputLayout) -> None:
        self.base_dir: Path = layout.dir(Domain.PUBLIC_STATS)

    def providers(self) -> List[str]:
        """Lists the providers (subdirs) present in the stats dir."""
        if not self.base_dir.is_dir():
            return []
        return sorted(
            subdir.name
            for subdir in self.base_dir.iterdir()
            if subdir.is_dir() and not subdir.name.startswith(".")
        )

    def _list_files(
        self, provider: str, ext: Optional[str] = None
    ) -> List[Path]:
        """Private method to list the files in a provider's directory."""
        provider_dir = self.base_dir / provider
        if not provider_dir.is_dir():
            return []
        return sorted(
            p
            for p in provider_dir.iterdir()
            if p.is_file() and (not ext or p.suffix == f".{ext}")
        )

    def epochs(
        self, provider: str, ext: Optional[str] = "json"
    ) -> Dict[datetime.datetime, Path]:
        """Provides the different sets of stats files found in a provider's directory."""

        def extract_epoch(filename: Path) -> Optional[datetime.datetime]:
            m = re.search(r"(\d{4}_\d{2})", filename.name)
            return (
                datetime.datetime.strptime(m.group(1), "%Y_%m")
                if m
                else None
            )

        return {
            epoch: f
            for f in self._list_files(provider, ext)
            if "summary" not in f.name and (epoch := extract_epoch(f)) is not None
        }

    def _read_json(self, file_path: Union[Path, str]) -> Any:
        """Private method to read and parse a JSON file."""
        return json.loads(Path(file_path).read_text(encoding="utf-8"))

    def _read_csv(self, file_path: Union[Path, str]) -> Any:
        """Private method to read and parse a CSV file."""
        with open(file_path, "r", encoding="utf-8", newline="") as f:
            return [
                {field.strip(): val for field, val in row.items()}
                for row in csv.DictReader(f)
            ]

    def get_stats(
        self, providers: Optional[Sequence[str]] = None
    ) -> List[StatsProvider]:
        """Returns a list of StatsProvider objects."""
        providers = [
            p for p in self.providers() if not providers or p in providers
        ]

        result: List[StatsProvider] = []
        for provider in providers:
            epochs = self.epochs(provider)
            if not epochs:
                continue
            latest_epoch = max(epochs)
            json_file = epochs[latest_epoch]

            stats_map: Dict[str, str] = {}
            for entry in self._read_json(json_file):
                entry_name = entry.get("Name").strip()
                bucket = entry.get("Domain Bucket").strip()
                normalized_name = unicodedata.normalize("NFC", entry_name)
                stats_map[normalized_name] = bucket

            result.append(
                StatsProvider(
                    provider_id=provider,
                    name=provider.capitalize(),
                    description=f"Based on monthly aggregations from {provider.capitalize()}'s web index.",
                    date=latest_epoch.strftime("%B %Y"),
                    stats_map=stats_map,
                )
            )

        return result
