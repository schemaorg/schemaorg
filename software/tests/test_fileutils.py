#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pathlib import Path
import tempfile
import unittest

import util.fileutils as fileutils


class FileUtilsTest(unittest.TestCase):
    def test_isAll(self):
        self.assertTrue(fileutils.isAll("all"))
        self.assertTrue(fileutils.isAll("ALL"))
        self.assertTrue(fileutils.isAll(fileutils.FileSelector.ALL))
        self.assertFalse(fileutils.isAll("current"))
        self.assertFalse(fileutils.isAll(fileutils.FileSelector.CURRENT))

    def test_mycopytree(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            src = Path(tmp_dir) / "src"
            dst = Path(tmp_dir) / "dst"
            src.mkdir()
            (src / "hello.txt").write_text("world")

            fileutils.mycopytree(str(src), str(dst))
            self.assertEqual((dst / "hello.txt").read_text(), "world")


if __name__ == "__main__":
    unittest.main()
