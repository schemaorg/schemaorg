# -*- coding: utf-8 -*-
"""
A collection of utilities for canonicalizing and inspecting graphs.

Among other things, they solve of the problem of deterministic bnode
comparisons.

Warning: the time to canonicalize bnodes may increase exponentially on
degenerate larger graphs. Use with care!

Example of comparing two graphs::

    >>> g1 = Graph().parse(format='n3', data='''
    ...     @prefix : <http://example.org/ns#> .
    ...     <http://example.org> :rel
    ...         <http://example.org/same>,
    ...         [ :label "Same" ],
    ...         <http://example.org/a>,
    ...         [ :label "A" ] .
    ... ''')
    >>> g2 = Graph().parse(format='n3', data='''
    ...     @prefix : <http://example.org/ns#> .
    ...     <http://example.org> :rel
    ...         <http://example.org/same>,
    ...         [ :label "Same" ],
    ...         <http://example.org/b>,
    ...         [ :label "B" ] .
    ... ''')
    >>>
    >>> iso1 = to_isomorphic(g1)
    >>> iso2 = to_isomorphic(g2)

These are not isomorphic::

    >>> iso1 == iso2
    False

Diff the two graphs::

    >>> in_both, in_first, in_second = graph_diff(iso1, iso2)

Present in both::

    >>> def dump_nt_sorted(g):
    ...     for l in sorted(g.serialize(format='nt').splitlines()):
    ...         if l: print(l.decode('ascii'))

    >>> dump_nt_sorted(in_both) #doctest: +SKIP
    <http://example.org>
        <http://example.org/ns#rel> <http://example.org/same> .
    <http://example.org>
        <http://example.org/ns#rel> _:cbcaabaaba17fecbc304a64f8edee4335e .
    _:cbcaabaaba17fecbc304a64f8edee4335e
        <http://example.org/ns#label> "Same" .

Only in first::

    >>> dump_nt_sorted(in_first) #doctest: +SKIP
    <http://example.org>
        <http://example.org/ns#rel> <http://example.org/a> .
    <http://example.org>
        <http://example.org/ns#rel> _:cb124e4c6da0579f810c0ffe4eff485bd9 .
    _:cb124e4c6da0579f810c0ffe4eff485bd9
        <http://example.org/ns#label> "A" .

Only in second::

    >>> dump_nt_sorted(in_second) #doctest: +SKIP
    <http://example.org>
        <http://example.org/ns#rel> <http://example.org/b> .
    <http://example.org>
        <http://example.org/ns#rel> _:cb558f30e21ddfc05ca53108348338ade8 .
    _:cb558f30e21ddfc05ca53108348338ade8
        <http://example.org/ns#label> "B" .
"""


# TODO:
# - Doesn't handle quads.
# - Add warning and/or safety mechanism before working on large graphs?
# - use this in existing Graph.isomorphic?

__all__ = ['IsomorphicGraph', 'to_isomorphic', 'isomorphic',
           'to_canonical_graph', 'graph_diff', 'similar']

from rdflib.graph import Graph, ConjunctiveGraph, ReadOnlyGraphAggregate
from rdflib.term import BNode, Node
try:
    import hashlib
    sha256 = hashlib.sha256
except ImportError:
    # for Python << 2.5
    import sha256
    sha256 = sha256.new

from datetime import datetime
from collections import defaultdict


def _total_seconds(td):
    result = td.days * 24 * 60 * 60
    result += td.seconds
    result += td.microseconds / 1000000.0
    return result


class _runtime(object):
    def __init__(self, label):
        self.label = label

    def __call__(self, f):
        if self.label is None:
            self.label = f.__name__ + "_runtime"

        def wrapped_f(*args, **kwargs):
            start = datetime.now()
            result = f(*args, **kwargs)
            if 'stats' in kwargs and kwargs['stats'] is not None:
                stats = kwargs['stats']
                stats[self.label] = _total_seconds(datetime.now() - start)
            return result
        return wrapped_f


class _call_count(object):
    def __init__(self, label):
        self.label = label

    def __call__(self, f):
        if self.label is None:
            self.label = f.__name__ + "_runtime"

        def wrapped_f(*args, **kwargs):
            if 'stats' in kwargs and kwargs['stats'] is not None:
                stats = kwargs['stats']
                if self.label not in stats:
                    stats[self.label] = 0
                stats[self.label] += 1
            return f(*args, **kwargs)
        return wrapped_f


