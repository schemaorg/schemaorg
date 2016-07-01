from rdflib.parser import Parser
from rdflib.plugins.parsers.ntriples import NTriplesParser

__all__ = ['NTSink', 'NTParser']


class NTSink(object):
    def __init__(self, graph):
        self.graph = graph

    def triple(self, s, p, o):
        self.graph.add((s, p, o))


class NTParser(Parser):
    """parser for the ntriples format, often stored with the .nt extension

    See http://www.w3.org/TR/rdf-testcases/#ntriples"""

    def __init__(self):
        super(NTParser, self).__init__()

    def parse(self, source, sink, baseURI=None):
        f = source.getByteStream()  # TODO getCharacterStream?
        parser = NTriplesParser(NTSink(sink))
        parser.parse(f)
        f.close()
