#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Input layout management for schema.org sources."""

import os
from pathlib import Path
import sys
from typing import List, Sequence, Union

from schemaorg.layout.domain import Domain


class InputLayout:
    """Floating layout resolving paths in the schema.org source tree."""

    def __init__(self, root_dir: Path) -> None:
        self.root_dir: Path = root_dir.resolve()

    def dir(self, domain: Domain) -> Path:
        """Return the directory path corresponding to the given Domain."""
        if domain == Domain.RELEASE:
            return self.root_dir / Domain.DATA.value / domain.value
        return self.root_dir / domain.value

    def file(self, domain: Domain, filename: str) -> Path:
        """Return the path to a specific file within a Domain."""
        return self.dir(domain) / filename

    def files(
        self, domain: Domain, patterns: Union[str, Sequence[str]]
    ) -> List[Path]:
        """Return matching files for glob patterns in Domain, sorted per pattern."""
        if isinstance(patterns, str):
            patterns = [patterns]
        base = self.dir(domain)
        # Sort per pattern to preserve caller pattern order (e.g. core before ext
        # in schemaorg-all-examples.txt); global sort splices subdirs mid-list.
        return [
            f
            for pattern in patterns
            for f in sorted(base.glob(pattern))
            if not f.name.startswith(".")
        ]

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
