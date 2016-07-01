from rdflib import ConjunctiveGraph
from rdflib.parser import Parser
from .notation3 import SinkParser, RDFSink


def becauseSubGraph(*args, **kwargs): pass


class TrigSinkParser(SinkParser):

    def directiveOrStatement(self, argstr, h):

        #import pdb; pdb.set_trace()

        i = self.skipSpace(argstr, h)
        if i < 0:
            return i    # EOF

        j = self.graph(argstr, i)
        if j >= 0:
            return j

        j = self.sparqlDirective(argstr, i)
        if j >= 0:
            return j

        j = self.directive(argstr, i)
        if j >= 0:
            return self.checkDot(argstr, j)

        j = self.statement(argstr, i)
        if j >= 0:
            return self.checkDot(argstr, j)


        return j

    def labelOrSubject(self, argstr, i, res):
        j = self.skipSpace(argstr, i)
        if j < 0:
            return j  # eof
        i = j

        j = self.uri_ref2(argstr, i, res)
        if j >= 0:
            return j

        if argstr[i] == '[':
            j = self.skipSpace(argstr, i+1)
            if j < 0:
                self.BadSyntax(argstr, i,
                    "Expected ] got EOF")
            if argstr[j] == ']':
                res.append(self.blankNode())
                return j+1
        return -1

    def graph(self, argstr, i):
        """
        Parse trig graph, i.e.

           <urn:graphname> = { .. triples .. }

        return -1 if it doesn't look like a graph-decl
        raise Exception if it looks like a graph, but isn't.
        """

        #import pdb; pdb.set_trace()
        j = self.sparqlTok('GRAPH', argstr, i) # optional GRAPH keyword
        if j >= 0: i = j

        r = []
        j = self.labelOrSubject(argstr, i, r)
        if j >= 0:
            graph = r[0]
            i = j
        else:
            graph = self._store.graph.identifier # hack


        j = self.skipSpace(argstr, i)
        if j < 0:
            self.BadSyntax(argstr, i,
                           "EOF found when expected graph")

        if argstr[j:j + 1] == "=": # optional = for legacy support

            i = self.skipSpace(argstr, j + 1)
            if i < 0:
                self.BadSyntax(argstr, i, "EOF found when expecting '{'")
        else:
            i = j

        if argstr[i:i+1] != "{":
            return -1 # the node wasn't part of a graph


        j = i+1

        oldParentContext = self._parentContext
        self._parentContext = self._context
        reason2 = self._reason2
        self._reason2 = becauseSubGraph
        self._context = self._store.newGraph(graph)

        while 1:
            i = self.skipSpace(argstr, j)
            if i < 0:
                self.BadSyntax(
                    argstr, i, "needed '}', found end.")

            if argstr[i:i + 1] == "}":
                j = i + 1
                break

            j = self.directiveOrStatement(argstr, i)
            if j < 0:
                self.BadSyntax(
                    argstr, i, "expected statement or '}'")

        self._context = self._parentContext
        self._reason2 = reason2
        self._parentContext = oldParentContext
        #res.append(subj.close())    # No use until closed
        return j




class TrigParser(Parser):
    """
    An RDFLib parser for TriG

    """

    def __init__(self):
        pass

    def parse(self, source, graph, encoding="utf-8"):

        if encoding not in [None, "utf-8"]:
            raise Exception(
                ("TriG files are always utf-8 encoded, ",
                 "I was passed: %s") % encoding)

        # we're currently being handed a Graph, not a ConjunctiveGraph
        assert graph.store.context_aware, "TriG Parser needs a context-aware store!"

        conj_graph = ConjunctiveGraph(store=graph.store)
        conj_graph.default_context = graph  # TODO: CG __init__ should have a
                                            # default_context arg
         # TODO: update N3Processor so that it can use conj_graph as the sink
        conj_graph.namespace_manager = graph.namespace_manager

        sink = RDFSink(conj_graph)

        baseURI = conj_graph.absolutize(
            source.getPublicId() or source.getSystemId() or "")
        p = TrigSinkParser(sink, baseURI=baseURI, turtle=True)

        p.loadStream(source.getByteStream())

        for prefix, namespace in p._bindings.items():
            conj_graph.bind(prefix, namespace)

        # return ???
