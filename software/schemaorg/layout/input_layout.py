#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Input layout management for schema.org sources."""

import os
from pathlib import Path
import sys
from typing import List, Optional, Sequence, Union

from schemaorg.layout.domain import Domain
from schemaorg.version import VersionItem


class InputLayout:
    """Floating layout resolving paths in the schema.org source tree."""

    def __init__(
        self, root_dir: Path, version: Optional[VersionItem] = None
    ) -> None:
        self.root_dir: Path = root_dir.resolve()
        self._version: Optional[VersionItem] = version

    def dir(self, domain: Domain) -> Path:
        """Return the directory path corresponding to the given Domain."""
        if domain == Domain.RELEASE_DATA:
            return self.root_dir / domain.value / str(self._version)
        return self.root_dir / domain.value

    def file(self, domain: Domain, filename: str) -> Path:
        """Return the path to a specific file within a Domain."""
        return self.dir(domain) / filename

    def files(
        self, domain: Domain, patterns: Union[str, Sequence[str]]
    ) -> List[Path]:
        """Return a sorted list of matching files for glob patterns in Domain."""
        if isinstance(patterns, str):
            patterns = [patterns]
        base = self.dir(domain)
        return sorted([f for pattern in patterns for f in base.glob(pattern)])

    # NOTE: This should be implemented as another construct over the input
    # layout rather than a method directly on InputLayout.
    def release_file(self, protocol: str) -> Path:
        """Return canonical release turtle file path ('http' or 'https')."""
        return self.dir(Domain.RELEASE_DATA) / f"schemaorg-all-{protocol}.ttl"

    def relative_file(self, path: Union[Path, str]) -> Path:
        """Return a path relative to the root directory."""
        target = Path(path)
        try:
            return target.relative_to(self.root_dir)
        except ValueError:
            return target.resolve().relative_to(self.root_dir)

    def _is_complete(self) -> bool:
        """Check that root_dir contains all required data directories.

        Raises:
            FileNotFoundError: If any required directories are missing.

        Returns:
            True if all required directories exist.
        """
        required = (Domain.DOCS, Domain.GCLOUD, Domain.DATA, Domain.TEMPLATES)
        missing = [self.dir(dom) for dom in required
                   if not self.dir(dom).is_dir()]
        if missing:
            raise FileNotFoundError(
                f"Required dirs not found: {', '.join(str(d) for d in missing)}"
            )
        return True



def checkDataDirectories() -> bool:
    """Legacy helper checking that PROJECT_ROOT contains required directories."""
    from schemaorg.constants import PROJECT_ROOT
    layout = InputLayout(PROJECT_ROOT)
    try:
        return layout._is_complete()
    except FileNotFoundError as e:
        sys.stderr.write(str(e))
        sys.exit(os.EX_CONFIG)
