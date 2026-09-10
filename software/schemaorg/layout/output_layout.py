#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Output layout management for generated schema.org website files."""

from pathlib import Path
from typing import Optional, Union

from schemaorg.layout.domain import Domain
from schemaorg.version import VersionItem


class OutputLayout:
    """Floating layout resolving output paths and ensuring directory creation."""

    def __init__(
        self, output_dir: Path, version: Optional[VersionItem] = None
    ) -> None:
        self.output_dir: Path = output_dir.resolve()
        self._version: Optional[VersionItem] = version

    @staticmethod
    def _ensure_dir(path: Path) -> Path:
        """Create directory and its parents if missing."""
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_output_dir(self) -> Path:
        """Return root output directory, ensuring it exists."""
        return self._ensure_dir(self.output_dir)

    def dir(self, domain: Domain) -> Path:
        """Return directory for the given Domain, ensuring it exists."""
        if domain == Domain.RELEASE:
            path = self.output_dir / domain.value / str(self._version)
        elif domain == Domain.GCLOUD:
            path = self.output_dir / Domain.GCLOUD_SITE.value
        else:
            path = self.output_dir / domain.value
        return self._ensure_dir(path)

    def file(self, domain: Domain, filename: str) -> Path:
        """Return file path in Domain, ensuring parent directory exists."""
        path = self.dir(domain) / filename
        self._ensure_dir(path.parent)
        return path

