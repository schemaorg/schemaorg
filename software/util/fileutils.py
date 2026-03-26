#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import enum
from typing import Dict, Set, Union, Optional, List, Callable, Iterable, Any


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
        return self.value


CHECKEDPATHS: Set[str] = set()
FILESET_SELECTORS: Set[str] = frozenset([s.value for s in FileSelector])
FILESET_PROTOCOLS: Set[str] = frozenset(["http", "https"])


def createMissingDir(dir_path: str) -> None:
    """Create a directory if it does not exist"""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def isAll(selector: Union[str, FileSelector]) -> bool:
    """Check if a selector string is a variation of the 'All' token."""
    return str(selector).lower() == FileSelector.ALL


def checkFilePath(path: str) -> None:
    if not path in CHECKEDPATHS:
        CHECKEDPATHS.add(path)
        # os.path.join ignores the first argument if `path` is absolute.
        full_path: str = os.path.join(os.getcwd(), path)
        try:
            os.makedirs(full_path)
        except OSError as e:
            if not os.path.isdir(full_path):
                raise e


def ensureAbsolutePath(output_dir: str, relative_path: str) -> str:
    """Convert into an absolute path and ensure the directory exists."""
    filepath: str = os.path.join(output_dir, relative_path)
    checkFilePath(os.path.dirname(filepath))
    return filepath


def releaseFilePath(
    output_dir: str,
    version: str,
    selector: Union[str, FileSelector],
    protocol: str,
    output_format: str,
    suffix: Optional[str] = None,
    subdirectory_path: Optional[str] = None,
) -> str:
    """Create a path for a release file

    Args:
        output_directory: typically schemaglobals.OUTPUTDIR
        version: version number
        selector: either FileSelector.ALL or FileSelector.CURRENT
        protocol: either 'http' or 'https'
        output_format: one of the keys present in `EXTENSIONS_FOR_FORMAT`
        suffix: optional suffix that is ended at the end of the file.
        subdirectory_path: optional subdirectory path. If None, defaults to "releases/{version}". An empty string means the root of output_dir.
    Returns:
        an absolute path with the necessary directories created.
    """
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

    relative_path: str = os.path.join(subdirectory_path, filename)
    return ensureAbsolutePath(
        output_dir=output_dir,
        relative_path=relative_path,
    )


def mycopytree(src: str, dst: str, symlinks: bool = False, ignore: Optional[Callable[[str, List[str]], Iterable[str]]] = None) -> None:
    """Copy a file-system tree, copes with already existing directories."""
    names: List[str] = os.listdir(src)
    ignored_names: Set[str]
    if ignore is not None:
        ignored_names = set(ignore(src, names))
    else:
        ignored_names = set()

    if not os.path.isdir(dst):
        os.makedirs(dst)
    errors: List[Any] = []
    for name in names:
        if name in ignored_names:
            continue
        srcname: str = os.path.join(src, name)
        dstname: str = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto: str = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif os.path.isdir(srcname):
                mycopytree(srcname, dstname, symlinks, ignore)
            else:
                # Will raise a SpecialFileError for unsupported file types
                shutil.copy2(srcname, dstname)
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except OSError as err:
            errors.extend(err.args[0])
        except EnvironmentError as why:
            errors.append((srcname, dstname, str(why)))
    try:
        shutil.copystat(src, dst)
    except OSError as why:
        # WindowsError might not be available on all systems
        win_err = getattr(__builtins__, 'WindowsError', None)
        if win_err and isinstance(why, win_err):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.append((src, dst, str(why)))
    if errors:
        raise Exception(errors)
