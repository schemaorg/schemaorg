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
# We may later bundle this, see https://github.com/schemaorg/schemaorg/issues/178
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
import optparse
import sys
import colorama
import os
import unittest
import io

SITEDIR = "software/site"
STANDALONE = False


class ColoredTestResult(unittest.TextTestResult):
    """Color the test results."""

    def __init__(self, stream, descriptions, verbosity):
        super().__init__(stream, descriptions, verbosity)
        try:
            self.is_tty = os.isatty(stream.fileno())
        except:
            self.is_tty = False
        if self.is_tty:
            try:
                columns = os.get_terminal_size().columns
            except:
                columns = 80
            self.separator1 = "▼" * columns
            self.separator2 = "▲" * columns

    def _colorPrint(self, message, color=None, short=None, newline=True):
        if not self.showAll and short:
            message = short
        if self.is_tty and color:
            message = color + message + colorama.Fore.WHITE + colorama.Style.NORMAL
        if newline:
            self.stream.writeln(message)
        else:
            self.stream.write(message)
            self.stream.flush()

    def addError(self, test, err):
        super(ColoredTestResult, self).addError(test, err)  # Include the 'err' argument
        self._colorPrint("Error", color=colorama.Fore.YELLOW, short="E")

    def startTest(self, test):
        super(unittest.TextTestResult, self).startTest(test)
        lines = self.getDescription(test).split("\n")
        for index, line in enumerate(lines):
            color = None
            if index > 0:
                color = colorama.Fore.LIGHTWHITE_EX
            lastline = index == len(lines) - 1
            if lastline:
                self._colorPrint(line + " … ", color=color, newline=False)
            else:
                self._colorPrint(line, color=color, newline=True)

    def addSuccess(self, test):
        super(unittest.TextTestResult, self).addSuccess(test)
        self._colorPrint("OK", color=colorama.Fore.GREEN, short=".")

    def addFailure(self, test, err):
        super(unittest.TextTestResult, self).addFailure(test, err)
        self._colorPrint("FAIL", color=colorama.Fore.RED, short="F")

    def addExpectedFailure(self, test, err):
        super(unittest.TextTestResult, self).addExpectedFailure(test, err)
        self._colorPrint("Expected failure", color=colorama.Fore.GREEN, short="x")

    def addUnexpectedSuccess(self, test):
        super(unittest.TextTestResult, self).addUnexpectedSuccess(test)
        self._colorPrint("Unexpected success", color=colorama.Fore.RED, short="U")

    def addSkip(self, test, reason):
        super(unittest.TextTestResult, self).addSkip(test, reason)
        self._colorPrint("Skipped", color=colorama.Fore.CYAN, short="S")
        if reason:
            self._colorPrint(reason, color=colorama.Fore.LIGHTCYAN_EX)

    def printErrorList(self, flavour, errors):
        super(unittest.TextTestResult, self).addSkip(flavour, errors)
        color = None
        if flavour == "ERROR":
            color = colorama.Fore.YELLOW
        elif flavour == "FAIL":
            color = colorama.Fore.LIGHTRED_EX
        for test, err in errors:
            self._colorPrint(self.separator1)
            self._colorPrint(self.getDescription(test), color=color)
            self._colorPrint(self.separator2)
            self._colorPrint("%s" % err, color=color)


def GetSuite(test_path, args):
    if args and vars(args)["skipbasics"]:
        suite = unittest.loader.TestLoader().discover(test_path, pattern="*graphs*.py")
    else:
        suite = unittest.loader.TestLoader().discover(test_path, pattern="test*.py")
    return suite


# TODO:
# Ensure that the google.appengine.* packages are available
# in tests as well as all bundled third-party packages.
def main(test_path, args=None):
    runner = unittest.TextTestRunner(
        verbosity=2, descriptions=True, resultclass=ColoredTestResult
    )
    suite = GetSuite(test_path, args)
    res = runner.run(suite)
    count = len(res.failures) + len(res.errors)
    return count


if __name__ == "__main__":
    colorama.init()
    parser = argparse.ArgumentParser(description="Configurable testing of schema.org.")
    parser.add_argument("--skipbasics", action="store_true", help="Skip basic tests.")
    args = parser.parse_args()
    sys.exit(main("./software/tests/", args))

# alternative, try
# PYTHONPATH=/usr/local/google_appengine ./scripts/run_tests.py
