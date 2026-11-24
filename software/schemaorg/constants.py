"""Global constants for the schema.org project."""

from pathlib import Path
from urllib.parse import urlparse

import pyprojroot

SCHEMA_URI: str = "https://schema.org/"
SCHEMA_PREFIX: str = "schema"
SITENAME: str = urlparse(SCHEMA_URI).hostname.capitalize()
VERSIONS_FILE: str = "versions.json"
PROJECT_ROOT: Path = pyprojroot.find_root(
    pyprojroot.has_file(VERSIONS_FILE), Path(__file__).parent
)
