"""Version and release log management for schema.org."""

from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class VersionItem:
    """Individual version entry with number and release date."""

    _number: str
    _date: str = field(compare=False)

    def __post_init__(self) -> None:
        if not self._number:
            raise ValueError(f"version {self._number} is not a number")
        float(self._number)
        datetime.strptime(self._date, "%Y-%m-%d")

    def number(self) -> str:
        return self._number

    def date(self) -> str:
        return self._date

    def __str__(self) -> str:
        return self._number


class Version:
    """Schema.org version information read from versions.json."""

    def __init__(self, versions_path: Path | str) -> None:
        self.versions_path: Path = Path(versions_path)
        data: dict[str, Any] = json.loads(
            self.versions_path.read_text(encoding="utf-8")
        )
        self._versions = [VersionItem(v, d) for v, d in data["releaseLog"].items()]
        current = next(
            (v for v in self._versions if str(v) == data["schemaversion"]), None
        )
        if current is None:
            raise ValueError(
                f"schemaversion '{data['schemaversion']}' not found in releaseLog"
            )
        self._current = current

    def current(self) -> VersionItem:
        return self._current

    def versions(self) -> list[VersionItem]:
        return list(self._versions)

    def add_version(self, version_number: str, date: str) -> None:
        new_version = VersionItem(version_number, date)

        if any(str(v) == version_number for v in self._versions):
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
