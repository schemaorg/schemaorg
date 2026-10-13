#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import enum
import shutil
from typing import Callable, Dict, FrozenSet, Iterable, List, Optional, Union

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


FILESET_SELECTORS: FrozenSet[str] = frozenset(s.value for s in FileSelector)
FILESET_PROTOCOLS: FrozenSet[str] = frozenset(["http", "https"])


def isAll(selector: Union[str, FileSelector]) -> bool:
    """Check if a selector string is a variation of the 'All' token."""
    return str(selector).lower() == FileSelector.ALL


def mycopytree(src: str, dst: str, symlinks: bool = False, ignore: Optional[Callable[[str, List[str]], Iterable[str]]] = None) -> None:
    """Copy a file-system tree, copes with already existing directories."""
    try:
        shutil.copytree(src, dst, symlinks=symlinks, ignore=ignore, dirs_exist_ok=True)
    except shutil.Error as err:
        raise Exception(err.args[0])
