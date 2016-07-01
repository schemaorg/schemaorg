from rdflib import Graph, Namespace, RDF, Variable

from rdflib.query import Result, ResultParser

RS = Namespace('http://www.w3.org/2001/sw/DataAccess/tests/result-set#')


class RDFResultParser(ResultParser):
    def parse(self, source, **kwargs):
        return RDFResult(source, **kwargs)


class RDFResult(Result):

    def __init__(self, source, **kwargs):

        if not isinstance(source, Graph):
            graph = Graph()
            graph.load(source, **kwargs)
        else:
            graph = source

        rs = graph.value(predicate=RDF.type, object=RS.ResultSet)
                         # there better be only one :)

        if rs is None:
            type_ = 'CONSTRUCT'

            # use a new graph
            g = Graph()
            g += graph

        else:

            askAnswer = graph.value(rs, RS.boolean)

            if askAnswer is not None:
                type_ = 'ASK'
            else:
                type_ = 'SELECT'

        Result.__init__(self, type_)

        if type_ == 'SELECT':
            self.vars = [Variable(v) for v in graph.objects(rs,
                                                            RS.resultVariable)]

            self.bindings = []

            for s in graph.objects(rs, RS.solution):
                sol = {}
                for b in graph.objects(s, RS.binding):
                    sol[Variable(graph.value(
                        b, RS.variable))] = graph.value(b, RS.value)
                self.bindings.append(sol)
        elif type_ == 'ASK':
            self.askAnswer = askAnswer.value
            if askAnswer.value == None:
                raise Exception('Malformed boolean in ask answer!')
        elif type_ == 'CONSTRUCT':
            self.graph = g
