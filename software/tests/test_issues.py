from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from schemaorg.layout import InputLayout, Issues


class TestIssues(unittest.TestCase):
    def setUp(self) -> None:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        self.root = Path(temp_dir.name)
        self.layout = InputLayout(self.root)
        self.issues = Issues(self.layout)

        data_dir = self.root / "data"
        (data_dir / "ext" / "auto").mkdir(parents=True, exist_ok=True)
        (data_dir / "ext" / "bib").mkdir(parents=True, exist_ok=True)

        self.core_ttl = data_dir / "schema.ttl"
        self.core_examples = data_dir / "sdo-examples.txt"
        self.core_ttl.touch()
        self.core_examples.touch()

        self.ext_ttl = data_dir / "ext" / "auto" / "auto.ttl"
        self.ext_examples = data_dir / "ext" / "auto" / "auto-examples.txt"
        self.ext_ttl.touch()
        self.ext_examples.touch()

        self.issue100_ttl = data_dir / "ext" / "auto" / "issue-100.ttl"
        self.issue100_examples = data_dir / "ext" / "auto" / "issue-100-examples.txt"
        self.issue100_ttl.touch()
        self.issue100_examples.touch()

        self.issue200_ttl = data_dir / "ext" / "bib" / "issue-200.ttl"
        self.issue200_examples = data_dir / "ext" / "bib" / "issue-200-examples.txt"
        self.issue200_ttl.touch()
        self.issue200_examples.touch()

    def test_get_issue_numbers(self) -> None:
        self.assertEqual(self.issues.get_issue_numbers(), ["100", "200"])

    def test_get_ttl_files_all(self) -> None:
        self.assertEqual(
            self.issues.get_ttl_files(),
            [self.core_ttl, self.ext_ttl, self.issue100_ttl, self.issue200_ttl],
        )

    def test_get_ttl_files_filtered(self) -> None:
        self.assertEqual(
            self.issues.get_ttl_files(["100"]),
            [self.core_ttl, self.ext_ttl, self.issue100_ttl],
        )

    def test_get_example_files_all(self) -> None:
        self.assertEqual(
            self.issues.get_example_files(),
            [
                self.core_examples,
                self.ext_examples,
                self.issue100_examples,
                self.issue200_examples,
            ],
        )

    def test_get_example_files_filtered(self) -> None:
        self.assertEqual(
            self.issues.get_example_files(["200"]),
            [self.core_examples, self.ext_examples, self.issue200_examples],
        )

    def test_get_ttl_files_nonexistent_issue(self) -> None:
        self.assertEqual(
            self.issues.get_ttl_files(["9999"]),
            [self.core_ttl, self.ext_ttl],
        )

    def test_get_ttl_files_multiple_issues(self) -> None:
        self.assertEqual(
            self.issues.get_ttl_files(["100", "200"]),
            [self.core_ttl, self.ext_ttl, self.issue100_ttl, self.issue200_ttl],
        )


if __name__ == "__main__":
    unittest.main()
