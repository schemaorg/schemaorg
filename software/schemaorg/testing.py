"""Shared temporary SiteBundle fixture helper for site-rendering unit tests."""

from __future__ import annotations

import json
from pathlib import Path

from schemaorg import constants
from schemaorg.layout import Domain, InputLayout, Releases
from schemaorg.progress import NullProgressReporter
from schemaorg.site_bundle import SiteBundle
from schemaorg.version import Version, VersionItem


def build_site_fixture(
    root: Path,
    ttl: str,
    *,
    templates: dict[str, str] | None = None,
    use_real_templates: bool = False,
    examples_txt: str | None = None,
    stats_json: list[dict[str, str]] | None = None,
    version_ref: str = "next",
) -> tuple[InputLayout, SiteBundle, Version]:
    """Create a minimal InputLayout and load its SiteBundle under root/in."""
    in_dir = root / "in"
    in_dir.mkdir(parents=True, exist_ok=True)

    versions_path = in_dir / "versions.json"
    versions_path.write_text(
        json.dumps({
            "schemaversion": "30.1",
            "releaseLog": {"30.1": "2026-09-16"},
        }),
        encoding="utf-8",
    )
    version = Version(versions_path)
    input_layout = InputLayout(in_dir)

    templates_dir = input_layout.dir(Domain.TEMPLATES)
    if use_real_templates:
        templates_dir.symlink_to(
            InputLayout(constants.PROJECT_ROOT).dir(Domain.TEMPLATES)
        )
    elif templates:
        for rel_path, content in templates.items():
            path = templates_dir / rel_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")

    data_dir = input_layout.dir(Domain.DATA)
    data_dir.mkdir(parents=True, exist_ok=True)
    if examples_txt is not None:
        (data_dir / "examples.txt").write_text(examples_txt, encoding="utf-8")

    if stats_json is not None:
        stats_dir = input_layout.dir(Domain.PUBLIC_STATS) / "commoncrawl"
        stats_dir.mkdir(parents=True, exist_ok=True)
        (stats_dir / "stats_2026_09.json").write_text(
            json.dumps(stats_json), encoding="utf-8"
        )

    target: VersionItem = version.resolve(version_ref)
    releases = Releases(input_layout, version)
    ttl_path = releases.file(target)
    ttl_path.parent.mkdir(parents=True, exist_ok=True)
    ttl_path.write_text(ttl, encoding="utf-8")

    bundle = SiteBundle.from_release(
        input_layout=input_layout,
        releases_layout=input_layout,
        target_version=target,
        progress=NullProgressReporter(),
    )
    return input_layout, bundle, version
