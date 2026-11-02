from collections.abc import Sequence
from pathlib import Path
import re

from schemaorg.layout.domain import Domain
from schemaorg.layout.input_layout import InputLayout

ALL_ISSUES: tuple[str, ...] = ("*",)
_ISSUE_RE: re.Pattern[str] = re.compile(r"^issue-([^-.]+)")


class Issues:
    """
    Builder class for determining which files should be loaded to construct
    the schema.org graph and examples.
    """

    def __init__(self, input_layout: InputLayout) -> None:
        self.input_layout = input_layout

    def get_issue_numbers(self) -> list[str]:
        """Returns a sorted list of all existing issue numbers found in the data."""
        issue_files = self.input_layout.files(Domain.DATA, ["ext/*/issue-*"])
        issue_numbers = {
            match.group(1)
            for f in issue_files
            if (match := _ISSUE_RE.match(f.name))
        }
        return sorted(issue_numbers)

    def get_ttl_files(self, issues: Sequence[str] = ALL_ISSUES) -> list[Path]:
        """Returns a list of TTL files needed to create the graph."""
        return self._get_files("*.ttl", issues)

    def get_example_files(
        self, issues: Sequence[str] = ALL_ISSUES
    ) -> list[Path]:
        """Returns a list of example txt files."""
        return self._get_files("*examples.txt", issues)

    def _get_files(self, ext_glob: str, issues: Sequence[str]) -> list[Path]:
        # Always include core data files from the root of the data domain
        root_files = self.input_layout.files(Domain.DATA, [ext_glob])

        # Scan all extension files in a single filesystem pass
        ext_files = self.input_layout.files(Domain.DATA, [f"ext/*/{ext_glob}"])

        if "*" not in issues:
            wanted = set(issues)
            ext_files = [
                f
                for f in ext_files
                if not (match := _ISSUE_RE.match(f.name))
                or match.group(1) in wanted
            ]

        return root_files + ext_files
