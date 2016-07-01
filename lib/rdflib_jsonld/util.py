try:
    import json
    assert json  # workaround for pyflakes issue #13
except ImportError:
    import simplejson as json

from rdflib.py3compat import PY3

from os import sep
from os.path import normpath
if PY3:
    from urllib.parse import urljoin, urlsplit, urlunsplit
else:
    from urlparse import urljoin, urlsplit, urlunsplit

from rdflib.parser import create_input_source
if PY3:
    from io import StringIO


def source_to_json(source):
    # TODO: conneg for JSON (fix support in rdflib's URLInputSource!)
    source = create_input_source(source, format='json-ld')

    stream = source.getByteStream()
    try:
        if PY3:
            return json.load(StringIO(stream.read().decode('utf-8')))
        else:
            return json.load(stream)
    finally:
        stream.close()


VOCAB_DELIMS = ('#', '/', ':')

def split_iri(iri):
    for delim in VOCAB_DELIMS:
        at = iri.rfind(delim)
        if at > -1:
            return iri[:at+1], iri[at+1:]
    return iri, None

def norm_url(base, url):
    url = urljoin(base, url)
    parts = urlsplit(url)
    path = normpath(parts[2])
    if sep != '/':
        path = '/'.join(path.split(sep))
    if parts[2].endswith('/') and not path.endswith('/'):
        path += '/'
    return urlunsplit(parts[0:2] + (path,) + parts[3:])
