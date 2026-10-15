"""XML sitemap renderer."""

from __future__ import annotations

from schemaorg import constants
from schemaorg.model import Vocabulary
from schemaorg.version import VersionItem

SITEMAP_STATIC_PAGES: tuple[str, ...] = (
    "docs/schemas.html",
    "docs/full.html",
    "docs/gs.html",
    "docs/about.html",
    "docs/howwework.html",
    "docs/releases.html",
    "docs/faq.html",
    "docs/datamodel.html",
    "docs/developers.html",
    "docs/extension.html",
    "docs/meddocs.html",
    "docs/hotels.html",
)


def render_sitemap(vocab: Vocabulary, version: VersionItem) -> str:
    """sitemap.xml listing every term page plus the static docs pages."""
    version_date = version.date()
    lastmod = f"   <lastmod>{version_date}</lastmod>\n" if version_date else ""

    def node(path: str) -> str:
        return f" <url>\n   <loc>{constants.SCHEMA_URI}{path}</loc>\n{lastmod} </url>\n"

    term_ids = sorted(t.id for t in vocab.all_terms().values())
    return "".join([
        '<?xml version="1.0" encoding="utf-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n',
        *(node(term_id) for term_id in term_ids),
        *(node(page) for page in SITEMAP_STATIC_PAGES),
        "</urlset>\n",
    ])
