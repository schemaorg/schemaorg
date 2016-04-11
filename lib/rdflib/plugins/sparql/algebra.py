
"""
Converting the 'parse-tree' output of pyparsing to a SPARQL Algebra expression

http://www.w3.org/TR/sparql11-query/#sparqlQuery

"""

import functools
import operator
import collections

from rdflib import Literal, Variable, URIRef, BNode

from rdflib.plugins.sparql.sparql import Prologue, Query
from rdflib.plugins.sparql.parserutils import CompValue, Expr
from rdflib.plugins.sparql.operators import (
    and_, TrueFilter, simplify as simplifyFilters)
from rdflib.paths import (
    InvPath, AlternativePath, SequencePath, MulPath, NegatedPath)

from pyparsing import ParseResults


# ---------------------------
# Some convenience methods
def OrderBy(p, expr):
    return CompValue('OrderBy', p=p, expr=expr)


def ToMultiSet(p):
    return CompValue('ToMultiSet', p=p)


def Union(p1, p2):
    return CompValue('Union', p1=p1, p2=p2)


def Join(p1, p2):
    return CompValue('Join', p1=p1, p2=p2)


def Minus(p1, p2):
    return CompValue('Minus', p1=p1, p2=p2)


def Graph(term, graph):
    return CompValue('Graph', term=term, p=graph)


def BGP(triples=None):
    return CompValue('BGP', triples=triples or [])


def LeftJoin(p1, p2, expr):
    return CompValue('LeftJoin', p1=p1, p2=p2, expr=expr)


def Filter(expr, p):
    return CompValue('Filter', expr=expr, p=p)


def Extend(p, expr, var):
    return CompValue('Extend', p=p, expr=expr, var=var)


def Project(p, PV):
    return CompValue('Project', p=p, PV=PV)


def Group(p, expr=None):
    return CompValue('Group', p=p, expr=expr)


def _knownTerms(triple, varsknown, varscount):
    return (len(filter(None, (x not in varsknown and
                              isinstance(
                                  x, (Variable, BNode)) for x in triple))),
            -sum(varscount.get(x, 0) for x in triple),
            not isinstance(triple[2], Literal),
            )


def reorderTriples(l):
    """
    Reorder triple patterns so that we execute the
    ones with most bindings first
    """

    def _addvar(term, varsknown):
        if isinstance(term, (Variable, BNode)):
            varsknown.add(term)

    l = [(None, x) for x in l]
    varsknown = set()
    varscount = collections.defaultdict(int)
    for t in l:
        for c in t[1]:
            if isinstance(c, (Variable, BNode)):
                varscount[c] += 1
    i = 0

    # Done in steps, sort by number of bound terms
    # the top block of patterns with the most bound terms is kept
    # the rest is resorted based on the vars bound after the first
    # block is evaluated

    # we sort by decorate/undecorate, since we need the value of the sort keys

    while i < len(l):
        l[i:] = sorted((_knownTerms(x[
                       1], varsknown, varscount), x[1]) for x in l[i:])
        t = l[i][0][0]  # top block has this many terms bound
        j = 0
        while i+j < len(l) and l[i+j][0][0] == t:
            for c in l[i+j][1]:
                _addvar(c, varsknown)
            j += 1
        i += 1

    return [x[1] for x in l]


def triples(l):

    l = reduce(lambda x, y: x + y, l)
    if (len(l) % 3) != 0:
        raise Exception('these aint triples')
    return reorderTriples((l[x], l[x + 1], l[x + 2])
                          for x in range(0, len(l), 3))


def translatePName(p, prologue):
    """
    Expand prefixed/relative URIs
    """
    if isinstance(p, CompValue):
        if p.name == 'pname':
            return prologue.absolutize(p)
        if p.name == 'literal':
            return Literal(p.string, lang=p.lang,
                           datatype=prologue.absolutize(p.datatype))
    elif isinstance(p, URIRef):
        return prologue.absolutize(p)


