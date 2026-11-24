"""Floating Jinja2 renderer for schema.org HTML templates."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any

import jinja2

from schemaorg import constants
from schemaorg.layout import Domain, InputLayout
from schemaorg.version import VersionItem


def _set_local_var(
    local_vars_dict: dict[str, Any], name: str, value: Any
) -> str:
    local_vars_dict[name] = value
    return ""


class TemplateRenderer:
    """Renders Jinja2 templates from an InputLayout for a target VersionItem."""

    def __init__(
        self,
        input_layout: InputLayout,
        version: VersionItem,
        build_opts: Sequence[str],
    ) -> None:
        self.input_layout: InputLayout = input_layout
        self.version: VersionItem = version
        self.build_opts: tuple[str, ...] = tuple(build_opts)

        self._env: jinja2.Environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                input_layout.dir(Domain.TEMPLATES)
            ),
            autoescape=True,
        )
        self._env.globals["set_local_var"] = _set_local_var

    def get_template(self, name: str) -> jinja2.Template:
        return self._env.get_template(name)

    def render(
        self,
        template: str | jinja2.Template,
        extra_vars: Mapping[str, Any],
    ) -> str:
        tvars: dict[str, Any] = {
            "local_vars": {},
            "version": self.version.number(),
            "versiondate": self.version.date() or "",
            "sitename": constants.SITENAME,
            "docsdir": f"/{Domain.DOCS}",
            "BUILDOPTS": self.build_opts,
        }
        tvars.update(extra_vars)
        compiled = (
            self._env.get_template(template)
            if isinstance(template, str)
            else template
        )
        return str(compiled.render(tvars))
