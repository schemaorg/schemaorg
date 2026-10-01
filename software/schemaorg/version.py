#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Version and release log management for schema.org."""

from datetime import datetime
import json
from pathlib import Path
from typing import Any, Dict, Optional, Set, Union, List


class VersionItem:
    """Individual version entry with number and release date."""

    def __init__(self, number: str, date: str) -> None:
        self._number: str = number
        self._date: Optional[str] = date
        # Validate the values
        if not number: raise ValueError(f"version {number} is not a number")
        num_version = float(number)
        datetime.strptime(date, "%Y-%m-%d")

    def number(self) -> str:
        return self._number

    def date(self) -> str:
        return self._date

    def __hash__(self) -> int:
        return hash(self._number)

    def __eq__(self, other: object) -> bool:
        return isinstance(other, VersionItem) and self._number == other._number

    def __str__(self) -> str:
        return self._number


class Version:
    """Schema.org version information read from versions.json."""

    def __init__(self, versions_path: Union[Path, str]) -> None:
        self.versions_path: Path = Path(versions_path)
        data: Dict[str, Any] = json.loads(
            self.versions_path.read_text(encoding="utf-8")
        )
        self._versions = [VersionItem(v, d) for v, d in data["releaseLog"].items()]
        self._current = [v for v in self._versions
                         if str(v) == data["schemaversion"]][0]

    def current(self) -> VersionItem:
        return self._current

    def versions(self) -> List[VersionItem]:
        return self._versions


    def add_version(self, version_number: str, date: str) -> None:
        new_version: VersionItem = VersionItem(version_number, date)

        if version_number in [str(v) for v in self._versions]:
            raise ValueError(f"Version {version_number} exists already!")

        self._versions.append(new_version)
        self._versions.sort(key=lambda vi: float(vi.number()), reverse=True)
        # The newest entry is the current one, on disk and in memory alike.
        self._current = self._versions[0]

        version_data = {
            "schemaversion": self._current.number(),
            "releaseLog": {str(vi): vi.date() for vi in self._versions},
        }
        self.versions_path.write_text(
            json.dumps(version_data, indent=4) + "\n",
            encoding="utf-8",
        )
