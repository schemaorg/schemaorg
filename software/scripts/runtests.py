#!/usr/bin/env python3
"""Runs the Schema.org unit test suite."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import os
import shutil
import sys
from typing import Any, IO
import unittest

import colorama

from schemaorg import constants


class ColoredTestResult(unittest.TextTestResult):
    """Color the test results."""

    def __init__(self, stream: IO[Any], descriptions: bool, verbosity: int) -> None:
        super().__init__(stream, descriptions, verbosity)
        try:
            self.is_tty = os.isatty(stream.fileno())
        except Exception:
            self.is_tty = False
        self.separator1: str = ""
        self.separator2: str = ""
        if self.is_tty:
            columns = shutil.get_terminal_size().columns
            self.separator1 = "▼" * columns
            self.separator2 = "▲" * columns

    def _colorPrint(
        self,
        message: str,
        color: str | None = None,
        short: str | None = None,
        newline: bool = True,
    ) -> None:
        if not self.showAll and short:
            message = short
        if self.is_tty and color:
            message = f"{color}{message}{colorama.Style.RESET_ALL}"
        if newline:
            self.stream.writeln(message)
        else:
            self.stream.write(message)
            self.stream.flush()

    def startTest(self, test: unittest.TestCase) -> None:
        unittest.TestResult.startTest(self, test)
        lines = self.getDescription(test).split("\n")
        for index, line in enumerate(lines):
            color = colorama.Fore.LIGHTWHITE_EX if index > 0 else None
            if index == len(lines) - 1:
                self._colorPrint(f"{line} … ", color=color, newline=False)
            else:
                self._colorPrint(line, color=color, newline=True)

    def addError(self, test: unittest.TestCase, err: Any) -> None:
        unittest.TestResult.addError(self, test, err)
        self._colorPrint("Error", color=colorama.Fore.YELLOW, short="E")

    def addSuccess(self, test: unittest.TestCase) -> None:
        unittest.TestResult.addSuccess(self, test)
        self._colorPrint("OK", color=colorama.Fore.GREEN, short=".")

    def addFailure(self, test: unittest.TestCase, err: Any) -> None:
        unittest.TestResult.addFailure(self, test, err)
        self._colorPrint("FAIL", color=colorama.Fore.RED, short="F")

    def addExpectedFailure(self, test: unittest.TestCase, err: Any) -> None:
        unittest.TestResult.addExpectedFailure(self, test, err)
        self._colorPrint("Expected failure", color=colorama.Fore.GREEN, short="x")

    def addUnexpectedSuccess(self, test: unittest.TestCase) -> None:
        unittest.TestResult.addUnexpectedSuccess(self, test)
        self._colorPrint("Unexpected success", color=colorama.Fore.RED, short="U")

    def addSkip(self, test: unittest.TestCase, reason: str) -> None:
        unittest.TestResult.addSkip(self, test, reason)
        self._colorPrint("Skipped", color=colorama.Fore.CYAN, short="S")
        if reason:
            self._colorPrint(reason, color=colorama.Fore.LIGHTCYAN_EX)

    def printErrorList(
        self, flavour: str, errors: list[tuple[unittest.TestCase, str]]
    ) -> None:
        color: str | None = None
        if flavour == "ERROR":
            color = colorama.Fore.YELLOW
        elif flavour == "FAIL":
            color = colorama.Fore.LIGHTRED_EX
        for test, err in errors:
            self._colorPrint(self.separator1)
            self._colorPrint(self.getDescription(test), color=color)
            self._colorPrint(self.separator2)
            self._colorPrint(f"{err}", color=color)


def GetSuite(
    test_path: str, args: argparse.Namespace | None
) -> unittest.TestSuite:
    pattern = "*graphs*.py" if args and args.skipbasics else "test*.py"
    return unittest.loader.TestLoader().discover(test_path, pattern=pattern)


def main(
    test_path: str | None = None,
    args: argparse.Namespace | None = None,
    argv: Sequence[str] | None = None,
) -> int:
    if test_path is None:
        test_path = str(constants.PROJECT_ROOT / "software/tests")
    if args is None:
        colorama.init()
        parser = argparse.ArgumentParser(
            description="Configurable testing of schema.org."
        )
        parser.add_argument(
            "--skipbasics", action="store_true", help="Skip basic tests."
        )
        args = parser.parse_args(argv)
    runner = unittest.TextTestRunner(
        verbosity=2, descriptions=True, resultclass=ColoredTestResult
    )
    suite = GetSuite(test_path, args)
    res = runner.run(suite)
    return len(res.failures) + len(res.errors)


if __name__ == "__main__":
    sys.exit(main())