class IsomorphicGraph(ConjunctiveGraph):
    """An implementation of the RGDA1 graph digest algorithm.

    An implementation of RGDA1 (publication forthcoming),
    a combination of Sayers & Karp's graph digest algorithm using
    sum and SHA-256 <http://www.hpl.hp.com/techreports/2003/HPL-2003-235R1.pdf>
    and traces <http://pallini.di.uniroma1.it>, an average case
    polynomial time algorithm for graph canonicalization.
    """

    def __init__(self, **kwargs):
        super(IsomorphicGraph, self).__init__(**kwargs)

    def __eq__(self, other):
        """Graph isomorphism testing."""
        if not isinstance(other, IsomorphicGraph):
            return False
        elif len(self) != len(other):
            return False
        return self.internal_hash() == other.internal_hash()

    def __ne__(self, other):
        """Negative graph isomorphism testing."""
        return not self.__eq__(other)

    def graph_digest(self, stats=None):
        """Synonym for IsomorphicGraph.internal_hash."""
        return self.internal_hash(stats=stats)

    def internal_hash(self, stats=None):
        """
        This is defined instead of __hash__ to avoid a circular recursion
        scenario with the Memory store for rdflib which requires a hash lookup
        in order to return a generator of triples.
        """
        return _TripleCanonicalizer(self).to_hash(stats=stats)


class Color:
    def __init__(self, nodes, hashfunc, color=(), hash_cache=None):
        if hash_cache is None:
            hash_cache = {}
        self._hash_cache = hash_cache
        self.color = color
        self.nodes = nodes
        self.hashfunc = hashfunc
        self._hash_color = None

    def key(self):
        return (len(self.nodes), self.hash_color())

    def hash_color(self, color=None):
        if color is None:
            color = self.color
        if color in self._hash_cache:
            return self._hash_cache[color]

        def stringify(x):
            if isinstance(x, Node):
                return x.n3()
            else:
                return unicode(x)
        if isinstance(color, Node):
            return stringify(color)
        value = 0
        for triple in color:
            value += self.hashfunc(' '.join([stringify(x) for x in triple]))
        val = u"%x" % value
        self._hash_cache[color] = val
        return val

    def distinguish(self, W, graph):
        colors = {}
        for n in self.nodes:
            new_color = list(self.color)
            for node in W.nodes:
                new_color += [
                    (1, p, W.hash_color())
                    for s, p, o in graph.triples((n, None, node))]
                new_color += [
                    (W.hash_color(), p, 3)
                    for s, p, o in graph.triples((node, None, n))]
            new_color = tuple(new_color)
            new_hash_color = self.hash_color(new_color)

            if new_hash_color not in colors:
                c = Color(
                    [], self.hashfunc, new_color,
                    hash_cache=self._hash_cache)
                colors[new_hash_color] = c
            colors[new_hash_color].nodes.append(n)
        return colors.values()

    def discrete(self):
        return len(self.nodes) == 1

    def copy(self):
        return Color(
            self.nodes[:], self.hashfunc, self.color,
            hash_cache=self._hash_cache)


