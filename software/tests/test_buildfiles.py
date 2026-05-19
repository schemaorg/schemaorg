#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import sys
import tempfile
import unittest
import unittest.mock

import software

import scripts.buildfiles as buildfiles
import util.fileutils as fileutils
import util.schema as schema
import util.textutils as textutils

class TestBuildFiles(unittest.TestCase):
    def testProtocolSwapEmpty(self):
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

    def testProtocols(self):
        self.assertEqual(sorted(buildfiles.protocols()), ["http", "https"])

    def testArrayToStr(self):
        self.assertEqual(textutils.Array2String([]), "")
        self.assertEqual(textutils.Array2String(["one"]), "one")
        self.assertEqual(
            textutils.Array2String(["one", "two", "three"]), "one, two, three"
        )

    def testUriWrap(self):
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

    @unittest.mock.patch("util.schema.getOutputDir")
    def testWriteCsvOut(self, mock_output_dir):
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_output_dir.return_value = temp_dir
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
