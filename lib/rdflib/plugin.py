"""
Plugin support for rdf.

There are a number of plugin points for rdf: parser, serializer,
store, query processor, and query result. Plugins can be registered
either through setuptools entry_points or by calling
rdf.plugin.register directly.

If you have a package that uses a setuptools based setup.py you can add the
following to your setup::

    entry_points = {
        'rdf.plugins.parser': [
            'nt =     rdf.plugins.parsers.nt:NTParser',
            ],
        'rdf.plugins.serializer': [
            'nt =     rdf.plugins.serializers.NTSerializer:NTSerializer',
            ],
        }

See the `setuptools dynamic discovery of services and plugins`__ for more
information.

.. __: http://peak.telecommunity.com/DevCenter/setuptools#dynamic-discovery-of-services-and-plugins

"""

from rdflib.store import Store
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from rdflib.query import ResultParser, ResultSerializer, \
    Processor, Result, UpdateProcessor
from rdflib.exceptions import Error

__all__ = [
    'register', 'get', 'plugins', 'PluginException', 'Plugin', 'PKGPlugin']

entry_points = {'rdf.plugins.store': Store,
                'rdf.plugins.serializer': Serializer,
                'rdf.plugins.parser': Parser,
                'rdf.plugins.resultparser': ResultParser,
                'rdf.plugins.resultserializer': ResultSerializer,
                'rdf.plugins.queryprocessor': Processor,
                'rdf.plugins.queryresult': Result,
                'rdf.plugins.updateprocessor': UpdateProcessor
                }

_plugins = {}


class PluginException(Error):
    pass


class Plugin(object):

    def __init__(self, name, kind, module_path, class_name):
        self.name = name
        self.kind = kind
        self.module_path = module_path
        self.class_name = class_name
        self._class = None

    def getClass(self):
        if self._class is None:
            module = __import__(self.module_path, globals(), locals(), [""])
            self._class = getattr(module, self.class_name)
        return self._class


class PKGPlugin(Plugin):

    def __init__(self, name, kind, ep):
        self.name = name
        self.kind = kind
        self.ep = ep
        self._class = None

    def getClass(self):
        if self._class is None:
            self._class = self.ep.load()
        return self._class


def register(name, kind, module_path, class_name):
    """
    Register the plugin for (name, kind). The module_path and
    class_name should be the path to a plugin class.
    """
    p = Plugin(name, kind, module_path, class_name)
    _plugins[(name, kind)] = p


def get(name, kind):
    """
    Return the class for the specified (name, kind). Raises a
    PluginException if unable to do so.
    """
    try:
        p = _plugins[(name, kind)]
    except KeyError:
        raise PluginException(
            "No plugin registered for (%s, %s)" % (name, kind))
    return p.getClass()


try:
    from pkg_resources import iter_entry_points
except ImportError:
    pass  # TODO: log a message
else:
    # add the plugins specified via pkg_resources' EntryPoints.
    for entry_point, kind in entry_points.iteritems():
        for ep in iter_entry_points(entry_point):
            _plugins[(ep.name, kind)] = PKGPlugin(ep.name, kind, ep)


def plugins(name=None, kind=None):
    """
    A generator of the plugins.

    Pass in name and kind to filter... else leave None to match all.
    """
    for p in _plugins.values():
        if (name is None or name == p.name) and (
                kind is None or kind == p.kind):
            yield p

register(
    'default', Store,
    'rdflib.plugins.memory', 'IOMemory')
register(
    'IOMemory', Store,
    'rdflib.plugins.memory', 'IOMemory')
register(
    'Auditable', Store,
    'rdflib.plugins.stores.auditable', 'AuditableStore')
register(
    'Concurrent', Store,
    'rdflib.plugins.stores.concurrent', 'ConcurrentStore')
register(
    'Sleepycat', Store,
    'rdflib.plugins.sleepycat', 'Sleepycat')
register(
    'SPARQLStore', Store,
    'rdflib.plugins.stores.sparqlstore', 'SPARQLStore')
register(
    'SPARQLUpdateStore', Store,
    'rdflib.plugins.stores.sparqlstore', 'SPARQLUpdateStore')

register(
    'application/rdf+xml', Serializer,
    'rdflib.plugins.serializers.rdfxml', 'XMLSerializer')
register(
    'xml', Serializer,
    'rdflib.plugins.serializers.rdfxml', 'XMLSerializer')
register(
    'text/n3', Serializer,
    'rdflib.plugins.serializers.n3', 'N3Serializer')
register(
    'n3', Serializer,
    'rdflib.plugins.serializers.n3', 'N3Serializer')
register(
    'text/turtle', Serializer,
    'rdflib.plugins.serializers.turtle', 'TurtleSerializer')
register(
    'turtle', Serializer,
    'rdflib.plugins.serializers.turtle', 'TurtleSerializer')
register(
    'trig', Serializer,
    'rdflib.plugins.serializers.trig', 'TrigSerializer')
register(
    'application/n-triples', Serializer,
    'rdflib.plugins.serializers.nt', 'NTSerializer')
