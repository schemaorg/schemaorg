#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import shutil
import enum


EXTENSIONS_FOR_FORMAT = {
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

    def __str__(self):
        return self.value


CHECKEDPATHS = set()
FILESET_SELECTORS = frozenset([s.value for s in FileSelector])
FILESET_PROTOCOLS = frozenset(["http", "https"])


def createMissingDir(dir_path):
    """Create a directory if it does not exist"""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


def isAll(selector: str):
    """Check if a selector string is a variation of the 'All' token."""
    return str(selector).lower() == FileSelector.ALL


def checkFilePath(path):
    if not path in CHECKEDPATHS:
        CHECKEDPATHS.add(path)
        # os.path.join ignores the first argument if `path` is absolute.
        path = os.path.join(os.getcwd(), path)
        try:
            os.makedirs(path)
        except OSError as e:
            if not os.path.isdir(path):
                raise e


def ensureAbsolutePath(output_dir: str, relative_path: str) -> str:
    """Convert into an absolute path and ensure the directory exists."""
    filepath = os.path.join(output_dir, relative_path)
    checkFilePath(os.path.dirname(filepath))
    return filepath


def releaseFilePath(
    output_dir: str,
    version: str,
    selector: FileSelector,
    protocol: str,
    output_format: str,
    suffix: str | None = None,
    subdirectory_path: str | None = None,
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
    extension = EXTENSIONS_FOR_FORMAT[output_format.lower()]
    selector = selector.lower()
    assert selector in FILESET_SELECTORS, selector
    protocol = protocol.lower()
    assert protocol in FILESET_PROTOCOLS, protocol
    parts = [selector, protocol]
    if suffix:
        parts.append(suffix)
    merged = "-".join(parts)
    filename = f"schemaorg-{merged}.{extension}"

    if subdirectory_path is None:
        subdirectory_path = f"releases/{version}"

    relative_path = os.path.join(subdirectory_path, filename)
    return ensureAbsolutePath(
        output_dir=output_dir,
        relative_path=relative_path,
    )


def mycopytree(src, dst, symlinks=False, ignore=None):
    """Copy a file-system tree, copes with already existing directories."""
    names = os.listdir(src)
    if ignore is not None:
        ignored_names = ignore(src, names)
    else:
        ignored_names = frozenset()

    if not os.path.isdir(dst):
        os.makedirs(dst)
    errors = []
    for name in names:
        if name in ignored_names:
            continue
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
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
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise Error(errors)
