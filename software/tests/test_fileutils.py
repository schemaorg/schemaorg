from __future__ import annotations

import unittest

import util.fileutils as fileutils


class FileUtilsTest(unittest.TestCase):
    def test_isAll(self) -> None:
        self.assertTrue(fileutils.isAll("all"))
        self.assertTrue(fileutils.isAll("ALL"))
        self.assertFalse(fileutils.isAll("current"))


if __name__ == "__main__":
    unittest.main()
