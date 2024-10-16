#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import unittest
import unittest.mock
import tempfile
import logging

if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software
import software.util.buildfiles as buildfiles
import software.util.fileutils as fileutils
import software.util.schemaglobals as schemaglobals


class TestBuildFiles(unittest.TestCase):

    def testProtocolSwapEmpty(self):
        self.assertEqual(buildfiles.protocolSwap(
            content='', protocol='http', altprotocol='https'),
            '')
        self.assertEqual(buildfiles.protocolSwap(
            content='Defined in http://schema.org and http://bib.schema.org',
            protocol='http', altprotocol='ftp'),
            'Defined in ftp://schema.org and ftp://bib.schema.org')

    def testProtocols(self):
        self.assertEqual(sorted(buildfiles.protocols()), ['http', 'https'])

    def testArrayToStr(self):
        self.assertEqual(buildfiles.array2str([]), '')
        self.assertEqual(buildfiles.array2str(['one']), 'one')
        self.assertEqual(buildfiles.array2str(['one', 'two', 'three']), 'one, two, three')

    def testUriWrap(self):
        self.assertEqual(
            buildfiles.uriwrap('Credential'),
            'https://schema.org/Credential')
        self.assertEqual(
            buildfiles.uriwrap('https://example.com/Bogus'),
            'https://example.com/Bogus')
        self.assertEqual(
            buildfiles.uriwrap(['Person', 'Thing']),
            'https://schema.org/Person, https://schema.org/Thing')

    @unittest.mock.patch('software.util.schemaglobals.getOutputDir')
    def testWriteCsvOut(self, mock_output_dir):
        with tempfile.TemporaryDirectory() as temp_dir:
            mock_output_dir.return_value = temp_dir
            buildfiles.writecsvout(
                ftype='properties',
                data=({'id': '123', 'value': 'Fnuble'}, {'id': '456', 'value': 'Blubrl'}),
                fields=('id', 'value'),
                selector=fileutils.FileSelector.CURRENT,
                protocol='http', altprotocol='https')


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    unittest.main()
