#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import unittest

import software


class BasicFileTests(unittest.TestCase):
    """Basic tests for file level integrity."""

    def testNoHttpExamples(self):
        """Test that no examples contain url of the http://schema.org (they should be https)."""
        httpexamplescheck = (
            "grep -l 'http://schema.org' data/*examples.txt data/ext/*/*examples.txt"
        )
        out = ""
        try:
            out = subprocess.check_output(httpexamplescheck, shell=True)
            if out:
                self.fail(
                    "Examples file(s) found containing 'http://schema.org':\n%s\n"
                    "Replace with 'https://schema.org and rerun."
                )
        except:
            pass
