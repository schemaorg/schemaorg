"""Layout package managing filesystem paths and domains for schema.org."""

from schemaorg.layout.domain import Domain
from schemaorg.layout.input_layout import InputLayout, checkDataDirectories
from schemaorg.layout.issues import Issues
from schemaorg.layout.output_layout import OutputLayout
from schemaorg.layout.releases import (
    LATEST_RELEASE,
    NEXT_VERSION,
    Protocol,
    Releases,
    Scope,
)
from schemaorg.layout.stats_layout import StatsLayout, StatsProvider

__all__ = [
    "Domain",
    "InputLayout",
    "Issues",
    "LATEST_RELEASE",
    "NEXT_VERSION",
    "OutputLayout",
    "Protocol",
    "Releases",
    "Scope",
    "StatsLayout",
    "StatsProvider",
    "checkDataDirectories",
]