def translatePath(p):

    """
    Translate PropertyPath expressions
    """

    if isinstance(p, CompValue):
        if p.name == 'PathAlternative':
            if len(p.part) == 1:
                return p.part[0]
            else:
                return AlternativePath(*p.part)

        elif p.name == 'PathSequence':
            if len(p.part) == 1:
                return p.part[0]
            else:
                return SequencePath(*p.part)

        elif p.name == 'PathElt':
            if not p.mod:
                return p.part
            else:
                if isinstance(p.part, list):
                    if len(p.part) != 1:
                        raise Exception('Denkfehler!')

                    return MulPath(p.part[0], p.mod)
                else:
                    return MulPath(p.part, p.mod)

        elif p.name == 'PathEltOrInverse':
            if isinstance(p.part, list):
                if len(p.part) != 1:
                    raise Exception('Denkfehler!')
                return InvPath(p.part[0])
            else:
                return InvPath(p.part)

        elif p.name == 'PathNegatedPropertySet':
            if isinstance(p.part, list):
                return NegatedPath(AlternativePath(*p.part))
            else:
                return NegatedPath(p.part)


def translateExists(e):

    """
    Translate the graph pattern used by EXISTS and NOT EXISTS
    http://www.w3.org/TR/sparql11-query/#sparqlCollectFilters
    """

    def _c(n):
        if isinstance(n, CompValue):
            if n.name in ('Builtin_EXISTS', 'Builtin_NOTEXISTS'):
                n.graph = translateGroupGraphPattern(n.graph)

    e = traverse(e, visitPost=_c)

    return e


def collectAndRemoveFilters(parts):

    """

    FILTER expressions apply to the whole group graph pattern in which
    they appear.

    http://www.w3.org/TR/sparql11-query/#sparqlCollectFilters
    """

    filters = []

    i = 0
    while i < len(parts):
        p = parts[i]
        if p.name == 'Filter':
            filters.append(translateExists(p.expr))
            parts.pop(i)
        else:
            i += 1

    if filters:
        return and_(*filters)

    return None


def translateGroupOrUnionGraphPattern(graphPattern):
    A = None

    for g in graphPattern.graph:
        g = translateGroupGraphPattern(g)
        if not A:
            A = g
        else:
            A = Union(A, g)
    return A


def translateGraphGraphPattern(graphPattern):
    return Graph(graphPattern.term,
                 translateGroupGraphPattern(graphPattern.graph))


def translateInlineData(graphPattern):
    return ToMultiSet(translateValues(graphPattern))


def translateGroupGraphPattern(graphPattern):
    """
    http://www.w3.org/TR/sparql11-query/#convertGraphPattern
    """

    if graphPattern.name == 'SubSelect':
        return ToMultiSet(translate(graphPattern)[0])

    if not graphPattern.part:
        graphPattern.part = []  # empty { }

    filters = collectAndRemoveFilters(graphPattern.part)

    g = []
    for p in graphPattern.part:
        if p.name == 'TriplesBlock':
            # merge adjacent TripleBlocks
            if not (g and g[-1].name == 'BGP'):
                g.append(BGP())
            g[-1]["triples"] += triples(p.triples)
        else:
            g.append(p)

    G = BGP()
    for p in g:
        if p.name == 'OptionalGraphPattern':
            A = translateGroupGraphPattern(p.graph)
            if A.name == 'Filter':
                G = LeftJoin(G, A.p, A.expr)
            else:
                G = LeftJoin(G, A, TrueFilter)
        elif p.name == 'MinusGraphPattern':
            G = Minus(p1=G, p2=translateGroupGraphPattern(p.graph))
        elif p.name == 'GroupOrUnionGraphPattern':
            G = Join(p1=G, p2=translateGroupOrUnionGraphPattern(p))
        elif p.name == 'GraphGraphPattern':
            G = Join(p1=G, p2=translateGraphGraphPattern(p))
        elif p.name == 'InlineData':
            G = Join(p1=G, p2=translateInlineData(p))
        elif p.name == 'ServiceGraphPattern':
            G = Join(p1=G, p2=p)
        elif p.name in ('BGP', 'Extend'):
            G = Join(p1=G, p2=p)
        elif p.name == 'Bind':
            G = Extend(G, p.expr, p.var)

        else:
            raise Exception('Unknown part in GroupGraphPattern: %s - %s' %
                            (type(p), p.name))

    if filters:
        G = Filter(expr=filters, p=G)

    return G


class StopTraversal(Exception):
    def __init__(self, rv):
        self.rv = rv


