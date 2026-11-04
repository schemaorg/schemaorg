from __future__ import annotations

import itertools
import unittest

import util.textutils as textutils

SENTENCE = "The quick brown fox jumps over the lazy dog."


class TestStripHtmlTags(unittest.TestCase):
    def testEmpty(self) -> None:
        self.assertEqual(textutils.StripHtmlTags(""), "")

    def testTag(self) -> None:
        self.assertEqual(textutils.StripHtmlTags("<strong>Yay!</strong>"), "Yay!")

    def testNoTag(self) -> None:
        self.assertEqual(textutils.StripHtmlTags("今日は"), "今日は")


class TestShortenOnSentence(unittest.TestCase):
    def setUp(self) -> None:
        self.text = " ".join(itertools.repeat(SENTENCE, 10))

    def testEmpty(self) -> None:
        self.assertEqual(textutils.ShortenOnSentence(""), "")

    def testNoCut(self) -> None:
        self.assertEqual(
            textutils.ShortenOnSentence(self.text, lengthHint=1000), self.text
        )

    def testCuts(self) -> None:
        self.assertEqual(
            textutils.ShortenOnSentence(self.text, lengthHint=10),
            "The quick brown fox jumps over the lazy dog...",
        )

    def testStripsWhitespaceBeforeLengthCheck(self) -> None:
        self.assertEqual(
            textutils.ShortenOnSentence(f"{' ' * 30}{SENTENCE}  ", lengthHint=50),
            SENTENCE,
        )


if __name__ == "__main__":
    unittest.main()
