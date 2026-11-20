"""Post-processors applied to rendered text right before it is written."""

from __future__ import annotations

from collections.abc import Callable
import re

from schemaorg.sdo_uri import SdoUri

PostProcessor = Callable[[str], str]

# schema.org subdomains that are real websites rather than vocabulary layers;
# their links are left exactly as authored.
PRESERVED_SUBDOMAINS: frozenset[str] = frozenset({"blog", "dev"})


def protocol_swap(
    protocol: str = "https", altprotocol: str = "http"
) -> PostProcessor:
    """Returns a post-processor rewriting the scheme of every schema.org URI.

    Applies to the schema.org host and all of its subdomains except
    ``PRESERVED_SUBDOMAINS``.
    """
    pattern = re.compile(rf"{re.escape(protocol)}://([\w-]+(?:\.[\w-]+)*)")

    def swap_match(match: re.Match[str]) -> str:
        uri = SdoUri(match.group(0))
        if not uri.is_sdo() or uri.layer() in PRESERVED_SUBDOMAINS:
            return match.group(0)
        return f"{altprotocol}://{match.group(1)}"

    def swap(content: str) -> str:
        return pattern.sub(swap_match, content)

    return swap
