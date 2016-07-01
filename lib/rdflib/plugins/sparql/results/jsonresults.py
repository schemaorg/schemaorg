from rdflib.query import (
    Result, ResultException, ResultSerializer, ResultParser)
from rdflib import Literal, URIRef, BNode, Variable

from rdflib.py3compat import bytestype


import jsonlayer

"""A Serializer for SPARQL results in JSON:

http://www.w3.org/TR/rdf-sparql-json-res/

Bits and pieces borrowed from:
http://projects.bigasterisk.com/sparqlhttp/

Authors: Drew Perttula, Gunnar Aastrand Grimnes

"""


class JSONResultParser(ResultParser):

    def parse(self, source):
        inp = source.read()
        if isinstance(inp, bytestype):
            inp = inp.decode('utf-8')
        return JSONResult(jsonlayer.decode(inp))


class JSONResultSerializer(ResultSerializer):

    def __init__(self, result):
        ResultSerializer.__init__(self, result)

    def serialize(self, stream, encoding=None):

        res = {}
        if self.result.type == 'ASK':
            res["head"] = {}
            res["boolean"] = self.result.askAnswer
        else:
            # select
            res["results"] = {}
            res["head"] = {}
            res["head"]["vars"] = self.result.vars
            res["results"]["bindings"] = [self._bindingToJSON(
                x) for x in self.result.bindings]

        r = jsonlayer.encode(res)
        if encoding is not None:
            stream.write(r.encode(encoding))
        else:
            stream.write(r)

    def _bindingToJSON(self, b):
        res = {}
        for var in b:
            j = termToJSON(self, b[var])
            if j is not None:
                res[var] = termToJSON(self, b[var])
        return res


class JSONResult(Result):

    def __init__(self, json):
        self.json = json
        if "boolean" in json:
            type_ = 'ASK'
        elif "results" in json:
            type_ = 'SELECT'
        else:
            raise ResultException('No boolean or results in json!')

        Result.__init__(self, type_)

        if type_ == 'ASK':
            self.askAnswer = bool(json['boolean'])
        else:
            self.bindings = self._get_bindings()
            self.vars = [Variable(x) for x in json["head"]["vars"]]

    def _get_bindings(self):
        ret = []
        for row in self.json['results']['bindings']:
            outRow = {}
            for k, v in row.items():
                outRow[Variable(k)] = parseJsonTerm(v)
            ret.append(outRow)
        return ret


def parseJsonTerm(d):
    """rdflib object (Literal, URIRef, BNode) for the given json-format dict.

    input is like:
      { 'type': 'uri', 'value': 'http://famegame.com/2006/01/username' }
      { 'type': 'literal', 'value': 'drewp' }
    """

    t = d['type']
    if t == 'uri':
        return URIRef(d['value'])
    elif t == 'literal':
        if 'xml:lang' in d:
            return Literal(d['value'], lang=d['xml:lang'])
        return Literal(d['value'])
    elif t == 'typed-literal':
        return Literal(d['value'], datatype=URIRef(d['datatype']))
    elif t == 'bnode':
        return BNode(d['value'])
    else:
        raise NotImplementedError("json term type %r" % t)


def termToJSON(self, term):
    if isinstance(term, URIRef):
        return {'type': 'uri', 'value': unicode(term)}
    elif isinstance(term, Literal):
        if term.datatype is not None:
            return {'type': 'typed-literal',
                    'value': unicode(term),
                    'datatype': unicode(term.datatype)}
        else:
            r = {'type': 'literal',
                 'value': unicode(term)}
            if term.language is not None:
                r['xml:lang'] = term.language
            return r

    elif isinstance(term, BNode):
        return {'type': 'bnode', 'value': str(term)}
    elif term is None:
        return None
    else:
        raise ResultException(
            'Unknown term type: %s (%s)' % (term, type(term)))
