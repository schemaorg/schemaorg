"""Domain enumeration representing filesystem paths for schema.org layouts."""

from enum import StrEnum, unique


@unique
class Domain(StrEnum):
    """Domains mapped directly to their relative filesystem paths."""

    # Core source directories
    DATA = "data"
    DOCS = "docs"
    TEMPLATES = "templates"
    STATIC_DOC_INSERTS = "templates/static-doc-inserts"
    PUBLIC_STATS = "data/public_stats"
    ROOT = ""

    # GCloud deployment configurations
    GCLOUD = "software/gcloud"
    GCLOUD_SITE = "gcloud"

    # Generated output directories
    DOCS_COLLAB = "docs/collab"
    DOCS_TERMFIND = "docs/termfind"
    TERMS = "terms"
    RELEASE = "releases"
    EMPTY = "empty"