def _traverse(e, visitPre=lambda n: None, visitPost=lambda n: None):
    """
    Traverse a parse-tree, visit each node

    if visit functions return a value, replace current node
    """
    _e = visitPre(e)
    if _e is not None:
        return _e

    if e is None:
        return None

    if isinstance(e, (list, ParseResults)):
        return [_traverse(x, visitPre, visitPost) for x in e]
    elif isinstance(e, tuple):
        return tuple([_traverse(x, visitPre, visitPost) for x in e])

    elif isinstance(e, CompValue):
        for k, val in e.iteritems():
            e[k] = _traverse(val, visitPre, visitPost)

    _e = visitPost(e)
    if _e is not None:
        return _e

    return e


def _traverseAgg(e, visitor=lambda n, v: None):
    """
    Traverse a parse-tree, visit each node

    if visit functions return a value, replace current node
    """

    res = []

    if isinstance(e, (list, ParseResults, tuple)):
        res = [_traverseAgg(x, visitor) for x in e]

    elif isinstance(e, CompValue):
        for k, val in e.iteritems():
            if val != None:
                res.append(_traverseAgg(val, visitor))

    return visitor(e, res)


def traverse(
        tree, visitPre=lambda n: None,
        visitPost=lambda n: None, complete=None):
    """
    Traverse tree, visit each node with visit function
    visit function may raise StopTraversal to stop traversal
    if complete!=None, it is returned on complete traversal,
    otherwise the transformed tree is returned
    """
    try:
        r = _traverse(tree, visitPre, visitPost)
        if complete is not None:
            return complete
        return r
    except StopTraversal, st:
        return st.rv


def _hasAggregate(x):
    """
    Traverse parse(sub)Tree
    return true if any aggregates are used
    """

    if isinstance(x, CompValue):
        if x.name.startswith('Aggregate_'):
            raise StopTraversal(True)


def _aggs(e, A):
    """
    Collect Aggregates in A
    replaces aggregates with variable references
    """

    # TODO: nested Aggregates?

    if isinstance(e, CompValue) and e.name.startswith('Aggregate_'):
        A.append(e)
        aggvar = Variable('__agg_%d__' % len(A))
        e["res"] = aggvar
        return aggvar


def _findVars(x, res):
    """
    Find all variables in a tree
    """
    if isinstance(x, Variable):
        res.add(x)
    if isinstance(x, CompValue):
        if x.name == "Bind":
            res.add(x.var)
            return x  # stop recursion and finding vars in the expr
        elif x.name == 'SubSelect':
            if x.projection: 
                res.update(v.var or v.evar for v in x.projection)
            return x


def _addVars(x, children):
    # import pdb; pdb.set_trace()
    if isinstance(x, Variable):
        return set([x])
    elif isinstance(x, CompValue):
        x["_vars"] = set(reduce(operator.or_, children, set()))
        if x.name == "Bind":
            return set([x.var])
        elif x.name == 'SubSelect':
            if x.projection:
                s = set(v.var or v.evar for v in x.projection)
            else: 
                s = set()

            return s
    return reduce(operator.or_, children, set())


def _sample(e, v=None):
    """
    For each unaggregated variable V in expr
    Replace V with Sample(V)
    """
    if isinstance(e, CompValue) and e.name.startswith("Aggregate_"):
        return e  # do not replace vars in aggregates
    if isinstance(e, Variable) and v != e:
        return CompValue('Aggregate_Sample', vars=e)


def _simplifyFilters(e):
    if isinstance(e, Expr):
        return simplifyFilters(e)


def translateAggregates(q, M):
    E = []
    A = []

    # collect/replace aggs in :
    #    select expr as ?var
    if q.projection:
        for v in q.projection:
            if v.evar: 
                v.expr = traverse(v.expr, functools.partial(_sample, v=v.evar))
                v.expr = traverse(v.expr, functools.partial(_aggs, A=A))


    # having clause
    if traverse(q.having, _hasAggregate, complete=False):
        q.having = traverse(q.having, _sample)
        traverse(q.having, functools.partial(_aggs, A=A))

    # order by
    if traverse(q.orderby, _hasAggregate, complete=False):
        q.orderby = traverse(q.orderby, _sample)
        traverse(q.orderby, functools.partial(_aggs, A=A))

    # sample all other select vars
    # TODO: only allowed for vars in group-by?
    if q.projection: 
        for v in q.projection: 
            if v.var:
                rv = Variable('__agg_%d__' % (len(A) + 1))
                A.append(CompValue('Aggregate_Sample', vars=v.var, res=rv))
                E.append((rv, v.var))
                
    return CompValue('AggregateJoin', A=A, p=M), E


