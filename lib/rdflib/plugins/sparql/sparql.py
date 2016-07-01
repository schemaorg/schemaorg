import collections
import itertools
import datetime

from rdflib.namespace import NamespaceManager
from rdflib import Variable, BNode, Graph, ConjunctiveGraph, URIRef, Literal
from rdflib.term import Node

from parserutils import CompValue

import rdflib.plugins.sparql
from rdflib.plugins.sparql.compat import Mapping, MutableMapping


class SPARQLError(Exception):
    def __init__(self, msg=None):
        Exception.__init__(self, msg)


class NotBoundError(SPARQLError):
    def __init__(self, msg=None):
        SPARQLError.__init__(self, msg)


class AlreadyBound(SPARQLError):
    """Raised when trying to bind a variable that is already bound!"""
    def __init__(self):
        SPARQLError.__init__(self)


class SPARQLTypeError(SPARQLError):
    def __init__(self, msg):
        SPARQLError.__init__(self, msg)


class Bindings(MutableMapping):

    """

    A single level of a stack of variable-value bindings.
    Each dict keeps a reference to the dict below it,
    any failed lookup is propegated back

    In python 3.3 this could be a collections.ChainMap
    """

    def __init__(self, outer=None, d=[]):
        self._d = dict(d)
        self.outer = outer

    def __getitem__(self, key):
        try:
            return self._d[key]
        except KeyError:
            if not self.outer:
                raise
            return self.outer[key]

    def __contains__(self, key):
        try:
            self[key]
            return True
        except KeyError:
            return False

    def __setitem__(self, key, value):
        self._d[key] = value

    def __delitem__(self, key):
        raise Exception("DelItem is not implemented!")

    def __len__(self):
        i = 0
        for x in self:
            i += 1
        return i

    def __iter__(self):
        d = self
        while d is not None:
            for i in dict.__iter__(d._d):
                yield i
            d = d.outer

    def __str__(self):
        return "Bindings({"+", ".join((k, self[k]) for k in self)+"})"

    def __repr__(self):
        return unicode(self)


class FrozenDict(Mapping):
    """
    An immutable hashable dict

    Taken from http://stackoverflow.com/a/2704866/81121

    """
    def __init__(self, *args, **kwargs):
        self._d = dict(*args, **kwargs)
        self._hash = None

    def __iter__(self):
        return iter(self._d)

    def __len__(self):
        return len(self._d)

    def __getitem__(self, key):
        return self._d[key]

    def __hash__(self):
        # It would have been simpler and maybe more obvious to
        # use hash(tuple(sorted(self._d.iteritems()))) from this discussion
        # so far, but this solution is O(n). I don't know what kind of
        # n we are going to run into, but sometimes it's hard to resist the
        # urge to optimize when it will gain improved algorithmic performance.
        if self._hash is None:
            self._hash = 0
            for key, value in self.iteritems():
                self._hash ^= hash(key)
                self._hash ^= hash(value)
        return self._hash

    def project(self, vars):
        return FrozenDict(
            (x for x in self.iteritems() if x[0] in vars))

    def disjointDomain(self, other):
        return not bool(set(self).intersection(other))

    def compatible(self, other):
        for k in self:
            try:
                if self[k] != other[k]:
                    return False
            except KeyError:
                pass

        return True

    def merge(self, other):
        res = FrozenDict(
            itertools.chain(self.iteritems(), other.iteritems()))

        return res

    def __str__(self):
        return str(self._d)

    def __repr__(self):
        return repr(self._d)


class FrozenBindings(FrozenDict):

    def __init__(self, ctx, *args, **kwargs):
        FrozenDict.__init__(self, *args, **kwargs)
        self.ctx = ctx

    def __getitem__(self, key):

        if not isinstance(key, Node):
            key = Variable(key)

        if not type(key) in (BNode, Variable):
            return key

        return self._d[key]

    def project(self, vars):
        return FrozenBindings(
            self.ctx, (x for x in self.iteritems() if x[0] in vars))

    def merge(self, other):
        res = FrozenBindings(
            self.ctx, itertools.chain(self.iteritems(), other.iteritems()))

        return res

    def _now(self):
        return self.ctx.now

    def _bnodes(self):
        return self.ctx.bnodes

    def _prologue(self):
        return self.ctx.prologue

    prologue = property(_prologue)
    bnodes = property(_bnodes)
    now = property(_now)

    def forget(self, before):
        """
        return a frozen dict only of bindings made in self
        since before
        """

        return FrozenBindings(self.ctx, (x for x in self.iteritems() if before[x[0]] is None))

    def remember(self, these):
        """
        return a frozen dict only of bindings in these
        """
        return FrozenBindings(self.ctx, (x for x in self.iteritems() if x[0] in these))


