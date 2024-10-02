#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import os
import shutil


def createMissingDir(dir_path):
    """Create a directory if it does not exist"""
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)


CHECKEDPATHS = []


def checkFilePath(path):
    if not path in CHECKEDPATHS:
        CHECKEDPATHS.append(path)
        # os.path.join ignores the first argument if `path` is absolute.
        path = os.path.join(os.getcwd(), path)
        try:
            os.makedirs(path)
        except OSError as e:
            if not os.path.isdir(path):
                raise e


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