def translateValues(v):
    # if len(v.var)!=len(v.value):
    #     raise Exception("Unmatched vars and values in ValueClause: "+str(v))

    res = []
    if not v.var:
        return res
    if not v.value:
        return res
    if not isinstance(v.value[0], list):

        for val in v.value:
            res.append({v.var[0]: val})
    else:
        for vals in v.value:
            res.append(dict(zip(v.var, vals)))

    return CompValue('values', res=res)


def translate(q):
    """
    http://www.w3.org/TR/sparql11-query/#convertSolMod

    """

    _traverse(q, _simplifyFilters)

    q.where = traverse(q.where, visitPost=translatePath)

    # TODO: Var scope test
    VS = set()
    traverse(q.where, functools.partial(_findVars, res=VS))

    # all query types have a where part
    M = translateGroupGraphPattern(q.where)

    aggregate = False
    if q.groupby:
        conditions = []
        # convert "GROUP BY (?expr as ?var)" to an Extend
        for c in q.groupby.condition:
            if isinstance(c, CompValue) and c.name == 'GroupAs':
                M = Extend(M, c.expr, c.var)
                c = c.var
            conditions.append(c)

        M = Group(p=M, expr=conditions)
        aggregate = True
    elif traverse(q.having, _hasAggregate, complete=False) or \
            traverse(q.orderby, _hasAggregate, complete=False) or \
            any(traverse(x.expr, _hasAggregate, complete=False)
                for x in q.projection or [] if x.evar):
        # if any aggregate is used, implicit group by
        M = Group(p=M)
        aggregate = True

    if aggregate:
        M, E = translateAggregates(q, M)
    else:
        E = []

    # HAVING
    if q.having:
        M = Filter(expr=and_(*q.having.condition), p=M)

    # VALUES
    if q.valuesClause:
        M = Join(p1=M, p2=ToMultiSet(translateValues(q.valuesClause)))

    if not q.projection: 
        # select *
        PV = list(VS)
    else:
        PV = list()
        for v in q.projection:
            if v.var:
                if v not in PV:
                    PV.append(v.var)
            elif v.evar:
                if v not in PV:
                    PV.append(v.evar)

                E.append((v.expr, v.evar))
            else: 
                raise Exception("I expected a var or evar here!")

    for e, v in E:
        M = Extend(M, e, v)

    # ORDER BY
    if q.orderby:
        M = OrderBy(M, [CompValue('OrderCondition', expr=c.expr,
                    order=c.order) for c in q.orderby.condition])

    # PROJECT
    M = Project(M, PV)

    if q.modifier:
        if q.modifier == 'DISTINCT':
            M = CompValue('Distinct', p=M)
        elif q.modifier == 'REDUCED':
            M = CompValue('Reduced', p=M)

    if q.limitoffset:
        offset = 0
        if q.limitoffset.offset != None:
            offset = q.limitoffset.offset.toPython()

        if q.limitoffset.limit != None:
            M = CompValue('Slice', p=M, start=offset,
                          length=q.limitoffset.limit.toPython())
        else:
            M = CompValue('Slice', p=M, start=offset)

    return M, PV


def simplify(n):
    """Remove joins to empty BGPs"""
    if isinstance(n, CompValue):
        if n.name == 'Join':
            if n.p1.name == 'BGP' and len(n.p1.triples) == 0:
                return n.p2
            if n.p2.name == 'BGP' and len(n.p2.triples) == 0:
                return n.p1
        elif n.name == 'BGP':
            n["triples"] = reorderTriples(n.triples)
            return n


def analyse(n, children):

    if isinstance(n, CompValue):
        if n.name == 'Join':
            n["lazy"] = all(children)
            return False
        elif n.name in ('Slice', 'Distinct'):
            return False
        else:
            return all(children)
    else:
        return True