class QueryContext(object):

    """
    Query context - passed along when evaluating the query
    """

    def __init__(self, graph=None, bindings=None):
        self.bindings = bindings or Bindings()

        if isinstance(graph, ConjunctiveGraph):
            self._dataset = graph
            if rdflib.plugins.sparql.SPARQL_DEFAULT_GRAPH_UNION:
                self.graph = self.dataset
            else:
                self.graph = self.dataset.default_context
        else:
            self._dataset = None
            self.graph = graph

        self.prologue = None
        self.now = datetime.datetime.now()

        self.bnodes = collections.defaultdict(BNode)

    def clone(self, bindings=None):
        r = QueryContext(
            self._dataset if self._dataset is not None else self.graph)
        r.prologue = self.prologue
        r.bindings.update(bindings or self.bindings)
        r.graph = self.graph
        r.bnodes = self.bnodes
        return r

    def _get_dataset(self):
        if self._dataset is None:
            raise Exception(
                'You performed a query operation requiring ' +
                'a dataset (i.e. ConjunctiveGraph), but ' +
                'operating currently on a single graph.')
        return self._dataset

    dataset = property(_get_dataset, doc="current dataset")

    def load(self, source, default=False, **kwargs):

        def _load(graph, source):
            try:
                return graph.load(source, **kwargs)
            except:
                pass
            try:
                return graph.load(source, format='n3', **kwargs)
            except:
                pass
            try:
                return graph.load(source, format='nt', **kwargs)
            except:
                raise Exception(
                    "Could not load %s as either RDF/XML, N3 or NTriples" % (
                    source))

        if not rdflib.plugins.sparql.SPARQL_LOAD_GRAPHS:
            # we are not loading - if we already know the graph
            # being "loaded", just add it to the default-graph
            if default:
                self.graph += self.dataset.get_context(source)
        else:

            if default:
                _load(self.graph, source)
            else:
                _load(self.dataset, source)

    def __getitem__(self, key):
        # in SPARQL BNodes are just labels
        if not type(key) in (BNode, Variable):
            return key
        try:
            return self.bindings[key]
        except KeyError:
            return None

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def solution(self, vars=None):
        """
        Return a static copy of the current variable bindings as dict
        """
        if vars:
            return FrozenBindings(
                self, ((k, v)
                       for k, v in self.bindings.iteritems()
                       if k in vars))
        else:
            return FrozenBindings(self, self.bindings.iteritems())

    def __setitem__(self, key, value):
        if key in self.bindings and self.bindings[key] != value:
            raise AlreadyBound()

        self.bindings[key] = value

    def pushGraph(self, graph):
        r = self.clone()
        r.graph = graph
        return r

    def push(self):
        r = self.clone(Bindings(self.bindings))
        return r

    def clean(self):
        return self.clone([])

    # def pop(self):
    #     self.bindings = self.bindings.outer
    #     if self.bindings is None:
    #         raise Exception("We've bottomed out of the bindings stack!")

    def thaw(self, frozenbindings):
        """
        Create a new read/write query context from the given solution
        """
        c = self.clone(frozenbindings)

        return c


class Prologue:

    """
    A class for holding prefixing bindings and base URI information
    """

    def __init__(self):
        self.base = None
        self.namespace_manager = NamespaceManager(
            Graph())  # ns man needs a store

    def resolvePName(self, prefix, localname):
        ns = self.namespace_manager.store.namespace(prefix or "")
        if ns is None:
            raise Exception('Unknown namespace prefix : %s' % prefix)
        return URIRef(ns + (localname or ""))

    def bind(self, prefix, uri):
        self.namespace_manager.bind(prefix, uri, replace=True)

    def absolutize(self, iri):

        """
        Apply BASE / PREFIXes to URIs
        (and to datatypes in Literals)

        TODO: Move resolving URIs to pre-processing
        """

        if isinstance(iri, CompValue):
            if iri.name == 'pname':
                return self.resolvePName(iri.prefix, iri.localname)
            if iri.name == 'literal':
                return Literal(
                    iri.string, lang=iri.lang,
                    datatype=self.absolutize(iri.datatype))
        elif isinstance(iri, URIRef) and not ':' in iri:  # TODO: Check for relative URI?
            return URIRef(self.base + iri)
        return iri


class Query:
    """
    A parsed and translated query
    """

    def __init__(self, prologue, algebra):
        self.prologue = prologue
        self.algebra = algebra
