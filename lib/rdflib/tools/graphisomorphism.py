"""
A commandline tool for testing if RDF graphs are isomorpic, i.e. equal
if BNode labels are ignored.
"""

from rdflib.graph import Graph
from rdflib import BNode
try:
    from itertools import combinations
    assert combinations
except ImportError:  # Python == 2.5
    # Copied from
    # http://docs.python.org/2/library/itertools.html#itertools.combinations
    def combinations(iterable, r):
        # combinations('ABCD', 2) --> AB AC AD BC BD CD
        # combinations(range(4), 3) --> 012 013 023 123
        pool = tuple(iterable)
        n = len(pool)
        if r > n:
            return
        indices = range(r)
        yield tuple(pool[i] for i in indices)
        while True:
            for i in reversed(range(r)):
                if indices[i] != i + n - r:
                    break
            else:
                return
            indices[i] += 1
            for j in range(i + 1, r):
                indices[j] = indices[j - 1] + 1
            yield tuple(pool[i] for i in indices)


class IsomorphicTestableGraph(Graph):
    """
    Ported from:
    http://www.w3.org/2001/sw/DataAccess/proto-tests/tools/rdfdiff.py
    (Sean B Palmer's RDF Graph Isomorphism Tester)
    """
    def __init__(self, **kargs):
        super(IsomorphicTestableGraph, self).__init__(**kargs)
        self.hash = None

    def internal_hash(self):
        """
        This is defined instead of __hash__ to avoid a circular recursion
        scenario with the Memory store for rdflib which requires a hash
        lookup in order to return a generator of triples
        """
        return hash(tuple(sorted(self.hashtriples())))

    def hashtriples(self):
        for triple in self:
            g = ((isinstance(t, BNode) and self.vhash(t)) or t for t in triple)
            yield hash(tuple(g))

    def vhash(self, term, done=False):
        return tuple(sorted(self.vhashtriples(term, done)))

    def vhashtriples(self, term, done):
        for t in self:
            if term in t:
                yield tuple(self.vhashtriple(t, term, done))

    def vhashtriple(self, triple, term, done):
        for p in xrange(3):
            if not isinstance(triple[p], BNode):
                yield triple[p]
            elif done or (triple[p] == term):
                yield p
            else:
                yield self.vhash(triple[p], done=True)

    def __eq__(self, G):
        """Graph isomorphism testing."""
        if not isinstance(G, IsomorphicTestableGraph):
            return False
        elif len(self) != len(G):
            return False
        elif list.__eq__(list(self), list(G)):
            return True  # @@
        return self.internal_hash() == G.internal_hash()

    def __ne__(self, G):
        """Negative graph isomorphism testing."""
        return not self.__eq__(G)


def main():
    import sys
    from optparse import OptionParser
    usage = '''usage: %prog [options] file1 file2 ... fileN'''
    op = OptionParser(usage=usage)
    op.add_option('-s', '--stdin', action='store_true', default=False,
                  help='Load from STDIN as well')
    op.add_option('--format',
                  default='xml',
                  dest='inputFormat',
                  metavar='RDF_FORMAT',
                  choices=['xml', 'trix', 'n3', 'nt', 'rdfa'],
                  help="The format of the RDF document(s) to compare" +
                  "One of 'xml','n3','trix', 'nt', " +
                  "or 'rdfa'.  The default is %default")

    (options, args) = op.parse_args()

    graphs = []
    graph2FName = {}
    if options.stdin:
        graph = IsomorphicTestableGraph().parse(
            sys.stdin, format=options.inputFormat)
        graphs.append(graph)
        graph2FName[graph] = '(STDIN)'
    for fn in args:
        graph = IsomorphicTestableGraph().parse(
            fn, format=options.inputFormat)
        graphs.append(graph)
        graph2FName[graph] = fn
    checked = set()
    for graph1, graph2 in combinations(graphs, 2):
        if (graph1, graph2) not in checked and (graph2, graph1) not in checked:
            assert graph1 == graph2, "%s != %s" % (
                graph2FName[graph1], graph2FName[graph2])

if __name__ == '__main__':
    main()
