#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import difflib
import logging
import os
import sys
import sys
import tempfile
import unittest

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software.util.snapshot_schema as snapshot_schema


FAIL_HELP = "\n [See fix here] Re-generate the snapshot file by running the 'software/util/snapshot_schema.py'-file."

class SnapshotTest(unittest.TestCase):
    @unittest.skip("skip snapshot tests until branch updates / pr actions are correctly set up")
    def test_snapshot_matches(self):
        # loads the software/tests/snapshot/schemaorg-all-https.ttl file
        snapshot_file = os.path.join(
            os.path.dirname(__file__), "snapshot/schemaorg-all-https.ttl"
        )
        with open(snapshot_file, "r", encoding="utf-8") as f:
            snapshot_content_lines = f.readlines()

        with tempfile.TemporaryDirectory() as temp_dir:
            # builds all terms again from scratch by calling the snapshot_ttl function directly
            snapshot_schema.snapshot_ttl(temp_dir)
            generated_file = os.path.join(temp_dir, "schemaorg-all-https.ttl")
            with open(generated_file, "r", encoding="utf-8") as f:
                generated_content_lines = f.readlines()

        # compares the two files.
        if snapshot_content_lines != generated_content_lines:
            diff = difflib.unified_diff(
                snapshot_content_lines,
                generated_content_lines,
                fromfile=snapshot_file,
                tofile=generated_file,
            )
            self.fail(
                "Generated schema does not match snapshot:\n"
                + "".join(diff)
                + FAIL_HELP
            )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
