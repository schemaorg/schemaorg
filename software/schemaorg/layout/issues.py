#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from pathlib import Path
from typing import List, Sequence, Set, Union

from schemaorg.layout.domain import Domain
from schemaorg.layout.input_layout import InputLayout

ALL_ISSUES = ["*"]


class Issues:
    """
    Builder class for determining which files should be loaded to construct
    the schema.org graph and examples.
    """

    def __init__(self, input_layout: InputLayout):
        self.input_layout = input_layout

    def get_issue_numbers(self) -> List[str]:
        """Returns a sorted list of all existing issue numbers found in the data."""
        issue_files = self.input_layout.files(Domain.DATA, ["ext/*/issue-*"])
        issue_numbers: Set[str] = set()
        for f in issue_files:
            match = re.match(r"^issue-([^-.]+)", f.name)
            if match:
                issue_numbers.add(match.group(1))
        return sorted(list(issue_numbers))

    def get_ttl_files(self, issues: List[str] = ALL_ISSUES) -> List[Path]:
        """Returns a list of TTL files needed to create the graph."""
        return self._get_files("*.ttl", issues)

    def get_example_files(self, issues: List[str] = ALL_ISSUES) -> List[Path]:
        """Returns a list of example txt files."""
        return self._get_files("*examples.txt", issues)

    def _get_files(self, ext_glob: str, issues: Sequence[str]) -> List[Path]:
        # Always include core data files from the root of the data domain
        root_files = self.input_layout.files(Domain.DATA, [ext_glob])

        # Scan all extension files in a single filesystem pass
        ext_files = self.input_layout.files(Domain.DATA, [f"ext/*/{ext_glob}"])

        def keep_for_issues(f):
            match = re.match(r"issue-([^-.]+)", f.name)
            return not match or match.group(1) in issues

        if "*" not in issues:
            ext_files = list(filter(keep_for_issues, ext_files))

        return sorted(list(set(root_files + ext_files)))
