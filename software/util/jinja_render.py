from __future__ import annotations

import functools
from typing import Any

import jinja2

from schemaorg import constants
import util.schema as schema

TEMPLATESDIR = constants.PROJECT_ROOT / "templates"
TERMHREFSUFFIX = ""
TERMHREFPREFIX = "/"


def _set_local_var(local_vars_dict: dict[str, Any], name: str, value: Any) -> str:
    local_vars_dict[name] = value
    return ""


@functools.lru_cache(maxsize=1)
def get_jinja_env() -> jinja2.Environment:
    jenv = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATESDIR),
        autoescape=True,
        cache_size=0,
    )
    jenv.globals["set_local_var"] = _set_local_var
    return jenv


def templateRender(
    template_path: str | None = None,
    extra_vars: dict[str, Any] | None = None,
    template_instance: jinja2.Template | None = None,
) -> str:
    """Render a page template."""
    target = schema.target_version()
    tvars: dict[str, Any] = {
        "local_vars": {},
        "version": target.number(),
        "versiondate": target.date() or "",
        "sitename": schema.constants.SITENAME,
        "TERMHREFPREFIX": TERMHREFPREFIX,
        "TERMHREFSUFFIX": TERMHREFSUFFIX,
    }
    if extra_vars:
        tvars.update(extra_vars)

    if template_instance is not None:
        template = template_instance
    elif template_path:
        template = get_jinja_env().get_template(template_path)
    else:
        raise ValueError("Either template_path or template_instance must be provided")

    return str(template.render(tvars))