register(
    'nt', Serializer,
    'rdflib.plugins.serializers.nt', 'NTSerializer')
register(
    'pretty-xml', Serializer,
    'rdflib.plugins.serializers.rdfxml', 'PrettyXMLSerializer')
register(
    'trix', Serializer,
    'rdflib.plugins.serializers.trix', 'TriXSerializer')
register(
    'application/trix', Serializer,
    'rdflib.plugins.serializers.trix', 'TriXSerializer')
register(
    "application/n-quads", Serializer,
    'rdflib.plugins.serializers.nquads', 'NQuadsSerializer')
register(
    "nquads", Serializer,
    'rdflib.plugins.serializers.nquads', 'NQuadsSerializer')

register(
    'application/rdf+xml', Parser,
    'rdflib.plugins.parsers.rdfxml', 'RDFXMLParser')
register(
    'xml', Parser,
    'rdflib.plugins.parsers.rdfxml', 'RDFXMLParser')
register(
    'text/n3', Parser,
    'rdflib.plugins.parsers.notation3', 'N3Parser')
register(
    'n3', Parser,
    'rdflib.plugins.parsers.notation3', 'N3Parser')
register(
    'text/turtle', Parser,
    'rdflib.plugins.parsers.notation3', 'TurtleParser')
register(
    'turtle', Parser,
    'rdflib.plugins.parsers.notation3', 'TurtleParser')
register(
    'application/n-triples', Parser,
    'rdflib.plugins.parsers.nt', 'NTParser')
register(
    'nt', Parser,
    'rdflib.plugins.parsers.nt', 'NTParser')
register(
    'application/n-quads', Parser,
    'rdflib.plugins.parsers.nquads', 'NQuadsParser')
register(
    'nquads', Parser,
    'rdflib.plugins.parsers.nquads', 'NQuadsParser')
register(
    'application/trix', Parser,
    'rdflib.plugins.parsers.trix', 'TriXParser')
register(
    'trix', Parser,
    'rdflib.plugins.parsers.trix', 'TriXParser')
register(
    'trig', Parser,
    'rdflib.plugins.parsers.trig', 'TrigParser')

# The basic parsers: RDFa (by default, 1.1),
# microdata, and embedded turtle (a.k.a. hturtle)
register(
    'hturtle', Parser,
    'rdflib.plugins.parsers.hturtle', 'HTurtleParser')
register(
    'rdfa', Parser,
    'rdflib.plugins.parsers.structureddata', 'RDFaParser')
register(
    'mdata', Parser,
    'rdflib.plugins.parsers.structureddata', 'MicrodataParser')
register(
    'microdata', Parser,
    'rdflib.plugins.parsers.structureddata', 'MicrodataParser')
# A convenience to use the RDFa 1.0 syntax (although the parse method can
# be invoked with an rdfa_version keyword, too)
register(
    'rdfa1.0', Parser,
    'rdflib.plugins.parsers.structureddata', 'RDFa10Parser')
# Just for the completeness, if the user uses this
register(
    'rdfa1.1', Parser,
    'rdflib.plugins.parsers.structureddata', 'RDFaParser')
# An HTML file may contain both microdata, rdfa, or turtle. If the user
# wants them all, the parser below simply invokes all:
register(
    'html', Parser,
    'rdflib.plugins.parsers.structureddata', 'StructuredDataParser')
# Some media types are also bound to RDFa
register(
    'application/svg+xml', Parser,
    'rdflib.plugins.parsers.structureddata', 'RDFaParser')
register(
    'application/xhtml+xml', Parser,
    'rdflib.plugins.parsers.structureddata', 'RDFaParser')
# 'text/html' media type should be equivalent to html:
register(
    'text/html', Parser,
    'rdflib.plugins.parsers.structureddata', 'StructuredDataParser')


register(
    'sparql', Result,
    'rdflib.plugins.sparql.processor', 'SPARQLResult')
register(
    'sparql', Processor,
    'rdflib.plugins.sparql.processor', 'SPARQLProcessor')

register(
    'sparql', UpdateProcessor,
    'rdflib.plugins.sparql.processor', 'SPARQLUpdateProcessor')


register(
    'xml', ResultSerializer,
    'rdflib.plugins.sparql.results.xmlresults', 'XMLResultSerializer')
register(
    'txt', ResultSerializer,
    'rdflib.plugins.sparql.results.txtresults', 'TXTResultSerializer')
register(
    'json', ResultSerializer,
    'rdflib.plugins.sparql.results.jsonresults', 'JSONResultSerializer')
register(
    'csv', ResultSerializer,
    'rdflib.plugins.sparql.results.csvresults', 'CSVResultSerializer')

register(
    'xml', ResultParser,
    'rdflib.plugins.sparql.results.xmlresults', 'XMLResultParser')
register(
    'json', ResultParser,
    'rdflib.plugins.sparql.results.jsonresults', 'JSONResultParser')
register(
    'csv', ResultParser,
    'rdflib.plugins.sparql.results.csvresults', 'CSVResultParser')
register(
    'tsv', ResultParser,
    'rdflib.plugins.sparql.results.tsvresults', 'TSVResultParser')
