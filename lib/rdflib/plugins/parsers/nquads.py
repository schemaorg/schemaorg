"""
This is a rdflib plugin for parsing NQuad files into Conjunctive
graphs that can be used and queried. The store that backs the graph
*must* be able to handle contexts.

>>> from rdflib import ConjunctiveGraph, URIRef, Namespace
>>> g = ConjunctiveGraph()
>>> data = open("test/nquads.rdflib/example.nquads", "rb")
>>> g.parse(data, format="nquads") # doctest:+ELLIPSIS
<Graph identifier=... (<class 'rdflib.graph.Graph'>)>
>>> assert len(g.store) == 449
>>> # There should be 16 separate contexts
>>> assert len([x for x in g.store.contexts()]) == 16
>>> # is the name of entity E10009 "Arco Publications"?
>>> #   (in graph http://bibliographica.org/entity/E10009)
>>> # Looking for:
>>> # <http://bibliographica.org/entity/E10009>
>>> #   <http://xmlns.com/foaf/0.1/name>
>>> #   "Arco Publications"
>>> #   <http://bibliographica.org/entity/E10009>
>>> s = URIRef("http://bibliographica.org/entity/E10009")
>>> FOAF = Namespace("http://xmlns.com/foaf/0.1/")
>>> assert(g.value(s, FOAF.name).eq("Arco Publications"))
"""

from codecs import getreader

from rdflib.py3compat import b

from rdflib import ConjunctiveGraph

# Build up from the NTriples parser:
from rdflib.plugins.parsers.ntriples import NTriplesParser
from rdflib.plugins.parsers.ntriples import ParseError
from rdflib.plugins.parsers.ntriples import r_tail
from rdflib.plugins.parsers.ntriples import r_wspace
from rdflib.plugins.parsers.ntriples import r_wspaces

__all__ = ['NQuadsParser']


class NQuadsParser(NTriplesParser):

    def parse(self, inputsource, sink, **kwargs):
        """Parse f as an N-Triples file."""
        assert sink.store.context_aware, ("NQuadsParser must be given"
                                          " a context aware store.")
        self.sink = ConjunctiveGraph(store=sink.store)

        source = inputsource.getByteStream()

        if not hasattr(source, 'read'):
            raise ParseError("Item to parse must be a file-like object.")

        source = getreader('utf-8')(source)

        self.file = source
        self.buffer = ''
        while True:
            self.line = __line = self.readline()
            if self.line is None:
                break
            try:
                self.parseline()
            except ParseError, msg:
                raise ParseError("Invalid line (%s):\n%r" % (msg, __line))

        return self.sink

    def parseline(self):
        self.eat(r_wspace)
        if (not self.line) or self.line.startswith(('#')):
            return  # The line is empty or a comment

        subject = self.subject()
        self.eat(r_wspace)

        predicate = self.predicate()
        self.eat(r_wspace)

        obj = self.object()
        self.eat(r_wspace)

        context = self.uriref() or self.nodeid()
        self.eat(r_tail)

        if self.line:
            raise ParseError("Trailing garbage")
        # Must have a context aware store - add on a normal Graph
        # discards anything where the ctx != graph.identifier
        self.sink.get_context(context).add((subject, predicate, obj))
