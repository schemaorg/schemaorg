"""
Serializer plugin interface.

This module is useful for those wanting to write a serializer that can
plugin to rdflib. If you are wanting to invoke a serializer you likely
want to do so through the Graph class serialize method.

TODO: info for how to write a serializer that can plugin to rdflib.
See also rdflib.plugin

"""

from rdflib.term import URIRef

__all__ = ['Serializer']


class Serializer(object):

    def __init__(self, store):
        self.store = store
        self.encoding = "UTF-8"
        self.base = None

    def serialize(self, stream, base=None, encoding=None, **args):
        """Abstract method"""

    def relativize(self, uri):
        base = self.base
        if base is not None and uri.startswith(base):
            uri = URIRef(uri.replace(base, "", 1))
        return uri