class _TripleCanonicalizer(object):

    def __init__(self, graph, hashfunc=sha256):
        self.graph = graph

        def _hashfunc(s):
            h = hashfunc()
            h.update(unicode(s).encode("utf8"))
            return int(h.hexdigest(), 16)
        self._hash_cache = {}
        self.hashfunc = _hashfunc


    def _discrete(self, coloring):
        return len([c for c in coloring if not c.discrete()]) == 0


    def _initial_color(self):
        """Finds an initial color for the graph.

        Finds an initial color fo the graph by finding all blank nodes and
        non-blank nodes that are adjacent. Nodes that are not adjacent to blank
        nodes are not included, as they are a) already colored (by URI or literal)
        and b) do not factor into the color of any blank node.
        """
        bnodes = set()
        others = set()
        self._neighbors = defaultdict(set)
        for s, p, o in self.graph:
            nodes = set([s, o])
            b = set([x for x in nodes if isinstance(x, BNode)])
            if len(b) > 0:
                others |= nodes - b
                bnodes |= b
                if isinstance(s, BNode):
                    self._neighbors[s].add(o)
                if isinstance(o, BNode):
                    self._neighbors[o].add(s)
        if len(bnodes) > 0:
            return [
                    Color(list(bnodes), self.hashfunc, hash_cache=self._hash_cache)
                ] + [
                    Color([x], self.hashfunc, x, hash_cache=self._hash_cache)
                    for x in others
                ]
        else:
            return []

    def _individuate(self, color, individual):
        new_color = list(color.color)
        new_color.append((len(color.nodes),))

        color.nodes.remove(individual)
        c = Color([individual], self.hashfunc, tuple(new_color),
                  hash_cache=self._hash_cache)
        return c

    def _get_candidates(self, coloring):
        candidates = [c for c in coloring if not c.discrete()]
        for c in [c for c in coloring if not c.discrete()]:
            for node in c.nodes:
                yield node, c

    def _refine(self, coloring, sequence):
        sequence = sorted(sequence, key=lambda x: x.key(), reverse=True)
        coloring = coloring[:]
        while len(sequence) > 0 and not self._discrete(coloring):
            W = sequence.pop()
            for c in coloring[:]:
                if len(c.nodes) > 1:
                    colors = sorted(c.distinguish(W, self.graph),
                                    key=lambda x: x.key(),
                                    reverse=True)
                    coloring.remove(c)
                    coloring.extend(colors)
                    try:
                        si = sequence.index(c)
                        sequence = sequence[:si] + colors + sequence[si+1:]
                    except ValueError:
                        sequence = colors[1:] + sequence

        return coloring

    @_runtime("to_hash_runtime")
    def to_hash(self, stats=None):
        result = 0
        for triple in self.canonical_triples(stats=stats):
            result += self.hashfunc(' '.join([x.n3() for x in triple]))
        if stats is not None:
            stats['graph_digest'] = "%x" % result
        return result

    def _experimental_path(self, coloring):
        coloring = [c.copy() for c in coloring]
        while not self._discrete(coloring):
            color = [x for x in coloring if not x.discrete()][0]
            node = color.nodes[0]
            new_color = self._individuate(color, node)
            coloring.append(new_color)
            coloring = self._refine(coloring, [new_color])
        return coloring

    def _create_generator(self, colorings, groupings=None):
        if not groupings:
            groupings = defaultdict(set)
        for group in zip(*colorings):
            g = set([c.nodes[0] for c in group])
            for n in group:
                g |= groupings[n]
            for n in g:
                groupings[n] = g
        return groupings

    @_call_count("individuations")
    def _traces(self, coloring, stats=None, depth=[0]):
        if stats is not None and 'prunings' not in stats:
            stats['prunings'] = 0
        depth[0] += 1
        candidates = self._get_candidates(coloring)
        best = []
        best_score = None
        best_experimental = None
        best_experimental_score = None
        last_coloring = None
        generator = defaultdict(set)
        visited = set()
        for candidate, color in candidates:
            if candidate in generator:
                v = generator[candidate] & visited
                if len(v) > 0:
                    visited.add(candidate)
                    continue
            visited.add(candidate)
            coloring_copy = []
            color_copy = None
            for c in coloring:
                c_copy = c.copy()
                coloring_copy.append(c_copy)
                if c == color:
                    color_copy = c_copy
            new_color = self._individuate(color_copy, candidate)
            coloring_copy.append(new_color)
            refined_coloring = self._refine(coloring_copy, [new_color])
            color_score = tuple([c.key() for c in refined_coloring])
            experimental = self._experimental_path(coloring_copy)
            experimental_score = set([c.key() for c in experimental])
            if last_coloring:
                generator = self._create_generator(
                    [last_coloring, experimental],
                    generator)
            last_coloring = experimental
            if best_score is None or best_score < color_score:
                best = [refined_coloring]
                best_score = color_score
                best_experimental = experimental
                best_experimental_score = experimental_score
            elif best_score > color_score:
                # prune this branch.
                if stats is not None:
                    stats['prunings'] += 1
            elif experimental_score != best_experimental_score:
                best.append(refined_coloring)
            else:
                # prune this branch.
                if stats is not None:
                    stats['prunings'] += 1
        discrete = [x for x in best if self._discrete(x)]
        if len(discrete) == 0:
            best_score = None
            best_depth = None
            for coloring in best:
                d = [depth[0]]
                new_color = self._traces(coloring, stats=stats, depth=d)
                color_score = tuple([c.key() for c in refined_coloring])
                if best_score is None or color_score > best_score:
                    discrete = [new_color]
                    best_score = color_score
                    best_depth = d[0]
            depth[0] = best_depth
        return discrete[0]

    def canonical_triples(self, stats=None):
        if stats is not None:
            start_canonicalization = datetime.now()
        if stats is not None:
            start_coloring = datetime.now()
        coloring = self._initial_color()
        if stats is not None:
            stats['triple_count'] = len(self.graph)
            stats['adjacent_nodes'] = max(0, len(coloring) - 1)
        coloring = self._refine(coloring, coloring[:])
        if stats is not None:
            stats['initial_coloring_runtime'] = _total_seconds(datetime.now() - start_coloring)
            stats['initial_color_count'] = len(coloring)

        if not self._discrete(coloring):
            depth = [0]
            coloring = self._traces(coloring, stats=stats, depth=depth)
            if stats is not None:
                stats['tree_depth'] = depth[0]
        elif stats is not None:
            stats['individuations'] = 0
            stats['tree_depth'] = 0
        if stats is not None:
            stats['color_count'] = len(coloring)

        bnode_labels = dict([(c.nodes[0], c.hash_color()) for c in coloring])
        if stats is not None:
            stats["canonicalize_triples_runtime"] = _total_seconds(datetime.now() - start_coloring)
        for triple in self.graph:
            result = tuple(self._canonicalize_bnodes(triple, bnode_labels))
            yield result

    def _canonicalize_bnodes(self, triple, labels):
        for term in triple:
            if isinstance(term, BNode):
                yield BNode(value="cb%s" % labels[term])
            else:
                yield term


