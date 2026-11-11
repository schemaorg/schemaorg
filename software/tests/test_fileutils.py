from __future__ import annotations

import unittest

import util.fileutils as fileutils


class FileUtilsTest(unittest.TestCase):
    def test_isAll(self) -> None:
        self.assertTrue(fileutils.isAll("all"))
        self.assertTrue(fileutils.isAll("ALL"))
        self.assertTrue(fileutils.isAll(fileutils.FileSelector.ALL))
        self.assertFalse(fileutils.isAll("current"))
        self.assertFalse(fileutils.isAll(fileutils.FileSelector.CURRENT))


if __name__ == "__main__":
    unittest.main()
