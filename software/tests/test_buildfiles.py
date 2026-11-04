from __future__ import annotations

import logging
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from schemaorg.layout import OutputLayout, Protocol, Releases, Scope
import scripts.buildfiles as buildfiles
import util.fileutils as fileutils
import util.schema as schema


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
            output_layout = OutputLayout(Path(temp_dir))
            mock_output_layout.return_value = output_layout
            buildfiles.writecsvout(
                ftype="properties",
                data=(
                    {"id": "123", "value": "http://schema.org/Fnuble"},
                    {"id": "456", "value": "Blubrl"},
                ),
                fields=("id", "value"),
                selector=fileutils.FileSelector.CURRENT,
                protocol="http",
                altprotocol="https",
            )

            releases = Releases(output_layout, schema.VERSION)
            http_csv = releases.file(
                protocol=Protocol.HTTP,
                scope=Scope.CURRENT,
                extension="-properties.csv",
            )
            https_csv = releases.file(
                protocol=Protocol.HTTPS,
                scope=Scope.CURRENT,
                extension="-properties.csv",
            )
            self.assertEqual(
                http_csv.read_text(encoding="utf-8"),
                '"id","value"\n"123","http://schema.org/Fnuble"\n"456","Blubrl"\n',
            )
            self.assertEqual(
                https_csv.read_text(encoding="utf-8"),
                '"id","value"\n"123","https://schema.org/Fnuble"\n"456","Blubrl"\n',
            )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