def translatePrologue(p, base, initNs=None, prologue=None):

    if prologue is None:
        prologue = Prologue()
        prologue.base = ""
    if base:
        prologue.base = base
    if initNs:
        for k, v in initNs.iteritems():
            prologue.bind(k, v)

    for x in p:
        if x.name == 'Base':
            prologue.base = x.iri
        elif x.name == 'PrefixDecl':
            prologue.bind(x.prefix, prologue.absolutize(x.iri))

    return prologue


def translateQuads(quads):
    if quads.triples:
        alltriples = triples(quads.triples)
    else:
        alltriples = []

    allquads = collections.defaultdict(list)

    if quads.quadsNotTriples:
        for q in quads.quadsNotTriples:
            if q.triples:
                allquads[q.term] += triples(q.triples)

    return alltriples, allquads


def translateUpdate1(u, prologue):
    if u.name in ('Load', 'Clear', 'Drop', 'Create'):
        pass  # no translation needed
    elif u.name in ('Add', 'Move', 'Copy'):
        pass
    elif u.name in ('InsertData', 'DeleteData', 'DeleteWhere'):
        t, q = translateQuads(u.quads)
        u["quads"] = q
        u["triples"] = t
        if u.name in ('DeleteWhere', 'DeleteData'):
            pass  # TODO: check for bnodes in triples
    elif u.name == 'Modify':
        if u.delete:
            u.delete["triples"], u.delete[
                "quads"] = translateQuads(u.delete.quads)
        if u.insert:
            u.insert["triples"], u.insert[
                "quads"] = translateQuads(u.insert.quads)
        u["where"] = translateGroupGraphPattern(u.where)
    else:
        raise Exception('Unknown type of update operation: %s' % u)

    u.prologue = prologue
    return u


def translateUpdate(q, base=None, initNs=None):
    """
    Returns a list of SPARQL Update Algebra expressions
    """

    res = []
    prologue = None
    if not q.request:
        return res
    for p, u in zip(q.prologue, q.request):
        prologue = translatePrologue(p, base, initNs, prologue)

        # absolutize/resolve prefixes
        u = traverse(
            u, visitPost=functools.partial(translatePName, prologue=prologue))
        u = _traverse(u, _simplifyFilters)

        u = traverse(u, visitPost=translatePath)

        res.append(translateUpdate1(u, prologue))

    return res


def translateQuery(q, base=None, initNs=None):
    """
    Translate a query-parsetree to a SPARQL Algebra Expression

    Return a rdflib.plugins.sparql.sparql.Query object
    """

    # We get in: (prologue, query)

    prologue = translatePrologue(q[0], base, initNs)

    # absolutize/resolve prefixes
    q[1] = traverse(
        q[1], visitPost=functools.partial(translatePName, prologue=prologue))

    P, PV = translate(q[1])
    datasetClause = q[1].datasetClause
    if q[1].name == 'ConstructQuery':

        template = triples(q[1].template) if q[1].template else None

        res = CompValue(q[1].name, p=P,
                        template=template,
                        datasetClause=datasetClause)
    else:
        res = CompValue(q[1].name, p=P, datasetClause=datasetClause, PV=PV)

    res = traverse(res, visitPost=simplify)
    _traverseAgg(res, visitor=analyse)
    _traverseAgg(res, _addVars)

    return Query(prologue, res)


def pprintAlgebra(q):
    def pp(p, ind="    "):
        # if isinstance(p, list):
        #     print "[ "
        #     for x in p: pp(x,ind)
        #     print "%s ]"%ind
        #     return
        if not isinstance(p, CompValue):
            print p
            return
        print "%s(" % (p.name, )
        for k in p:
            print "%s%s =" % (ind, k,),
            pp(p[k], ind + "    ")
        print "%s)" % ind

    try:
        pp(q.algebra)
    except AttributeError:
        # it's update, just a list
        for x in q:
            pp(x)

if __name__ == '__main__':
    import sys
    from rdflib.plugins.sparql import parser
    import os.path

    if os.path.exists(sys.argv[1]):
        q = file(sys.argv[1])
    else:
        q = sys.argv[1]

    pq = parser.parseQuery(q)
    print pq
    tq = translateQuery(pq)
    print pprintAlgebra(tq)
