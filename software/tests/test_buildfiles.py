from __future__ import annotations

import logging
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import scripts.buildfiles as buildfiles
import util.fileutils as fileutils
import util.paths as paths

class TestBuildFiles(unittest.TestCase):
    def testProtocolSwapEmpty(self) -> None:
        self.assertEqual(
            buildfiles.protocolSwap(content="", protocol="http", altprotocol="https"),
            "",
        )
        self.assertEqual(
            buildfiles.protocolSwap(
                content="Defined in http://schema.org and http://bib.schema.org",
                protocol="http",
                altprotocol="ftp",
            ),
            "Defined in ftp://schema.org and ftp://bib.schema.org",
        )

    def testProtocols(self) -> None:
        self.assertEqual(sorted(buildfiles.protocols()), ["http", "https"])

    def testUriWrap(self) -> None:
        self.assertEqual(
            buildfiles.uriwrap("Credential"), "https://schema.org/Credential"
        )
        self.assertEqual(
            buildfiles.uriwrap("https://example.com/Bogus"), "https://example.com/Bogus"
        )
        self.assertEqual(
            buildfiles.uriwrap(["Person", "Thing"]),
            "https://schema.org/Person, https://schema.org/Thing",
        )

    @patch("scripts.buildfiles.paths.DefaultOutputLayout")
    def testWriteCsvOut(self, mock_output_layout) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_output_layout.return_value = paths.OutputLayout(Path(temp_dir))
            buildfiles.writecsvout(
                ftype="properties",
                data=(
                    {"id": "123", "value": "Fnuble"},
                    {"id": "456", "value": "Blubrl"},
                ),
                fields=("id", "value"),
                selector=fileutils.FileSelector.CURRENT,
                protocol="http",
                altprotocol="https",
            )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
