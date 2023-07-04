#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import itertools
import os
import sys
import unittest
import tempfile

for path in [os.getcwd(), "software/util"]:
  sys.path.insert(1, path) #Pickup libs from local directories

import textutils

class TestStripHtmlTags(unittest.TestCase):
  """Test for the `StripHtmlTags` function."""

  def testEmpty(self):
    """Test processing empty input."""
    self.assertEqual(
        textutils.StripHtmlTags(''), '')

  def testTag(self):
    """Test processing input with tags."""
    self.assertEqual(
        textutils.StripHtmlTags('<strong>Yay!</strong>'),
        'Yay!')

  def testNoTag(self):
    """Test processign input with no tag."""
    self.assertEqual(
        textutils.StripHtmlTags('今日は'), '今日は')

SENTENCE = 'The quick brown fox jumps over the lazy dog.'

class TestShortenOnSentence(unittest.TestCase):

  def setUp(self):
    self.text = ' '.join(itertools.repeat(SENTENCE, 10))

  def testEmpty(self):
    self.assertEqual(
      textutils.ShortenOnSentence(''),
      '')

  def testNoCut(self):
    self.assertEqual(
      textutils.ShortenOnSentence(self.text, lengthHint=1000),
      self.text
    )

  def testCuts(self):
    self.assertEqual(
      textutils.ShortenOnSentence(self.text, lengthHint=10),
      'The quick brown fox jumps over the lazy dog...'
    )

if __name__ == '__main__':
    unittest.main()