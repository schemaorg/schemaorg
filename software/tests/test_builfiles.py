#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import unittest

if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software
import software.util.buildfiles as buildfiles


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



if __name__ == '__main__':
    unittest.main()
