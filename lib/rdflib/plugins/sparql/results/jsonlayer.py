# -*- coding: utf-8 -*-
#
# Copyright (C) 2009 Christopher Lenz
# All rights reserved.
#

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:

# 1. Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
# notice, this list of conditions and the following disclaimer in
# the documentation and/or other materials provided with the
# distribution.
# 3. The name of the author may not be used to endorse or promote
# products derived from this software without specific prior
# written permission.

# THIS SOFTWARE IS PROVIDED BY THE AUTHOR ``AS IS'' AND ANY EXPRESS
# OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE
# GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER
# IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR
# OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN
# IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""Thin abstraction layer over the different available modules for decoding
and encoding JSON data.

This module currently supports the following JSON modules:
 - ``simplejson``: http://code.google.com/p/simplejson/
 - ``cjson``: http://pypi.python.org/pypi/python-cjson
 - ``json``: This is the version of ``simplejson`` that is bundled with the
   Python standard library since version 2.6
   (see http://docs.python.org/library/json.html)

The default behavior is to use ``simplejson`` if installed, and otherwise
fallback to the standard library module. To explicitly tell SPARQLWrapper
which module to use, invoke the `use()` function with the module name::

    import jsonlayer
    jsonlayer.use('cjson')

In addition to choosing one of the above modules, you can also configure
SPARQLWrapper to use custom decoding and encoding functions::

    import jsonlayer
    jsonlayer.use(decode=my_decode, encode=my_encode)

"""

__all__ = ['decode', 'encode', 'use']

_initialized = False
_using = None
_decode = None
_encode = None


def decode(string):
    """Decode the given JSON string.

    :param string: the JSON string to decode
    :type string: basestring
    :return: the corresponding Python data structure
    :rtype: object
    """
    if not _initialized:
        _initialize()
    return _decode(string)


def encode(obj):
    """Encode the given object as a JSON string.

    :param obj: the Python data structure to encode
    :type obj: object
    :return: the corresponding JSON string
    :rtype: basestring
    """
    if not _initialized:
        _initialize()
    return _encode(obj)


def use(module=None, decode=None, encode=None):
    """Set the JSON library that should be used, either by specifying a known
    module name, or by providing a decode and encode function.

    The modules "simplejson", "cjson", and "json" are currently supported for
    the ``module`` parameter.

    If provided, the ``decode`` parameter must be a callable that accepts a
    JSON string and returns a corresponding Python data structure. The
    ``encode`` callable must accept a Python data structure and return the
    corresponding JSON string. Exceptions raised by decoding and encoding
    should be propagated up unaltered.

    :param module: the name of the JSON library module to use, or the module
                   object itself
    :type module: str or module
    :param decode: a function for decoding JSON strings
    :type decode: callable
    :param encode: a function for encoding objects as JSON strings
    :type encode: callable
    """
    global _decode, _encode, _initialized, _using
    if module is not None:
        if not isinstance(module, basestring):
            module = module.__name__
        if module not in ('cjson', 'json', 'simplejson'):
            raise ValueError('Unsupported JSON module %s' % module)
        _using = module
        _initialized = False
    else:
        assert decode is not None and encode is not None
        _using = 'custom'
        _decode = decode
        _encode = encode
        _initialized = True


def _initialize():
    global _initialized

    def _init_simplejson():
        global _decode, _encode
        import simplejson
        _decode = lambda string, loads=simplejson.loads: loads(string)
        _encode = lambda obj, dumps=simplejson.dumps: \
            dumps(obj, allow_nan=False, ensure_ascii=False)

    def _init_cjson():
        global _decode, _encode
        import cjson
        _decode = lambda string, decode=cjson.decode: decode(string)
        _encode = lambda obj, encode=cjson.encode: encode(obj)

    def _init_stdlib():
        global _decode, _encode
        json = __import__('json', {}, {})
        _decode = lambda string, loads=json.loads: loads(string)
        _encode = lambda obj, dumps=json.dumps: \
            dumps(obj, allow_nan=False, ensure_ascii=False)

    if _using == 'simplejson':
        _init_simplejson()
    elif _using == 'cjson':
        _init_cjson()
    elif _using == 'json':
        _init_stdlib()
    elif _using != 'custom':
        try:
            _init_simplejson()
        except ImportError:
            _init_stdlib()
    _initialized = True
