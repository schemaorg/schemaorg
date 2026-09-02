#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Tests to verify that public statistics data files use https:// URLs."""

import datetime
import os
from pathlib import Path
import sys
from typing import List, Tuple
import unittest

if os.getcwd() not in sys.path:
    sys.path.insert(1, os.getcwd())
import software

import util.paths as paths
import util.stats as stats


class PublicStatsDataTests(unittest.TestCase):
    """Tests to verify that public statistics data use https://."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.layout = stats.StatsLayout(paths.DefaultInputLayout())

    def test_stats_csv_use_https(self) -> None:
        """Verify that statistics CSV files use https:// for all terms."""
        failures: List[str] = []
        for provider in self.layout.providers():
            for epoch, file_path in self.layout.epochs(provider, ext="csv").items():
                for row in self.layout._read_csv(file_path):
                    name = row.get("Name", "")
                    if not name.startswith("https://"):
                        failures.append(f" - Provider: {provider}, Epoch: {epoch.strftime("%Y_%m")}")
                        break

        if failures:
            self.fail(f"Statistics CSV data contains non-https URLs in:\n{'\n'.join(failures)}")

    def test_stats_json_use_https(self) -> None:
        """Verify that statistics JSON files use https:// for all terms."""
        failures: List[str] = []
        for provider in self.layout.providers():
            for epoch, file_path in self.layout.epochs(provider, ext="json").items():
                for entry in self.layout._read_json(file_path):
                    name = entry.get("Name", "")
                    if not name.startswith("https://"):
                        failures.append(f" - Provider: {provider}, Epoch: {epoch.strftime("%Y_%m")}")
                        break

        if failures:
            self.fail(f"Statistics JSON data contains non-https URLs in:\n{'\n'.join(failures)}")


if __name__ == "__main__":
    unittest.main()
