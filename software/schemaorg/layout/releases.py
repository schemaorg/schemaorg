"""Release discovery and destinations for schema.org published artefacts.

A release's location is computed from its version, never searched for, and
delegated to the given layout (``InputLayout`` or ``OutputLayout``) through
``Domain.RELEASE``.

``Releases`` is the counterpart of ``Issues``: it answers *which files* make
up a release, and nothing else.
"""

from enum import StrEnum, unique
from pathlib import Path

from schemaorg.layout.domain import Domain
from schemaorg.layout.input_layout import InputLayout
from schemaorg.layout.output_layout import OutputLayout
from schemaorg.version import Version, VersionItem

# Sentinel meaning "the current release", per versions.json.
CURRENT_VERSION = None

VersionRef = str | VersionItem | None


@unique
class Protocol(StrEnum):
    """URI scheme a release's vocabulary files are expressed in."""

    HTTPS = "https"
    HTTP = "http"


@unique
class Scope(StrEnum):
    """Portion of the vocabulary a release file covers."""

    ALL = "all"
    CURRENT = "current"


class Releases:
    """Locates the files belonging to a published release.

    Args:
        layout: Input or output layout holding the releases.
        version: Version authority for declared releases.
    """

    @staticmethod
    def _schema_file(
        scope: Scope | str,
        protocol: Protocol | str,
        extension: str,
    ) -> str:
        """Joins the non-empty parts, so "" drops its separator too."""
        parts = [p for p in ("schemaorg", str(scope), str(protocol)) if p]
        return "-".join(parts) + extension

    def __init__(
        self,
        layout: InputLayout | OutputLayout,
        version: Version,
    ) -> None:
        self.layout = layout
        self.version = version

    # -- versions, per versions.json -------------------------------------

    def versions(self) -> list[VersionItem]:
        return self.version.versions()

    def current(self) -> VersionItem:
        return self.version.current()

    def resolve(self, version: VersionRef = CURRENT_VERSION) -> VersionItem:
        if version is None:
            return self.current()
        wanted = str(version)
        found = next((v for v in self.versions() if str(v) == wanted), None)
        if found is not None:
            return found
        declared = ", ".join(str(v) for v in self.versions())
        raise ValueError(
            f"Version {wanted} is not declared in "
            f"{self.version.versions_path}. Declared: {declared}"
        )

    # -- locations: computed, never searched for -------------------------

    def dir(self, version: VersionRef = CURRENT_VERSION) -> Path:
        v = self.resolve(version)
        return self.layout.dir(Domain.RELEASE) / str(v)

    def get_ttl_files(
        self,
        version: VersionRef = CURRENT_VERSION,
        protocol: Protocol = Protocol.HTTPS,
        scope: Scope = Scope.ALL,
    ) -> list[Path]:
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

    def file(
        self,
        version: VersionRef = CURRENT_VERSION,
        protocol: Protocol | str = Protocol.HTTPS,
        scope: Scope | str = Scope.ALL,
        extension: str = ".ttl",
        filename: str | None = None,
    ) -> Path:
        v = self.resolve(version)
        name = filename or self._schema_file(scope, protocol, extension)
        return self.layout.file(Domain.RELEASE, f"{v}/{name}")
