from __future__ import annotations

import unittest

import SchemaTerms.sdoterm as sdoterm


class SdoTermOrIdTest(unittest.TestCase):
    def testEmpty(self) -> None:
        empty = sdoterm.SdoTermOrId()
        self.assertFalse(empty)
        self.assertTrue(empty.expanded)
        self.assertIsNone(empty.id)
        with self.assertRaises(sdoterm.UnexpandedTermError):
            _ = empty.term

    def testIdonly(self) -> None:
        id_only = sdoterm.SdoTermOrId(term_id="testing")
        self.assertTrue(id_only)
        self.assertFalse(id_only.expanded)
        self.assertEqual(id_only.id, "testing")
        with self.assertRaises(sdoterm.UnexpandedTermError):
            _ = id_only.term

    def testTerm(self) -> None:
        term = sdoterm.SdoReference(
            term_id="testing2", uri="http://example.com/testing2", label=""
        )
        with_term = sdoterm.SdoTermOrId(term=term)
        self.assertTrue(with_term)
        self.assertTrue(with_term.expanded)
        self.assertEqual(with_term.id, "testing2")
        self.assertEqual(with_term.term, term)

    def testSetIdAndSetTermInvalidateState(self) -> None:
        term = sdoterm.SdoReference(
            term_id="testing2", uri="http://example.com/testing2", label=""
        )
        holder = sdoterm.SdoTermOrId(term=term)
        holder.setId("other")
        self.assertEqual(holder.id, "other")
        self.assertFalse(holder.expanded)
        with self.assertRaises(sdoterm.UnexpandedTermError):
            _ = holder.term

        holder.setTerm(None)
        self.assertFalse(holder)
        self.assertIsNone(holder.id)
        self.assertTrue(holder.expanded)


class SdoTermSequenceTest(unittest.TestCase):
    def testEmpty(self) -> None:
        empty = sdoterm.SdoTermSequence()
        self.assertFalse(empty)
        self.assertTrue(empty.expanded)
        self.assertEqual(0, len(empty))
        self.assertCountEqual(empty.ids, [])
        self.assertCountEqual(empty.terms, [])

    def testUnexpanded(self) -> None:
        unexpanded = sdoterm.SdoTermSequence()
        unexpanded.setIds(["testing3"])
        self.assertTrue(unexpanded)
        self.assertFalse(unexpanded.expanded)
        self.assertEqual(1, len(unexpanded))
        self.assertCountEqual(unexpanded.ids, ["testing3"])
        with self.assertRaises(sdoterm.UnexpandedTermError):
            _ = unexpanded.terms

    def testExpanded(self) -> None:
        expanded = sdoterm.SdoTermSequence()
        term = sdoterm.SdoReference(
            term_id="testing4", uri="http://example.com/testing4", label="test"
        )
        expanded.setTerms([term])
        self.assertTrue(expanded)
        self.assertTrue(expanded.expanded)
        self.assertEqual(1, len(expanded))
        self.assertCountEqual(expanded.ids, ["testing4"])
        self.assertCountEqual(expanded.terms, [term])


if __name__ == "__main__":
    unittest.main()
