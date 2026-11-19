"""Floating task that discovers and runs the schema.org unittest suite."""

from __future__ import annotations

from dataclasses import dataclass
import logging
from pathlib import Path
from typing import Any
import unittest

from schemaorg.progress import ProgressReporter, TaskProgress


@dataclass(frozen=True)
class TestSuiteSummary:
    """Structured summary returned by RunUnitTestsTask."""

    total_run: int
    failure_count: int
    error_count: int
    skipped_count: int
    expected_failure_count: int
    unexpected_success_count: int
    failures: tuple[tuple[str, str], ...]
    errors: tuple[tuple[str, str], ...]

    @property
    def ok(self) -> bool:
        return (
            self.failure_count == 0
            and self.error_count == 0
            and self.unexpected_success_count == 0
        )


class _ProgressTestResult(unittest.TestResult):
    """Forwards per-test progress and failure tracebacks to TaskProgress."""

    def __init__(self, progress: TaskProgress) -> None:
        super().__init__()
        self._progress = progress

    def startTest(self, test: unittest.TestCase) -> None:
        super().startTest(test)
        self._progress.step(test.id())

    def stopTest(self, test: unittest.TestCase) -> None:
        super().stopTest(test)
        self._progress.advance(1)

    def addError(self, test: unittest.TestCase, err: Any) -> None:
        super().addError(test, err)
        _, traceback_str = self.errors[-1]
        self._progress.log(f"ERROR in {test.id()}:\n{traceback_str}", logging.ERROR)

    def addFailure(self, test: unittest.TestCase, err: Any) -> None:
        super().addFailure(test, err)
        _, traceback_str = self.failures[-1]
        self._progress.log(f"FAIL in {test.id()}:\n{traceback_str}", logging.ERROR)

    def addUnexpectedSuccess(self, test: unittest.TestCase) -> None:
        super().addUnexpectedSuccess(test)
        self._progress.log(
            f"UNEXPECTED SUCCESS in {test.id()}", logging.ERROR
        )


class RunUnitTestsTask:
    """Discovers and executes unittest cases in a given directory."""

    def __init__(
        self,
        tests_dir: Path,
        skip_basics: bool,
        progress: ProgressReporter,
    ) -> None:
        self.tests_dir: Path = tests_dir
        self.skip_basics: bool = skip_basics
        self.progress: ProgressReporter = progress

    def run(self) -> TestSuiteSummary:
        pattern = "*graphs*.py" if self.skip_basics else "test*.py"
        # Pass top_level_dir=tests_dir so two distinct tests_dir paths in one
        # process do not collide unless module basenames overlap.
        suite = unittest.loader.TestLoader().discover(
            start_dir=str(self.tests_dir),
            pattern=pattern,
            top_level_dir=str(self.tests_dir),
        )
        total = suite.countTestCases()

        with self.progress.task(
            "Running unit tests",
            total=total,
            unit="tests",
        ) as p:
            result = _ProgressTestResult(p)
            result.startTestRun()
            try:
                suite.run(result)
            finally:
                result.stopTestRun()

        return TestSuiteSummary(
            total_run=result.testsRun,
            failure_count=len(result.failures),
            error_count=len(result.errors),
            skipped_count=len(result.skipped),
            expected_failure_count=len(result.expectedFailures),
            unexpected_success_count=len(result.unexpectedSuccesses),
            failures=tuple((t.id(), tb) for t, tb in result.failures),
            errors=tuple((t.id(), tb) for t, tb in result.errors),
        )
