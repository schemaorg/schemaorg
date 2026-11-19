from __future__ import annotations

import logging
from pathlib import Path
import sys
import tempfile
import textwrap
import unittest

from schemaorg.progress import LogProgressReporter, NullProgressReporter
from schemaorg.tasks.run_unit_tests import RunUnitTestsTask


class TestRunUnitTestsTask(unittest.TestCase):
    def setUp(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.tests_dir = Path(temp_dir.name)
        self.addCleanup(
            lambda: [
                sys.modules.pop(m, None)
                for m in ("test_sample_ok", "test_sample_graphs")
            ]
        )

        (self.tests_dir / "test_sample_ok.py").write_text(
            textwrap.dedent("""\
                import unittest
                class SampleOkTests(unittest.TestCase):
                    def test_pass(self) -> None:
                        self.assertEqual(1 + 1, 2)
                    def test_fail(self) -> None:
                        self.assertEqual(1, 2)
            """),
            encoding="utf-8",
        )
        (self.tests_dir / "test_sample_graphs.py").write_text(
            textwrap.dedent("""\
                import unittest
                class SampleGraphsTests(unittest.TestCase):
                    def test_graph_check(self) -> None:
                        self.assertTrue(True)
            """),
            encoding="utf-8",
        )

    def test_runs_all_tests_and_reports_failures(self) -> None:
        logger = logging.getLogger("test.run_unit_tests")
        reporter = LogProgressReporter(logger=logger, log_steps=True)
        with self.assertLogs(logger, level=logging.INFO) as captured:
            summary = RunUnitTestsTask(
                tests_dir=self.tests_dir,
                skip_basics=False,
                progress=reporter,
            ).run()

        self.assertEqual(summary.total_run, 3)
        self.assertEqual(summary.failure_count, 1)
        self.assertEqual(summary.error_count, 0)
        self.assertFalse(summary.ok)
        self.assertIn("(3/3 tests)", "\n".join(captured.output))

    def test_skip_basics_runs_only_graphs_pattern(self) -> None:
        summary = RunUnitTestsTask(
            tests_dir=self.tests_dir,
            skip_basics=True,
            progress=NullProgressReporter(),
        ).run()
        self.assertEqual(summary.total_run, 1)
        self.assertTrue(summary.ok)


if __name__ == "__main__":
    unittest.main()
