#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Schema.org root package."""

import locale


def _enforce_global_utf8() -> None:
    """Globally enforce UTF-8 as the default encoding for file reads/writes."""
    if hasattr(locale, 'getencoding'):
        locale.getencoding = lambda: 'utf-8'
    locale.getpreferredencoding = lambda do_setlocale=True: 'utf-8'


_enforce_global_utf8()