def to_isomorphic(graph):
    if isinstance(graph, IsomorphicGraph):
        return graph
    return IsomorphicGraph(store=graph.store)


def isomorphic(graph1, graph2):
    """Compare graph for equality.

    Uses an algorithm to compute unique hashes which takes bnodes into account.

    Examples::

        >>> g1 = Graph().parse(format='n3', data='''
        ...     @prefix : <http://example.org/ns#> .
        ...     <http://example.org> :rel <http://example.org/a> .
        ...     <http://example.org> :rel <http://example.org/b> .
        ...     <http://example.org> :rel [ :label "A bnode." ] .
        ... ''')
        >>> g2 = Graph().parse(format='n3', data='''
        ...     @prefix ns: <http://example.org/ns#> .
        ...     <http://example.org> ns:rel [ ns:label "A bnode." ] .
        ...     <http://example.org> ns:rel <http://example.org/b>,
        ...             <http://example.org/a> .
        ... ''')
        >>> isomorphic(g1, g2)
        True

        >>> g3 = Graph().parse(format='n3', data='''
        ...     @prefix : <http://example.org/ns#> .
        ...     <http://example.org> :rel <http://example.org/a> .
        ...     <http://example.org> :rel <http://example.org/b> .
        ...     <http://example.org> :rel <http://example.org/c> .
        ... ''')
        >>> isomorphic(g1, g3)
        False
    """
    gd1 = _TripleCanonicalizer(graph1).to_hash()
    gd2 = _TripleCanonicalizer(graph2).to_hash()
    return gd1 == gd2



def to_canonical_graph(g1):
    """Creates a canonical, read-only graph.

    Creates a canonical, read-only graph where all bnode id:s are based on
    deterministical SHA-256 checksums, correlated with the graph contents.
    """
    graph = Graph()
    graph += _TripleCanonicalizer(g1).canonical_triples()
    return ReadOnlyGraphAggregate([graph])


def graph_diff(g1, g2):
    """Returns three sets of triples: "in both", "in first" and "in second"."""
    # bnodes have deterministic values in canonical graphs:
    cg1 = to_canonical_graph(g1)
    cg2 = to_canonical_graph(g2)
    in_both = cg1 * cg2
    in_first = cg1 - cg2
    in_second = cg2 - cg1
    return (in_both, in_first, in_second)



_MOCK_BNODE = BNode()


def similar(g1, g2):
    """Checks if the two graphs are "similar".

    Checks if the two graphs are "similar", by comparing sorted triples where
    all bnodes have been replaced by a singular mock bnode (the
    ``_MOCK_BNODE``).

    This is a much cheaper, but less reliable, alternative to the comparison
    algorithm in ``isomorphic``.
    """
    return all(t1 == t2 for (t1, t2) in _squashed_graphs_triples(g1, g2))


def _squashed_graphs_triples(g1, g2):
    for (t1, t2) in zip(sorted(_squash_graph(g1)), sorted(_squash_graph(g2))):
        yield t1, t2


def _squash_graph(graph):
    return (_squash_bnodes(triple) for triple in graph)


def _squash_bnodes(triple):
    return tuple((isinstance(t, BNode) and _MOCK_BNODE) or t for t in triple)
