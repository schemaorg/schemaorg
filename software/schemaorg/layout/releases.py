#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Release discovery and destinations for schema.org published artefacts.

Two sources, one each:

* the **source tree** supplies ``versions.json``, the authority on which
  versions exist, read through ``Version`` (``InputLayout``);
* the **output tree** supplies every path: releases are both read from and
  published to ``<output>/releases/<version>`` (``OutputLayout``).

A release's location is computed from its version, never searched for.

``Releases`` is the counterpart of ``Issues``: it answers *which files* make
up a release, and nothing else.
"""

from enum import Enum, unique
from pathlib import Path
from typing import ClassVar, List, Union

from schemaorg.layout.domain import Domain
from schemaorg.layout.input_layout import InputLayout
from schemaorg.layout.output_layout import OutputLayout
from schemaorg.version import Version, VersionItem

# Sentinel meaning "the current release", per versions.json.
CURRENT_VERSION = None

VersionRef = Union[str, VersionItem, None]


@unique
class Protocol(str, Enum):
    """URI scheme a release's vocabulary files are expressed in."""

    HTTPS = "https"
    HTTP = "http"

    def __str__(self) -> str:
        return str(self.value)


@unique
class Scope(str, Enum):
    """Portion of the vocabulary a release file covers."""

    ALL = "all"
    CURRENT = "current"

    def __str__(self) -> str:
        return str(self.value)


class Releases:
    """Locates the files belonging to a published release.

    Args:
        input_layout: Source tree, holding ``versions.json``.
        output_layout: Output tree, holding the releases.
    """

    # Name of the file declaring every version, at the source tree root.
    VERSIONS_FILE: ClassVar[str] = "versions.json"

    @staticmethod
    def _schema_file(
        scope: Union[Scope, str],
        protocol: Union[Protocol, str],
        extension: str,
    ) -> str:
        """Joins the non-empty parts, so "" drops its separator too."""
        parts = [p for p in ("schemaorg", str(scope), str(protocol)) if p]
        return "-".join(parts) + extension

    def __init__(
        self,
        input_layout: InputLayout,
        output_layout: OutputLayout,
    ) -> None:
        self.input_layout = input_layout
        self.output_layout = output_layout
        self.version = Version(
            input_layout.file(Domain.ROOT, self.VERSIONS_FILE)
        )

    # -- versions, per versions.json -------------------------------------

    def versions(self) -> List[VersionItem]:
        return self.version.versions()

    def current(self) -> VersionItem:
        return self.version.current()

    def resolve(self, version: VersionRef = CURRENT_VERSION) -> VersionItem:
        if version is None:
            return self.current()
        wanted = str(version)
        candidates = [v for v in self.versions() if str(v) == wanted]
        if candidates:
            return candidates[0]
        declared = ", ".join(str(v) for v in self.versions())
        raise ValueError(
            f"Version {wanted} is not declared in "
            f"{self.version.versions_path}. Declared: {declared}"
        )

    # -- locations: computed, never searched for -------------------------

    def dir(self, version: VersionRef = CURRENT_VERSION) -> Path:
        v = self.resolve(version)
        return self.output_layout.dir(Domain.RELEASE) / str(v)

    def get_ttl_files(
        self,
        version: VersionRef = CURRENT_VERSION,
        protocol: Protocol = Protocol.HTTPS,
        scope: Scope = Scope.ALL,
    ) -> List[Path]:
        release_dir = self.dir(version)
        if not release_dir.is_dir():
            raise FileNotFoundError(
                f"Release {release_dir.name} is declared but not present at "
                f"{release_dir}"
            )
        name = self._schema_file(scope, protocol, ".ttl")
        path = release_dir / name
        if path.is_file():
            return [path]
        raise FileNotFoundError(
            f"Release {release_dir.name} has no '{name}' file."
        )

    # -- writing: the only thing that creates anything -------------------

    def publish_file(
        self,
        version: VersionRef = CURRENT_VERSION,
        protocol: Protocol = Protocol.HTTPS,
        scope: Scope = Scope.ALL,
        extension: str = ".ttl",
    ) -> Path:
        target = self.dir(version)
        target.mkdir(parents=True, exist_ok=True)
        return target / self._schema_file(scope, protocol, extension)
