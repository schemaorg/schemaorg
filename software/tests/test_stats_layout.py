#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Unit tests for schemaorg.layout.stats_layout."""

import datetime
import json
from pathlib import Path
import tempfile
import unittest

from schemaorg.layout.domain import Domain
from schemaorg.layout.input_layout import InputLayout
from schemaorg.layout.stats_layout import StatsLayout, StatsProvider
import util.stats as legacy_stats


class TestStatsLayout(unittest.TestCase):
    """Test suite for StatsLayout."""

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.input_layout = InputLayout(self.root)
        self.stats_dir = self.input_layout.dir(Domain.PUBLIC_STATS)
        self.layout = StatsLayout(self.input_layout)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_providers_nonexistent_dir(self):
        self.assertEqual(self.layout.providers(), [])

    def test_providers_discovery(self):
        self.stats_dir.mkdir(parents=True, exist_ok=True)
        (self.stats_dir / "google").mkdir()
        (self.stats_dir / "bing").mkdir()
        (self.stats_dir / ".git").mkdir()
        (self.stats_dir / "README.md").touch()

        self.assertEqual(self.layout.providers(), ["bing", "google"])

    def test_list_files(self):
        self.assertEqual(self.layout._list_files("nonexistent"), [])

        provider_dir = self.stats_dir / "google"
        provider_dir.mkdir(parents=True, exist_ok=True)
        f_json = provider_dir / "stats_2026_01.json"
        f_csv = provider_dir / "stats_2026_01.csv"
        f_sub = provider_dir / "subdir"
        f_json.touch()
        f_csv.touch()
        f_sub.mkdir()

        self.assertEqual(self.layout._list_files("google"), [f_csv, f_json])
        self.assertEqual(self.layout._list_files("google", ext="json"), [f_json])
        self.assertEqual(self.layout._list_files("google", ext="csv"), [f_csv])

    def test_epochs(self):
        provider_dir = self.stats_dir / "google"
        provider_dir.mkdir(parents=True, exist_ok=True)
        f1 = provider_dir / "stats_2025_12.json"
        f2 = provider_dir / "stats_2026_01.json"
        f_summary = provider_dir / "summary_2026_01.json"
        f_invalid = provider_dir / "random.json"
        f1.touch()
        f2.touch()
        f_summary.touch()
        f_invalid.touch()

        epochs = self.layout.epochs("google")
        self.assertEqual(
            epochs,
            {
                datetime.datetime(2025, 12, 1): f1,
                datetime.datetime(2026, 1, 1): f2,
            },
        )

    def test_read_json_and_csv(self):
        provider_dir = self.stats_dir / "google"
        provider_dir.mkdir(parents=True, exist_ok=True)

        json_file = provider_dir / "data.json"
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump([{"key": "value"}], f)
        self.assertEqual(self.layout._read_json(json_file), [{"key": "value"}])

        csv_file = provider_dir / "data.csv"
        with open(csv_file, "w", encoding="utf-8") as f:
            f.write(" Name , Value \nhttps://schema.org/Thing,high\n")
        self.assertEqual(
            self.layout._read_csv(csv_file),
            [{"Name": "https://schema.org/Thing", "Value": "high"}],
        )

    def test_get_stats(self):
        google_dir = self.stats_dir / "google"
        google_dir.mkdir(parents=True, exist_ok=True)
        old_json = google_dir / "stats_2025_12.json"
        new_json = google_dir / "stats_2026_01.json"

        with open(old_json, "w", encoding="utf-8") as f:
            json.dump([{"Name": "OldThing", "Domain Bucket": "low"}], f)
        with open(new_json, "w", encoding="utf-8") as f:
            json.dump(
                [
                    {"Name": "Thing", "Domain Bucket": "high"},
                    {"Name": "Event", "Domain Bucket": "medium"},
                ],
                f,
            )

        empty_dir = self.stats_dir / "empty"
        empty_dir.mkdir(parents=True, exist_ok=True)

        stats = self.layout.get_stats()
        self.assertEqual(len(stats), 1)
        self.assertIsInstance(stats[0], StatsProvider)
        self.assertEqual(stats[0].provider_id, "google")
        self.assertEqual(stats[0].name, "Google")
        self.assertEqual(
            stats[0].description,
            "Based on monthly aggregations from Google's web index.",
        )
        self.assertEqual(stats[0].date, "January 2026")
        self.assertEqual(
            stats[0].stats_map,
            {"Thing": "high", "Event": "medium"},
        )

        filtered = self.layout.get_stats(providers=["empty"])
        self.assertEqual(filtered, [])

    def test_backward_compatibility_reexports(self):
        self.assertIs(legacy_stats.StatsLayout, StatsLayout)
        self.assertIs(legacy_stats.StatsProvider, StatsProvider)
        self.assertTrue(callable(legacy_stats.get_stats_providers))


if __name__ == "__main__":
    unittest.main()
