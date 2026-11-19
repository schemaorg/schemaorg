from __future__ import annotations

import logging
import unittest

from schemaorg.progress import LogProgressReporter, NullProgressReporter


class TestProgressReporter(unittest.TestCase):
    def test_null_progress_reporter_is_silent(self) -> None:
        reporter = NullProgressReporter()
        with reporter.task("Quiet work", total=2, unit="items") as p:
            p.step("first")
            p.advance(1)
            p.log("ignored", logging.INFO)
            p.advance(1)

    def test_log_progress_reporter_emits_block_and_steps(self) -> None:
        logger = logging.getLogger("test.progress")
        reporter = LogProgressReporter(logger=logger, log_steps=True)
        with self.assertLogs(logger, level=logging.INFO) as captured:
            with reporter.task("Exporting", total=2, unit="files") as p:
                p.step("a.ttl")
                p.advance(1)
                p.step("b.ttl")
                p.advance(1)
                p.log("extra detail", logging.WARNING)

        joined = "\n".join(captured.output)
        self.assertIn("Start: Exporting", joined)
        self.assertIn("Exporting: a.ttl", joined)
        self.assertIn("Exporting: b.ttl", joined)
        self.assertIn("WARNING:test.progress:extra detail", joined)
        self.assertIn("Done: Exporting (2/2 files)", joined)


if __name__ == "__main__":
    unittest.main()
