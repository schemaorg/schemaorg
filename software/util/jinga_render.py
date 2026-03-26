#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import standard python libraries

import os
import sys
import jinja2
import logging
import typing
from typing import Any, Dict, List, Optional, Tuple, Union, Iterable, Sequence, Callable

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software
import software.util.schemaversion as schemaversion

SITENAME: str = "Schema.org"
TEMPLATESDIR: str = "templates"
DOCSHREFSUFFIX: str = ""
DOCSHREFPREFIX: str = "/"
TERMHREFSUFFIX: str = ""
TERMHREFPREFIX: str = "/"

###################################################
# JINJA INITIALISATION
###################################################


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
    if JENV:
        return JENV
    jenv: jinja2.Environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader(TEMPLATESDIR), autoescape=True, cache_size=0
    )
    jenv.filters["debug"] = _jinjaDebug
    jenv.globals["set_local_var"] = _set_local_var
    JENV = jenv
    return JENV


### Template rendering


def templateRender(template_path: Optional[str], extra_vars: Optional[Dict[str, Any]] = None, template_instance: Optional[jinja2.Template] = None) -> str:
    """Render a page template.

    Returns: the generated page.
    """
    # Basic variables configuring UI
    tvars: Dict[str, Any] = {
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

    template: jinja2.Template
    if template_instance:
        template = template_instance
    elif template_path:
        template = GetJinga().get_template(template_path)
    else:
        raise ValueError("Either template_path or template_instance must be provided")
        
    return str(template.render(tvars))


###################################################
# JINJA INITIALISATION - End
###################################################
