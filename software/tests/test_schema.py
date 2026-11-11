from __future__ import annotations

import unittest

from schemaorg.version import Version
import util.schema as schema


class TestSchema(unittest.TestCase):
    def test_schema_version_instance(self) -> None:
        self.assertIsInstance(schema.VERSION, Version)
        self.assertTrue(schema.VERSION.current().number())

    def test_has_opt(self) -> None:
        self.assertFalse(schema.hasOpt("nonexistent_opt"))


if __name__ == "__main__":
    unittest.main()
