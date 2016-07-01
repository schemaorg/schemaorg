"""

This module implements a parser and serializer for the CSV SPARQL result
formats

http://www.w3.org/TR/sparql11-results-csv-tsv/

"""

import codecs
import csv

from rdflib import Variable, BNode, URIRef, Literal, py3compat

from rdflib.query import Result, ResultSerializer, ResultParser


class CSVResultParser(ResultParser):
    def __init__(self):
        self.delim = ","

    def parse(self, source):

        r = Result('SELECT')

        if isinstance(source.read(0), py3compat.bytestype):
            # if reading from source returns bytes do utf-8 decoding
            source = codecs.getreader('utf-8')(source)

        reader = csv.reader(source, delimiter=self.delim)
        r.vars = [Variable(x) for x in reader.next()]
        r.bindings = []

        for row in reader:
            r.bindings.append(self.parseRow(row, r.vars))

        return r

    def parseRow(self, row, v):
        return dict((var, val)
                    for var, val in zip(v, [self.convertTerm(t)
                                            for t in row]) if val is not None)

    def convertTerm(self, t):
        if t == "":
            return None
        if t.startswith("_:"):
            return BNode(t)  # or generate new IDs?
        if t.startswith("http://") or t.startswith("https://"):  # TODO: more?
            return URIRef(t)
        return Literal(t)


class CSVResultSerializer(ResultSerializer):

    def __init__(self, result):
        ResultSerializer.__init__(self, result)

        self.delim = ","
        if result.type != "SELECT":
            raise Exception(
                "CSVSerializer can only serialize select query results")

    def serialize(self, stream, encoding='utf-8'):

        if py3compat.PY3:
            # the serialiser writes bytes in the given encoding
            # in py3 csv.writer is unicode aware and writes STRINGS,
            # so we encode afterwards
            # in py2 it breaks when passed unicode strings,
            # and must be passed utf8, so we encode before

            import codecs
            stream = codecs.getwriter(encoding)(stream)

        out = csv.writer(stream, delimiter=self.delim)

        vs = [self.serializeTerm(v, encoding) for v in self.result.vars]
        out.writerow(vs)
        for row in self.result.bindings:
            out.writerow([self.serializeTerm(
                row.get(v), encoding) for v in self.result.vars])

    def serializeTerm(self, term, encoding):
        if term is None:
            return ""
        if not py3compat.PY3:
            return term.encode(encoding)
        else:
            return term
