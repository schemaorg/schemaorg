#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Import standard python libraries
import sys
import os
import unittest
import logging

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software

import software.SchemaTerms.sdoterm as sdoterm

class SdoTermOrIdTest(unittest.TestCase):

    def testEmpty(self):
        empty = sdoterm.SdoTermOrId()
        self.assertFalse(empty)
        self.assertTrue(empty.expanded)
        self.assertIsNone(empty.id)
        self.assertRaises(sdoterm.UnexpandedTermError, lambda : empty.term)

    def testIdonly(self):
        id_only =sdoterm.SdoTermOrId(term_id='testing')
        self.assertTrue(id_only)
        self.assertFalse(id_only.expanded)
        self.assertEqual(id_only.id, 'testing')
        self.assertRaises(sdoterm.UnexpandedTermError, lambda : id_only.term)

    def testTerm(self):
        term = sdoterm.SdoReference(term_id='testing2', uri='http://example.com/testing2', label='')
        with_term = sdoterm.SdoTermOrId(term=term)
        self.assertTrue(with_term)
        self.assertTrue(with_term.expanded)
        self.assertEqual(with_term.id, 'testing2')
        self.assertEqual(with_term.term, term)

class SdoTermSequenceTest(unittest.TestCase):

    def testEmpty(self):
        empty = sdoterm.SdoTermSequence()
        self.assertFalse(empty)
        self.assertTrue(empty.expanded)
        self.assertEqual(0, len(empty))
        self.assertCountEqual(empty.ids, [])
        self.assertCountEqual(empty.terms, [])

    def testUnexpanded(self):
        unexpanded = sdoterm.SdoTermSequence()
        unexpanded.setIds(['testing3'])
        self.assertTrue(unexpanded)
        self.assertFalse(unexpanded.expanded)
        self.assertEqual(1, len(unexpanded))
        self.assertCountEqual(unexpanded.ids, ['testing3'])
        self.assertRaises(sdoterm.UnexpandedTermError, lambda : unexpanded.terms)

    def testExpanded(self):
        expanded = sdoterm.SdoTermSequence()
        term = sdoterm.SdoReference(term_id='testing4', uri='http://example.com/testing4', label='test')
        expanded.setTerms([term])
        self.assertTrue(expanded)
        self.assertTrue(expanded.expanded)
        self.assertEqual(1, len(expanded))
        self.assertCountEqual(expanded.ids, ['testing4'])
        self.assertCountEqual(expanded.terms, [term])

if __name__ == "__main__":
    unittest.main()
