from rdflib.serializer import Serializer
from rdflib.plugins.serializers.xmlwriter import XMLWriter

from rdflib.term import URIRef, Literal, BNode
from rdflib.namespace import Namespace

from rdflib.graph import Graph, ConjunctiveGraph

from rdflib.py3compat import b

__all__ = ['TriXSerializer']

## TODO: MOve this somewhere central
TRIXNS = Namespace("http://www.w3.org/2004/03/trix/trix-1/")
XMLNS = Namespace("http://www.w3.org/XML/1998/namespace")


class TriXSerializer(Serializer):
    def __init__(self, store):
        super(TriXSerializer, self).__init__(store)
        if not store.context_aware:
            raise Exception(
                "TriX serialization only makes sense for context-aware stores")

    def serialize(self, stream, base=None, encoding=None, **args):

        nm = self.store.namespace_manager

        self.writer = XMLWriter(stream, nm, encoding, extra_ns={"": TRIXNS})

        self.writer.push(TRIXNS[u"TriX"])
        self.writer.namespaces()

        if isinstance(self.store, ConjunctiveGraph):
            for subgraph in self.store.contexts():
                self._writeGraph(subgraph)
        elif isinstance(self.store, Graph):
            self._writeGraph(self.store)
        else:
            raise Exception("Unknown graph type: " + type(self.store))

        self.writer.pop()
        stream.write(b("\n"))

    def _writeGraph(self, graph):
        self.writer.push(TRIXNS[u"graph"])
        if isinstance(graph.identifier, URIRef):
            self.writer.element(
                TRIXNS[u"uri"], content=unicode(graph.identifier))

        for triple in graph.triples((None, None, None)):
            self._writeTriple(triple)
        self.writer.pop()

    def _writeTriple(self, triple):
        self.writer.push(TRIXNS[u"triple"])
        for component in triple:
            if isinstance(component, URIRef):
                self.writer.element(TRIXNS[u"uri"],
                                    content=unicode(component))
            elif isinstance(component, BNode):
                self.writer.element(TRIXNS[u"id"],
                                    content=unicode(component))
            elif isinstance(component, Literal):
                if component.datatype:
                    self.writer.element(TRIXNS[u"typedLiteral"],
                                        content=unicode(component),
                                        attributes={TRIXNS[u"datatype"]:
                                                    unicode(
                                                        component.datatype)})
                elif component.language:
                    self.writer.element(TRIXNS[u"plainLiteral"],
                                        content=unicode(component),
                                        attributes={XMLNS[u"lang"]:
                                                    unicode(
                                                        component.language)})
                else:
                    self.writer.element(TRIXNS[u"plainLiteral"],
                                        content=unicode(component))
        self.writer.pop()
