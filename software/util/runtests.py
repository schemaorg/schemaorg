#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# Note: if this stops working in OSX, consider "sudo pip uninstall protobuf"
# to remove a 2nd clashing google/ python lib. See
# https://github.com/coto/gae-boilerplate/issues/306

# This script runs the Schema.org unit tests. The basic tests are concerned
# with our site infrastructure; loading and accessing data.  The graph tests
# are concerned with the shape/size of the schema graph itself.

# Currently this means they require Google AppEngine to be installed,
# because api.py and sdoapp.py both  depend upon AppEngine. This is
# something we should minimise - eventually only
# sdoapp.py should need AppEngine.  We use W3C SPARQL for the graph tests,
# and therefore these tests will only run  if 'rdflib' is installed.
#
# We do not currently test the generated Web site with unit tests. However
# please see /docs/qa.html for some useful links to check whenever site UI
# code is being changed.
#
# There are two dependencies:
#
# 1. AppEngine SDK
# Typically in ~/google_cloud_sdk and/or linked from /usr/local/google_appengine
# This script will do its best to update your python path to point to
# the SDK (whether you point to it directly or the broader Cloud SDK), to
# AppEngine's tools and libs and to other bundled libraries. But to bootstrap
# this is needs to at least find dev_appserver.
#
# 2. rdflib
#
# A normal Python package. Take care that it is installed against the version of
# Python that is being used to run this script. easy_install or pip should work.
# We may later bundle this, see
# https://github.com/schemaorg/schemaorg/issues/178
#
# script originally based on original in google appengine dist and shared
# under same terms,
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

import argparse
import sys
import colorama
import os
import unittest
import typing
from typing import Any, Dict, List, Optional, Tuple, Union, Iterable, Sequence, Set, Callable, Type, IO


SITEDIR: str = "software/site"
STANDALONE: bool = False


class ColoredTestResult(unittest.TextTestResult):
    """Color the test results."""

    def __init__(self, stream: IO[Any], descriptions: bool, verbosity: int) -> None:
        super().__init__(stream, descriptions, verbosity)
        self.is_tty: bool
        try:
            self.is_tty = os.isatty(stream.fileno())
        except Exception:
            self.is_tty = False
        self.separator1: str = ""
        self.separator2: str = ""
        if self.is_tty:
            try:
                columns: int = os.get_terminal_size().columns
            except Exception:
                columns = 80
            self.separator1 = "▼" * columns
            self.separator2 = "▲" * columns

    def _colorPrint(self, message: str, color: Optional[str] = None, short: Optional[str] = None, newline: bool = True) -> None:
        if not self.showAll and short:
            message = short
        if self.is_tty and color:
            message = color + message + colorama.Fore.WHITE + colorama.Style.NORMAL
        if newline:
            self.stream.writeln(message)
        else:
            self.stream.write(message)
            self.stream.flush()

    def addError(self, test: unittest.TestCase, err: Any) -> None:
        super(ColoredTestResult, self).addError(test, err)  # Include the 'err' argument
        self._colorPrint("Error", color=colorama.Fore.YELLOW, short="E")

    def startTest(self, test: unittest.TestCase) -> None:
        super(unittest.TextTestResult, self).startTest(test)
        lines: List[str] = self.getDescription(test).split("\n")
        for index, line in enumerate(lines):
            color: Optional[str] = None
            if index > 0:
                color = colorama.Fore.LIGHTWHITE_EX
            lastline: bool = index == len(lines) - 1
            if lastline:
                self._colorPrint(line + " … ", color=color, newline=False)
            else:
                self._colorPrint(line, color=color, newline=True)

    def addSuccess(self, test: unittest.TestCase) -> None:
        super(unittest.TextTestResult, self).addSuccess(test)
        self._colorPrint("OK", color=colorama.Fore.GREEN, short=".")

    def addFailure(self, test: unittest.TestCase, err: Any) -> None:
        super(unittest.TextTestResult, self).addFailure(test, err)
        self._colorPrint("FAIL", color=colorama.Fore.RED, short="F")

    def addExpectedFailure(self, test: unittest.TestCase, err: Any) -> None:
        super(unittest.TextTestResult, self).addExpectedFailure(test, err)
        self._colorPrint("Expected failure", color=colorama.Fore.GREEN, short="x")

    def addUnexpectedSuccess(self, test: unittest.TestCase) -> None:
        super(unittest.TextTestResult, self).addUnexpectedSuccess(test)
        self._colorPrint("Unexpected success", color=colorama.Fore.RED, short="U")

    def addSkip(self, test: unittest.TestCase, reason: str) -> None:
        super(unittest.TextTestResult, self).addSkip(test, reason)
        self._colorPrint("Skipped", color=colorama.Fore.CYAN, short="S")
        if reason:
            self._colorPrint(reason, color=colorama.Fore.LIGHTCYAN_EX)

    def printErrorList(self, flavour: str, errors: List[Tuple[unittest.TestCase, str]]) -> None:
        # super(unittest.TextTestResult, self).addSkip(flavour, errors)
        color: Optional[str] = None
        if flavour == "ERROR":
            color = colorama.Fore.YELLOW
        elif flavour == "FAIL":
            color = colorama.Fore.LIGHTRED_EX
        for test, err in errors:
            self._colorPrint(self.separator1)
            self._colorPrint(self.getDescription(test), color=color)
            self._colorPrint(self.separator2)
            self._colorPrint("%s" % err, color=color)


def GetSuite(test_path: str, args: Optional[argparse.Namespace]) -> unittest.TestSuite:
    suite: unittest.TestSuite
    if args and vars(args)["skipbasics"]:
        suite = unittest.loader.TestLoader().discover(test_path, pattern="*graphs*.py")
    else:
        suite = unittest.loader.TestLoader().discover(test_path, pattern="test*.py")
    return suite


# TODO:
# Ensure that the google.appengine.* packages are available
# in tests as well as all bundled third-party packages.
def main(test_path: str, args: Optional[argparse.Namespace] = None) -> int:
    runner: unittest.TextTestRunner = unittest.TextTestRunner(
        verbosity=2, descriptions=True, resultclass=ColoredTestResult
    )
    suite: unittest.TestSuite = GetSuite(test_path, args)
    res: unittest.TestResult = runner.run(suite)
    count: int = len(res.failures) + len(res.errors)
    return count


if __name__ == "__main__":
    colorama.init()
    parser: argparse.ArgumentParser = argparse.ArgumentParser(description="Configurable testing of schema.org.")
    parser.add_argument("--skipbasics", action="store_true", help="Skip basic tests.")
    args_parsed: argparse.Namespace = parser.parse_args()
    sys.exit(main("./software/tests/", args_parsed))

# alternative, try
# PYTHONPATH=/usr/local/google_appengine ./scripts/run_tests.py
