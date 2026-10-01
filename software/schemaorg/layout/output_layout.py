#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Output layout management for generated schema.org website files."""

from pathlib import Path

from schemaorg.layout.domain import Domain


class OutputLayout:
    """Floating layout resolving output paths and ensuring directory creation.

    The layout is version-agnostic: ``Domain.RELEASE`` is the directory
    holding *all* releases. Picking a version inside it is ``Releases``' job.
    """

    def __init__(self, output_dir: Path) -> None:
        self.output_dir: Path = output_dir.resolve()

    @staticmethod
    def _ensure_dir(path: Path) -> Path:
        """Create directory and its parents if missing."""
        path.mkdir(parents=True, exist_ok=True)
        return path

    def dir(self, domain: Domain) -> Path:
        """Return directory for the given Domain, ensuring it exists."""
        if domain == Domain.GCLOUD:
            path = self.output_dir / Domain.GCLOUD_SITE.value
        else:
            path = self.output_dir / domain.value
        return self._ensure_dir(path)

    def file(self, domain: Domain, filename: str) -> Path:
        """Return file path in Domain, ensuring parent directory exists."""
        path = self.dir(domain) / filename
        self._ensure_dir(path.parent)
        return path

