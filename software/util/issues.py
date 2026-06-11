#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from pathlib import Path
from typing import List, Union, Set

from software.util.paths import InputLayout, Domain

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
        issue_files = self.input_layout.domain_files(Domain.DATA, ["ext/*/issue-*"])
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

    def _get_files(self, extension_glob: str, issues: List[str]) -> List[Path]:
        # Always include core data files from the root of the data domain
        root_files = self.input_layout.domain_files(Domain.DATA, [extension_glob])

        # Always include extension "base" files (those that are NOT issue-specific)
        all_ext_files = self.input_layout.domain_files(Domain.DATA, [f"ext/*/{extension_glob}"])
        base_ext_files = [f for f in all_ext_files if not f.name.startswith("issue-")]

        # Use items in the 'issues' list as placeholders for targeted file search
        issue_patterns = []
        for issue in issues:
            # We construct a pattern like 'ext/*/issue-{issue}.ttl'
            # The extension_glob (e.g. '*.ttl') provides the suffix.
            # We strip the leading '*' from the glob to get the actual suffix.
            suffix = extension_glob[1:] if extension_glob.startswith("*") else extension_glob
            pattern = f"ext/*/issue-{issue}{suffix}"
            issue_patterns.append(pattern)

        issue_files = self.input_layout.domain_files(Domain.DATA, issue_patterns)

        # Combine all parts and ensure uniqueness
        combined = root_files + base_ext_files + issue_files

        # Sort for deterministic output
        return sorted(list(set(combined)))
