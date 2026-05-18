#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import glob
import string
import sys
import os
import locale
from pathlib import Path
from typing import List, Optional, Union, Sequence
from enum import Enum, unique

# Globally enforce UTF-8 as the default encoding for file reads/writes
def _enforce_global_utf8() -> None:
    if hasattr(locale, 'getencoding'):
        locale.getencoding = lambda: 'utf-8'
    locale.getpreferredencoding = lambda do_setlocale=True: 'utf-8'

_enforce_global_utf8()

# Need to safely import schemaglobals to read OUTPUTDIR
if Path.cwd() not in [Path(p).resolve() for p in sys.path]:
    sys.path.insert(1, str(Path.cwd()))
import software.util.schemaglobals as schemaglobals
import software.util.schemaversion as schemaversion


@unique
class Domain(str, Enum):
    DATA = "data"
    DOCS = "docs"
    GCLOUD = "gcloud"
    TEMPLATES = "templates"
    STATIC_DOC_INSERTS = "static_doc_inserts"
    RELEASE_DATA = "release_data"
    RELEASE = "release"
    LATEST_RELEASE = "latest_release"
    TERMS = "terms"
    EMPTY = "empty"
    RELEASES = "releases"
    ROOT = "root"
    DOCS_COLLAB = "docs/collab"
    DOCS_TERMFIND = "docs/termfind"

    def __str__(self) -> str:
        return str(self.value)


class InputLayout:
    def __init__(self, root_dir: Path) -> None:
        self.root_dir: Path = Path(root_dir).resolve()

    def domain_dir(self, domain: Domain) -> Path:
        if domain in (Domain.DATA, Domain.DOCS, Domain.TEMPLATES):
            return self.root_dir / domain
        elif domain == Domain.GCLOUD:
            return self.root_dir / "software" / "gcloud"
        elif domain == Domain.STATIC_DOC_INSERTS:
            return self.root_dir / "templates" / "static-doc-inserts"
        elif domain == Domain.RELEASE_DATA:
            return self.root_dir / "data" / "releases" / schemaversion.getVersion()
        elif domain == Domain.ROOT:
            return self.root_dir
        else:
            return self.root_dir / domain

    def domain_file(self, domain: Domain, filename: str) -> Path:
        return self.domain_dir(domain) / filename

    def domain_files(self, domain: Domain, patterns: Union[str, List[str]]) -> List[Path]:
        if isinstance(patterns, str):
            patterns = [patterns]
        files = []
        base_dir = self.domain_dir(domain)
        for p in patterns:
            globs = base_dir / p
            files.extend([Path(path) for path in sorted(glob.glob(str(globs)))])
        return files

    def relative(self, path: Union[Path, str]) -> Path:
        try:
            return Path(path).relative_to(self.root_dir)
        except ValueError:
            return Path(path).resolve().relative_to(self.root_dir)


class OutputLayout:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir: Path = Path(output_dir).resolve()

    def _create_dir_if_missing(self, path: Path) -> Path:
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_output_dir(self) -> Path:
        return self._create_dir_if_missing(self.output_dir)

    def domain_dir(self, domain: Domain) -> Path:
        if domain == Domain.RELEASE:
            path = self.output_dir / "releases" / schemaversion.getVersion()
        elif domain == Domain.LATEST_RELEASE:
            path = self.output_dir / "releases" / "LATEST"
        else:
            path = self.output_dir / domain
        return self._create_dir_if_missing(path)

    def domain_file(self, domain: Domain, filename: str) -> Path:
        path = self.domain_dir(domain) / filename
        self._create_dir_if_missing(path.parent)
        return path

    def generic_file(self, relative_path: str) -> Path:
        path: Path = self.output_dir / relative_path
        self._create_dir_if_missing(path.parent)
        return path


def DefaultInputLayout() -> InputLayout:
    """Returns the default InputLayout instance relative to the current working directory."""
    return InputLayout(Path.cwd())


def DefaultOutputLayout() -> OutputLayout:
    """Returns the default OutputLayout instance relative to the schemaglobals.OUTPUTDIR."""
    return OutputLayout(Path(schemaglobals.OUTPUTDIR))
