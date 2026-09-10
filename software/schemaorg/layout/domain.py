#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Domain enumeration representing filesystem paths for schema.org layouts."""

from enum import Enum, unique


@unique
class Domain(str, Enum):
    """Domains mapped directly to their relative filesystem paths."""

    # Core source directories
    DATA = "data"
    DOCS = "docs"
    TEMPLATES = "templates"
    STATIC_DOC_INSERTS = "templates/static-doc-inserts"
    PUBLIC_STATS = "data/public_stats"
    PUBLIC_STATS_GOOGLE = "data/public_stats/google"
    RELEASE_DATA = "data/releases"
    ROOT = ""

    # GCloud deployment configurations
    GCLOUD = "software/gcloud"
    GCLOUD_SITE = "gcloud"

    # Generated output directories
    DOCS_COLLAB = "docs/collab"
    DOCS_TERMFIND = "docs/termfind"
    TERMS = "terms"
    RELEASE = "releases"
    LATEST_RELEASE = "releases/LATEST"
    EMPTY = "empty"

    def __str__(self) -> str:
        return str(self.value)
