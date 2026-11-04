from __future__ import annotations

import unittest

import SchemaTerms.sdotermsource as sdotermsource
import util.buildocspages as buildocspages


class TestBuildDocs(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        sdotermsource.SdoTermSource.sourceGraph()

    def testJsonldtree(self) -> None:
        buildocspages.jsonldtree(page=None)


if __name__ == "__main__":
    unittest.main()
