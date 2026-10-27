#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Schema.org URI namespace and manipulation helpers."""

import logging
from typing import Optional, Union
from urllib.parse import ParseResult, urlparse

from rdflib import BNode, Namespace, URIRef

from schemaorg import constants

log = logging.getLogger(__name__)

SDO = Namespace(constants.SCHEMA_URI)
SCHEMA_URL: ParseResult = urlparse(constants.SCHEMA_URI)
if not SCHEMA_URL.hostname:
    raise ValueError(f"SCHEMA_URI has no hostname: {constants.SCHEMA_URI!r}")


class SdoUri:
    """Wrapper around a URI or term identifier for schema.org URI operations.

    Scheme-less strings are schema.org term names; BNodes are never schema.org URIs.
    """

    def __init__(self, uri: Union[URIRef, str, ParseResult]) -> None:
        self._parsed = uri if isinstance(uri, ParseResult) else urlparse(str(uri))
        if not self._parsed.scheme and not isinstance(uri, BNode):
            self._parsed = urlparse(f"{constants.SCHEMA_URI}{self._parsed.geturl()}")
        if self._parsed.scheme != SCHEMA_URL.scheme and self.is_sdo():
            log.warning(f"Upgrading {self._parsed.scheme}:// schema.org URI to {SCHEMA_URL.scheme}:// {self._parsed.geturl()}")
            self._parsed = self._parsed._replace(scheme=SCHEMA_URL.scheme)

    @property
    def uri(self) -> URIRef:
        return URIRef(self._parsed.geturl())

    def is_sdo(self) -> bool:
        host = self._parsed.hostname or ""
        return host == SCHEMA_URL.hostname or host.endswith(
            f".{SCHEMA_URL.hostname}"
        )

    def term_name(self) -> str:
        if self.is_sdo():
            return self._parsed.path.removeprefix("/")
        return self._parsed.geturl()

    def layer(self) -> str:
        host = self._parsed.hostname or ""
        suffix = f".{SCHEMA_URL.hostname}"
        if host.endswith(suffix):
            return host.removesuffix(suffix)
        return "core"

    @classmethod
    def for_layer(cls, layer: Optional[str] = None) -> "SdoUri":
        """Root URI of a layer: https://schema.org for core/None/"", https://<layer>.schema.org otherwise (no trailing slash, no path)."""
        netloc = SCHEMA_URL.netloc
        if layer and layer != "core":
            netloc = f"{layer}.{SCHEMA_URL.hostname}"
        return cls(SCHEMA_URL._replace(netloc=netloc, path=""))

    def is_retired(self) -> bool:
        return self.layer() == "attic"

    def __str__(self) -> str:
        return self._parsed.geturl()
