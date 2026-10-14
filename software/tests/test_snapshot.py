#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import difflib
import logging
from pathlib import Path
import tempfile
import unittest

import scripts.snapshot_schema as snapshot_schema


FAIL_HELP = "\n [See fix here] Re-generate the snapshot file by running the 'software/scripts/snapshot_schema.py'-file."

class SnapshotTest(unittest.TestCase):
    @unittest.skip("skip snapshot tests until branch updates / pr actions are correctly set up")
    def test_snapshot_matches(self):
        # loads the software/tests/snapshot/schemaorg-all-https.ttl file
        snapshot_file = Path(__file__).parent / "snapshot/schemaorg-all-https.ttl"
        snapshot_content_lines = snapshot_file.read_text(encoding="utf-8").splitlines(keepends=True)

        with tempfile.TemporaryDirectory() as temp_dir:
            # builds all terms again from scratch by calling the snapshot_ttl
            # function directly
            snapshot_schema.snapshot_ttl(temp_dir)
            generated_file = Path(temp_dir) / "schemaorg-all-https.ttl"
            generated_content_lines = generated_file.read_text(encoding="utf-8").splitlines(keepends=True)

        # compares the two files.
        if snapshot_content_lines != generated_content_lines:
            diff = difflib.unified_diff(
                snapshot_content_lines,
                generated_content_lines,
                fromfile=str(snapshot_file),
                tofile=str(generated_file),
            )
            self.fail(
                "Generated schema does not match snapshot:\n"
                + "".join(diff)
                + FAIL_HELP
            )


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    unittest.main()
