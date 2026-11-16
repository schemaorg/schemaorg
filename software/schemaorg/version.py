"""Version and release log management for schema.org."""

from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
from typing import Any


NEXT_VERSION: str = "next"
LATEST_RELEASE: str = "latest"


@dataclass(frozen=True)
class VersionItem:
    """Individual version entry with identifier and optional release date."""

    _number: str
    _date: str | None = field(default=None, compare=False)

    def __post_init__(self) -> None:
        if not self._number:
            raise ValueError(f"version {self._number!r} is not a number")
        if self._number == NEXT_VERSION:
            if self._date is not None:
                raise ValueError(
                    f"unreleased version '{NEXT_VERSION}' must not have a date"
                )
        else:
            float(self._number)
            if not self._date:
                raise ValueError(
                    f"version {self._number} requires a release date"
                )
            datetime.strptime(self._date, "%Y-%m-%d")

    def is_next(self) -> bool:
        return self._number == NEXT_VERSION

    def number(self) -> str:
        return self._number

    def date(self) -> str | None:
        return self._date

    def __str__(self) -> str:
        return self._number


_NEXT_ITEM: VersionItem = VersionItem(NEXT_VERSION)


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

    def next(self) -> VersionItem:
        return _NEXT_ITEM

    def current(self) -> VersionItem:
        return self._current

    def versions(self) -> list[VersionItem]:
        return list(self._versions)

    def resolve(
        self, version: str | VersionItem | None = NEXT_VERSION
    ) -> VersionItem:
        if version is None or str(version) == NEXT_VERSION:
            return self.next()
        wanted = str(version)
        if wanted == LATEST_RELEASE:
            return self.current()
        found = next((v for v in self._versions if str(v) == wanted), None)
        if found is not None:
            return found
        declared = ", ".join(str(v) for v in self._versions)
        raise ValueError(
            f"Version {wanted} is not declared in "
            f"{self.versions_path}. Declared: {declared}"
        )

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
