#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import enum
import shutil
from pathlib import Path
from typing import Dict, Set, Union, Optional, List, Callable, Iterable, Any, FrozenSet

EXTENSIONS_FOR_FORMAT: Dict[str, str] = {
    "xml": "xml",
    "rdf": "rdf",
    "nquads": "nq",
    "nt": "nt",
    "json-ld": "jsonld",
    "turtle": "ttl",
    "csv": "csv",
}


class FileSelector(str, enum.Enum):
    """Enumeration describing the type of an SdoTerm."""

    ALL = "all"
    CURRENT = "current"

    def __str__(self) -> str:
        return str(self.value)


CHECKEDPATHS: Set[Path] = set()
FILESET_SELECTORS: FrozenSet[str] = frozenset([s.value for s in FileSelector])
FILESET_PROTOCOLS: FrozenSet[str] = frozenset(["http", "https"])


def createMissingDir(dir_path: Union[str, Path]) -> None:
    """Create a directory if it does not exist"""
    Path(dir_path).mkdir(parents=True, exist_ok=True)


def isAll(selector: Union[str, FileSelector]) -> bool:
    """Check if a selector string is a variation of the 'All' token."""
    return str(selector).lower() == FileSelector.ALL


def checkFilePath(path: Union[str, Path]) -> None:
    full_path: Path = Path(path).resolve()
    if full_path not in CHECKEDPATHS:
        full_path.mkdir(parents=True, exist_ok=True)
        CHECKEDPATHS.add(full_path)


def ensureAbsolutePath(output_dir: Union[str, Path], relative_path: str) -> str:
    """Convert into an absolute path and ensure the directory exists."""
    filepath: Path = Path(output_dir) / relative_path
    checkFilePath(filepath.parent)
    return str(filepath.absolute())


def releaseFilePath(
    output_dir: str,
    version: str,
    selector: Union[str, FileSelector],
    protocol: str,
    output_format: str,
    suffix: Optional[str] = None,
    subdirectory_path: Optional[str] = None,
) -> str:
    """Create a path for a release file"""
    extension: str = EXTENSIONS_FOR_FORMAT[output_format.lower()]
    selector_str: str = str(selector).lower()
    assert selector_str in FILESET_SELECTORS, selector_str
    protocol = protocol.lower()
    assert protocol in FILESET_PROTOCOLS, protocol
    
    parts: List[str] = [selector_str, protocol]
    if suffix:
        parts.append(suffix)
    merged: str = "-".join(parts)
    filename: str = f"schemaorg-{merged}.{extension}"

    if subdirectory_path is None:
        subdirectory_path = f"releases/{version}"

    return ensureAbsolutePath(
        output_dir=output_dir,
        relative_path=str(Path(subdirectory_path) / filename),
    )


def mycopytree(src: str, dst: str, symlinks: bool = False, ignore: Optional[Callable[[str, List[str]], Iterable[str]]] = None) -> None:
    """Copy a file-system tree, copes with already existing directories."""
    try:
        shutil.copytree(src, dst, symlinks=symlinks, ignore=ignore, dirs_exist_ok=True)
    except shutil.Error as err:
        raise Exception(err.args[0])
