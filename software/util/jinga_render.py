#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import standard python libraries
import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Union

import jinja2

# Import schema.org libraries
if Path.cwd() not in [Path(p).resolve() for p in sys.path]:
    sys.path.insert(1, str(Path.cwd()))

import software.util.schemaversion as schemaversion

SITENAME = "Schema.org"
TEMPLATESDIR = "templates"
DOCSHREFSUFFIX = ""
DOCSHREFPREFIX = "/"
TERMHREFSUFFIX = ""
TERMHREFPREFIX = "/"

def _jinjaDebug(text: str) -> str:
    logging.debug(text)
    return ""

local_vars: Dict[str, Any] = {}

def _set_local_var(local_vars_dict: Dict[str, Any], name: str, value: Any) -> str:
    local_vars_dict[name] = value
    return ""

JENV: Optional[jinja2.Environment] = None

def GetJinga() -> jinja2.Environment:
    global JENV
    if JENV is not None:
        return JENV
    
    jenv = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATESDIR),
        autoescape=True,
        cache_size=0
    )
    jenv.filters["debug"] = _jinjaDebug
    jenv.globals["set_local_var"] = _set_local_var
    JENV = jenv
    return JENV


def templateRender(
    template_path: Optional[str], 
    extra_vars: Optional[Dict[str, Any]] = None, 
    template_instance: Optional[jinja2.Template] = None
) -> str:
    """Render a page template."""
    # Basic variables configuring UI
    tvars = {
        "local_vars": local_vars,
        "version": schemaversion.getVersion(),
        "versiondate": schemaversion.getCurrentVersionDate(),
        "sitename": SITENAME,
        "TERMHREFPREFIX": TERMHREFPREFIX,
        "TERMHREFSUFFIX": TERMHREFSUFFIX,
        "DOCSHREFPREFIX": DOCSHREFPREFIX,
        "DOCSHREFSUFFIX": DOCSHREFSUFFIX,
        "home_page": "False",
    }
    if extra_vars:
        tvars.update(extra_vars)

    if template_instance:
        template = template_instance
    elif template_path:
        template = GetJinga().get_template(template_path)
    else:
        raise ValueError("Either template_path or template_instance must be provided")
        
    return str(template.render(tvars))
