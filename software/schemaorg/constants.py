"""Global constants for the schema.org project."""

from pathlib import Path

import pyprojroot

SCHEMA_URI: str = "https://schema.org/"
VERSIONS_FILE: str = "versions.json"
PROJECT_ROOT: Path = pyprojroot.find_root(
    pyprojroot.has_file(VERSIONS_FILE), Path(__file__).parent
)
