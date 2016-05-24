import collections

from rdflib.term import Variable, Literal, BNode, URIRef

from rdflib.plugins.sparql.operators import EBV
from rdflib.plugins.sparql.parserutils import Expr, CompValue
from rdflib.plugins.sparql.sparql import SPARQLError, NotBoundError


def _diff(a, b, expr):
    res = set()

    for x in a:
        if all(not x.compatible(y) or not _ebv(expr, x.merge(y)) for y in b):
            res.add(x)

    return res


def _minus(a, b):
    for x in a:
        if all((not x.compatible(y)) or x.disjointDomain(y) for y in b):
            yield x



def _join(a, b):
    for x in a:
        for y in b:
            if x.compatible(y):
                yield x.merge(y)


def _ebv(expr, ctx):

    """
    Return true/false for the given expr
    Either the expr is itself true/false
    or evaluates to something, with the given ctx

    an error is false
    """

    try:
        return EBV(expr)
    except SPARQLError:
        pass
    if isinstance(expr, Expr):
        try:
            return EBV(expr.eval(ctx))
        except SPARQLError:
            return False  # filter error == False
    elif isinstance(expr, CompValue):
        raise Exception(
            "Weird - filter got a CompValue without evalfn! %r" % expr)
    elif isinstance(expr, Variable):
        try:
            return EBV(ctx[expr])
        except:
            return False
    return False


def _eval(expr, ctx):
    if isinstance(expr, (Literal, URIRef)):
        return expr
    if isinstance(expr, Expr):
        return expr.eval(ctx)
    elif isinstance(expr, Variable):
        try:
            return ctx[expr]
        except KeyError:
            return NotBoundError("Variable %s is not bound" % expr)
    elif isinstance(expr, CompValue):
        raise Exception(
            "Weird - _eval got a CompValue without evalfn! %r" % expr)
    else:
        raise Exception("Cannot eval thing: %s (%s)" % (expr, type(expr)))


def _filter(a, expr):
    for c in a:
        if _ebv(expr, c):
            yield c


def _fillTemplate(template, solution):

    """
    For construct/deleteWhere and friends

    Fill a triple template with instantiated variables
    """

    bnodeMap = collections.defaultdict(BNode)
    for t in template:
        s, p, o = t

        _s = solution.get(s)
        _p = solution.get(p)
        _o = solution.get(o)

        # instantiate new bnodes for each solution
        _s, _p, _o = [bnodeMap[x] if isinstance(
            x, BNode) else y for x, y in zip(t, (_s, _p, _o))]

        if _s is not None and \
                _p is not None and \
                _o is not None:

            yield (_s, _p, _o)
