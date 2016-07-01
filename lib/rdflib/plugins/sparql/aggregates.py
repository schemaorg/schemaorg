from rdflib import Literal, XSD

from rdflib.plugins.sparql.evalutils import _eval
from rdflib.plugins.sparql.operators import numeric
from rdflib.plugins.sparql.datatypes import type_promotion

from rdflib.plugins.sparql.compat import num_max, num_min

from decimal import Decimal

"""
Aggregation functions
"""


def _eval_rows(expr, group):
    for row in group:
        try:
            yield _eval(expr, row)
        except:
            pass


def agg_Sum(a, group, bindings):
    c = 0

    dt = None
    for x in group:
        try:
            e = _eval(a.vars, x)
            n = numeric(e)
            if dt == None:
                dt = e.datatype
            else:
                dt = type_promotion(dt, e.datatype)

            if type(c) == float and type(n) == Decimal:
                c += float(n)
            elif type(n) == float and type(c) == Decimal:
                c = float(c) + n
            else:
                c += n
        except:
            pass  # simply dont count

    bindings[a.res] = Literal(c, datatype=dt)

# Perhaps TODO: keep datatype for max/min?


def agg_Min(a, group, bindings):
    m = None

    for x in group:
        try:
            v = numeric(_eval(a.vars, x))
            if m is None:
                m = v
            else:
                m = num_min(v, m)
        except:
            return  # error in aggregate => no binding

    if m is not None:
        bindings[a.res] = Literal(m)


def agg_Max(a, group, bindings):
    m = None

    for x in group:
        try:
            v = numeric(_eval(a.vars, x))
            if m is None:
                m = v
            else:
                m = num_max(v, m)
        except:
            return  # error in aggregate => no binding

    if m is not None:
        bindings[a.res] = Literal(m)


def agg_Count(a, group, bindings):

    c = 0
    for x in group:
        try:
            if a.vars != '*':
                _eval(a.vars, x)
            c += 1
        except:
            return  # error in aggregate => no binding
            # pass  # simply dont count

    bindings[a.res] = Literal(c)


def agg_Sample(a, group, bindings):
    try:
        bindings[a.res] = _eval(a.vars, iter(group).next())
    except StopIteration:
        pass  # no res


def agg_GroupConcat(a, group, bindings):

    sep = a.separator or " "

    bindings[a.res] = Literal(
        sep.join(unicode(x) for x in _eval_rows(a.vars, group)))


def agg_Avg(a, group, bindings):

    c = 0
    s = 0
    dt = None
    for x in group:
        try:
            e = _eval(a.vars, x)
            n = numeric(e)
            if dt == None:
                dt = e.datatype
            else:
                dt = type_promotion(dt, e.datatype)

            if type(s) == float and type(n) == Decimal:
                s += float(n)
            elif type(n) == float and type(s) == Decimal:
                s = float(s) + n
            else:
                s += n
            c += 1
        except:
            return  # error in aggregate => no binding

    if c == 0:
        bindings[a.res] = Literal(0)
    if dt == XSD.float or dt == XSD.double:
        bindings[a.res] = Literal(s / c)
    else:
        bindings[a.res] = Literal(Decimal(s) / Decimal(c))


def evalAgg(a, group, bindings):
    if a.name == 'Aggregate_Count':
        return agg_Count(a, group, bindings)
    elif a.name == 'Aggregate_Sum':
        return agg_Sum(a, group, bindings)
    elif a.name == 'Aggregate_Sample':
        return agg_Sample(a, group, bindings)
    elif a.name == 'Aggregate_GroupConcat':
        return agg_GroupConcat(a, group, bindings)
    elif a.name == 'Aggregate_Avg':
        return agg_Avg(a, group, bindings)
    elif a.name == 'Aggregate_Min':
        return agg_Min(a, group, bindings)
    elif a.name == 'Aggregate_Max':
        return agg_Max(a, group, bindings)

    else:
        raise Exception("Unknown aggregate function " + a.name)
