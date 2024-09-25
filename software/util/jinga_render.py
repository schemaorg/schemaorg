#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Import standard python libraries

import os
import sys
import jinja2
import logging

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software
import software.util.schemaversion as schemaversion

SITENAME = 'Schema.org'
TEMPLATESDIR = 'templates'
DOCSHREFSUFFIX=''
DOCSHREFPREFIX='/'
TERMHREFSUFFIX=''
TERMHREFPREFIX='/'

###################################################
#JINJA INITIALISATION
###################################################

def _jinjaDebug(text):
    logging.debug(text)
    return ''

local_vars = {}
def _set_local_var(local_vars, name, value):
    local_vars[name] = value
    return ''


JENV = None
def GetJinga():
    global JENV
    if JENV:
      return JENV
    jenv = jinja2.Environment(loader=jinja2.FileSystemLoader(TEMPLATESDIR), autoescape=True, cache_size=0)
    jenv.filters['debug']=_jinjaDebug
    jenv.globals['set_local_var'] = _set_local_var
    JENV = jenv
    return JENV

### Template rendering

def templateRender(template_path, extra_vars=None, template_instance=None):
  """Render a page template.

  Returns: the generated page.
  """
  #Basic variables configuring UI
  tvars = {
      'local_vars': local_vars,
      'version': schemaversion.getVersion(),
      'versiondate': schemaversion.getCurrentVersionDate(),
      'sitename': SITENAME,
      'TERMHREFPREFIX': TERMHREFPREFIX,
      'TERMHREFSUFFIX': TERMHREFSUFFIX,
      'DOCSHREFPREFIX': DOCSHREFPREFIX,
      'DOCSHREFSUFFIX': DOCSHREFSUFFIX,
      'home_page': 'False'
  }
  if extra_vars:
      tvars.update(extra_vars)

  template = template_instance or GetJinga().get_template(template_path)
  return template.render(tvars)

###################################################
#JINJA INITIALISATION - End
###################################################
