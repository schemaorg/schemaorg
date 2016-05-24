"""
This contains evaluation functions for expressions

They get bound as instances-methods to the CompValue objects from parserutils
using setEvalFn

"""

import re
import math
import random
import uuid
import hashlib
import urllib2

from decimal import Decimal, ROUND_HALF_UP, InvalidOperation

import operator as pyop  # python operators

import isodate

from rdflib.plugins.sparql.parserutils import CompValue, Expr
from rdflib.plugins.sparql.datatypes import XSD_DTs, type_promotion
from rdflib import URIRef, BNode, Variable, Literal, XSD, RDF
from rdflib.term import Node

from pyparsing import ParseResults

from rdflib.plugins.sparql.sparql import SPARQLError, SPARQLTypeError


# closed namespace, langString isn't in it
RDF_langString = URIRef(RDF.uri + "langString")


def Builtin_IRI(expr, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-iri
    """

    a = expr.arg

    if isinstance(a, URIRef):
        return a
    if isinstance(a, Literal):
        return ctx.prologue.absolutize(URIRef(a))

    raise SPARQLError('IRI function only accepts URIRefs or Literals/Strings!')


def Builtin_isBLANK(expr, ctx):
    return Literal(isinstance(expr.arg, BNode))


def Builtin_isLITERAL(expr, ctx):
    return Literal(isinstance(expr.arg, Literal))


def Builtin_isIRI(expr, ctx):
    return Literal(isinstance(expr.arg, URIRef))


def Builtin_isNUMERIC(expr, ctx):
    try:
        numeric(expr.arg)
        return Literal(True)
    except:
        return Literal(False)


def Builtin_BNODE(expr, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-bnode
    """

    a = expr.arg

    if a is None:
        return BNode()

    if isinstance(a, Literal):
        return ctx.bnodes[a]  # defaultdict does the right thing

    raise SPARQLError(
        'BNode function only accepts no argument or literal/string')


def Builtin_ABS(expr, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-abs
    """

    return Literal(abs(numeric(expr.arg)))


def Builtin_IF(expr, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-if
    """

    return expr.arg2 if EBV(expr.arg1) else expr.arg3


def Builtin_RAND(expr, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#idp2133952
    """

    return Literal(random.random())


def Builtin_UUID(expr, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-strdt
    """

    return URIRef(uuid.uuid4().urn)


def Builtin_STRUUID(expr, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-strdt
    """

    return Literal(str(uuid.uuid4()))


def Builtin_MD5(expr, ctx):
    s = string(expr.arg).encode("utf-8")
    return Literal(hashlib.md5(s).hexdigest())


def Builtin_SHA1(expr, ctx):
    s = string(expr.arg).encode("utf-8")
    return Literal(hashlib.sha1(s).hexdigest())


def Builtin_SHA256(expr, ctx):
    s = string(expr.arg).encode("utf-8")
    return Literal(hashlib.sha256(s).hexdigest())


def Builtin_SHA384(expr, ctx):
    s = string(expr.arg).encode("utf-8")
    return Literal(hashlib.sha384(s).hexdigest())


def Builtin_SHA512(expr, ctx):
    s = string(expr.arg).encode("utf-8")
    return Literal(hashlib.sha512(s).hexdigest())


def Builtin_COALESCE(expr, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-coalesce
    """
    for x in expr.get('arg', variables=True):
        if x is not None and not isinstance(x, (SPARQLError, Variable)):
            return x
    raise SPARQLError(
        "COALESCE got no arguments that did not evaluate to an error")


def Builtin_CEIL(expr, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-ceil
    """

    l = expr.arg
    return Literal(int(math.ceil(numeric(l))), datatype=l.datatype)


def Builtin_FLOOR(expr, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-floor
    """
    l = expr.arg
    return Literal(int(math.floor(numeric(l))), datatype=l.datatype)


def Builtin_ROUND(expr, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-round
    """

    # This used to be just math.bound
    # but in py3k bound was changed to
    # "round-to-even" behaviour
    # this is an ugly work-around
    l = expr.arg
    v = numeric(l)
    v = int(Decimal(v).quantize(1, ROUND_HALF_UP))
    return Literal(v, datatype=l.datatype)


def Builtin_REGEX(expr, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-regex
    Invokes the XPath fn:matches function to match text against a regular
    expression pattern.
    The regular expression language is defined in XQuery 1.0 and XPath 2.0
    Functions and Operators section 7.6.1 Regular Expression Syntax
    """

    text = string(expr.text)
    pattern = string(expr.pattern)
    flags = expr.flags

    cFlag = 0
    if flags:
        # Maps XPath REGEX flags (http://www.w3.org/TR/xpath-functions/#flags)
        # to Python's re flags
        flagMap = dict(
            [('i', re.IGNORECASE), ('s', re.DOTALL), ('m', re.MULTILINE)])
        cFlag = reduce(pyop.or_, [flagMap.get(f, 0) for f in flags])

    return Literal(bool(re.search(unicode(pattern), text, cFlag)))


def Builtin_REPLACE(expr, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-substr
    """
    text = string(expr.arg)
    pattern = string(expr.pattern)
    replacement = string(expr.replacement)
    flags = expr.flags

    # python uses \1, xpath/sparql uses $1
    replacement = re.sub('\\$([0-9]*)', r'\\\1', replacement)

    def _r(m):

        # Now this is ugly.
        # Python has a "feature" where unmatched groups return None
        # then re.sub chokes on this.
        # see http://bugs.python.org/issue1519638

        # this works around and hooks into the internal of the re module...

        # the match object is replaced with a wrapper that
        # returns "" instead of None for unmatched groups

        class _m():
            def __init__(self, m):
                self.m = m
                self.string = m.string

            def group(self, n):
                return m.group(n) or ""

        return re._expand(pattern, _m(m), replacement)

    cFlag = 0
    if flags:
        # Maps XPath REGEX flags (http://www.w3.org/TR/xpath-functions/#flags)
        # to Python's re flags
        flagMap = dict(
            [('i', re.IGNORECASE), ('s', re.DOTALL), ('m', re.MULTILINE)])
        cFlag = reduce(pyop.or_, [flagMap.get(f, 0) for f in flags])

        # @@FIXME@@ either datatype OR lang, NOT both
    return Literal(re.sub(unicode(pattern), _r, text, cFlag),
                   datatype=text.datatype, lang=text.language)


def Builtin_STRDT(expr, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-strdt
    """

    return Literal(unicode(expr.arg1), datatype=expr.arg2)


def Builtin_STRLANG(expr, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-strlang
    """

    s = string(expr.arg1)
    if s.language or s.datatype:
        raise SPARQLError('STRLANG expects a simple literal')

    # TODO: normalisation of lang tag to lower-case
    # should probably happen in literal __init__
    return Literal(unicode(s), lang=str(expr.arg2).lower())


def Builtin_CONCAT(expr, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-concat
    """

    # dt/lang passed on only if they all match

    dt = set(x.datatype for x in expr.arg)
    dt = dt.pop() if len(dt) == 1 else None

    lang = set(x.language for x in expr.arg)
    lang = lang.pop() if len(lang) == 1 else None

    return Literal("".join(string(x)
                           for x in expr.arg), datatype=dt, lang=lang)


def _compatibleStrings(a, b):
    string(a)
    string(b)

    if b.language and a.language != b.language:
        raise SPARQLError('incompatible arguments to str functions')


def Builtin_STRSTARTS(expr, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-strstarts
    """

    a = expr.arg1
    b = expr.arg2
    _compatibleStrings(a, b)

    return Literal(a.startswith(b))


def Builtin_STRENDS(expr, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-strends
    """
    a = expr.arg1
    b = expr.arg2

    _compatibleStrings(a, b)

    return Literal(a.endswith(b))


def Builtin_STRBEFORE(expr, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-strbefore
    """

    a = expr.arg1
    b = expr.arg2
    _compatibleStrings(a, b)

    i = a.find(b)
    if i == -1:
        return Literal("")
    else:
        return Literal(a[:i], lang=a.language, datatype=a.datatype)


def Builtin_STRAFTER(expr, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-strafter
    """

    a = expr.arg1
    b = expr.arg2
    _compatibleStrings(a, b)

    i = a.find(b)
    if i == -1:
        return Literal("")
    else:
        return Literal(a[i + len(b):], lang=a.language, datatype=a.datatype)


def Builtin_CONTAINS(expr, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-strcontains
    """

    a = expr.arg1
    b = expr.arg2
    _compatibleStrings(a, b)

    return Literal(b in a)


def Builtin_ENCODE_FOR_URI(expr, ctx):
    return Literal(urllib2.quote(string(expr.arg).encode("utf-8")))


def Builtin_SUBSTR(expr, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-substr
    """

    a = string(expr.arg)

    start = numeric(expr.start) - 1

    length = expr.length
    if length is not None:
        length = numeric(length) + start

    return Literal(a[start:length], lang=a.language, datatype=a.datatype)


def Builtin_STRLEN(e, ctx):
    l = string(e.arg)

    return Literal(len(l))


def Builtin_STR(e, ctx):
    arg = e.arg
    if isinstance(arg, SPARQLError):
        raise arg
    return Literal(unicode(arg))  # plain literal


def Builtin_LCASE(e, ctx):
    l = string(e.arg)

    return Literal(l.lower(), datatype=l.datatype, lang=l.language)


def Builtin_LANGMATCHES(e, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-langMatches


    """
    langTag = string(e.arg1)
    langRange = string(e.arg2)

    if unicode(langTag) == "":
        return Literal(False)  # nothing matches empty!

    return Literal(_lang_range_check(langRange, langTag))


def Builtin_NOW(e, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-now
    """
    return Literal(ctx.now)


def Builtin_YEAR(e, ctx):
    d = datetime(e.arg)
    return Literal(d.year)


def Builtin_MONTH(e, ctx):
    d = datetime(e.arg)
    return Literal(d.month)


def Builtin_DAY(e, ctx):
    d = datetime(e.arg)
    return Literal(d.day)


def Builtin_HOURS(e, ctx):
    d = datetime(e.arg)
    return Literal(d.hour)


def Builtin_MINUTES(e, ctx):
    d = datetime(e.arg)
    return Literal(d.minute)


def Builtin_SECONDS(e, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-seconds
    """
    d = datetime(e.arg)
    return Literal(d.second, datatype=XSD.decimal)


def Builtin_TIMEZONE(e, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-timezone

    :returns: the timezone part of arg as an xsd:dayTimeDuration.
    :raises: an error if there is no timezone.
    """
    dt = datetime(e.arg)
    if not dt.tzinfo:
        raise SPARQLError('datatime has no timezone: %s' % dt)

    delta = dt.tzinfo.utcoffset(ctx.now)

    d = delta.days
    s = delta.seconds
    neg = ""

    if d < 0:
        s = -24 * 60 * 60 * d - s
        d = 0
        neg = "-"

    h = s / (60 * 60)
    m = (s - h * 60 * 60) / 60
    s = s - h * 60 * 60 - m * 60

    tzdelta = "%sP%sT%s%s%s" % (neg,
                                "%dD" % d if d else "",
                                "%dH" % h if h else "",
                                "%dM" % m if m else "",
                                "%dS" % s if not d and not h and not m else "")

    return Literal(tzdelta, datatype=XSD.dayTimeDuration)


def Builtin_TZ(e, ctx):
    d = datetime(e.arg)
    if not d.tzinfo:
        return Literal("")
    n = d.tzinfo.tzname(d)
    if n == "UTC":
        n = "Z"
    return Literal(n)


def Builtin_UCASE(e, ctx):
    l = string(e.arg)

    return Literal(l.upper(), datatype=l.datatype, lang=l.language)


def Builtin_LANG(e, ctx):

    """
    http://www.w3.org/TR/sparql11-query/#func-lang

    Returns the language tag of ltrl, if it has one. It returns "" if ltrl has
    no language tag. Note that the RDF data model does not include literals
    with an empty language tag.
    """

    l = literal(e.arg)
    return Literal(l.language or "")


def Builtin_DATATYPE(e, ctx):
    l = e.arg
    if not isinstance(l, Literal):
        raise SPARQLError('Can only get datatype of literal: %s' % l)
    if l.language:
        return RDF_langString
    if not l.datatype and not l.language:
        return XSD.string
    return l.datatype


def Builtin_sameTerm(e, ctx):
    a = e.arg1
    b = e.arg2
    return Literal(a == b)


def Builtin_BOUND(e, ctx):
    """
    http://www.w3.org/TR/sparql11-query/#func-bound
    """
    n = e.get('arg', variables=True)

    return Literal(not isinstance(n, Variable))


def Builtin_EXISTS(e, ctx):
    # damn...
    from rdflib.plugins.sparql.evaluate import evalPart

    exists = e.name == 'Builtin_EXISTS'

    ctx = ctx.ctx.thaw(ctx)  # hmm
    for x in evalPart(ctx, e.graph):
        return Literal(exists)
    return Literal(not exists)


def Function(e, ctx):
    """
    Custom functions (and casts!)
    """

    if e.iri in XSD_DTs:
        # a cast

        if not e.expr:
            raise SPARQLError("Nothing given to cast.")
        if len(e.expr) > 1:
            raise SPARQLError("Cannot cast more than one thing!")

        x = e.expr[0]

        if e.iri == XSD.string:

            if isinstance(x, (URIRef, Literal)):
                return Literal(x, datatype=XSD.string)
            else:
                raise SPARQLError(
                    "Cannot cast term %s of type %s" % (x, type(x)))

        if not isinstance(x, Literal):
            raise SPARQLError(
                "Can only cast Literals to non-string data-types")

        if x.datatype and not x.datatype in XSD_DTs:
            raise SPARQLError(
                "Cannot cast literal with unknown datatype: %s" % x.datatype)

        if e.iri == XSD.dateTime:
            if x.datatype and x.datatype not in (XSD.dateTime, XSD.string):
                raise SPARQLError(
                    "Cannot cast %s to XSD:dateTime" % x.datatype)
            try:
                return Literal(isodate.parse_datetime(x), datatype=e.iri)
            except:
                raise SPARQLError("Cannot interpret '%s' as datetime" % x)

        if x.datatype == XSD.dateTime:
            raise SPARQLError("Cannot cast XSD.dateTime to %s" % e.iri)

        if e.iri in (XSD.float, XSD.double):
            try:
                return Literal(float(x), datatype=e.iri)
            except:
                raise SPARQLError("Cannot interpret '%s' as float" % x)

        elif e.iri == XSD.decimal:
            if "e" in x or "E" in x:  # SPARQL/XSD does not allow exponents in decimals
                raise SPARQLError("Cannot interpret '%s' as decimal" % x)
            try:
                return Literal(Decimal(x), datatype=e.iri)
            except:
                raise SPARQLError("Cannot interpret '%s' as decimal" % x)

        elif e.iri == XSD.integer:
            try:
                return Literal(int(x), datatype=XSD.integer)
            except:
                raise SPARQLError("Cannot interpret '%s' as int" % x)

        elif e.iri == XSD.boolean:
            # # I would argue that any number is True...
            # try:
            #     return Literal(bool(int(x)), datatype=XSD.boolean)
            # except:
            if x.lower() in ("1", "true"):
                return Literal(True)
            if x.lower() in ("0", "false"):
                return Literal(False)

            raise SPARQLError("Cannot interpret '%s' as bool" % x)
        else:
            raise Exception("I do not know how to cast to %s" % e.iri)

    else:
        raise SPARQLError('Unknown function %s"%e.iri')

    # TODO: Custom functions!


def UnaryNot(expr, ctx):
    return Literal(not EBV(expr.expr))


def UnaryMinus(expr, ctx):
    return Literal(-numeric(expr.expr))


def UnaryPlus(expr, ctx):
    return Literal(+numeric(expr.expr))


def MultiplicativeExpression(e, ctx):

    expr = e.expr
    other = e.other

    # because of the way the mul-expr production handled operator precedence
    # we sometimes have nothing to do
    if other is None:
        return expr
    try:
        res = Decimal(numeric(expr))
        for op, f in zip(e.op, other):
            f = numeric(f)

            if type(f) == float:
                res = float(res)

            if op == '*':
                res *= f
            else:
                res /= f
    except (InvalidOperation, ZeroDivisionError):
        raise SPARQLError('divide by 0')

    return Literal(res)


def AdditiveExpression(e, ctx):

    expr = e.expr
    other = e.other

    # because of the way the add-expr production handled operator precedence
    # we sometimes have nothing to do
    if other is None:
        return expr

    res = numeric(expr)

    dt = expr.datatype

    for op, term in zip(e.op, other):
        n = numeric(term)
        if isinstance(n, Decimal) and isinstance(res, float):
            n = float(n)
        if isinstance(n, float) and isinstance(res, Decimal):
            res = float(res)

        dt = type_promotion(dt, term.datatype)

        if op == '+':
            res += n
        else:
            res -= n

    return Literal(res, datatype=dt)


def RelationalExpression(e, ctx):

    expr = e.expr
    other = e.other
    op = e.op

    # because of the way the add-expr production handled operator precedence
    # we sometimes have nothing to do
    if other is None:
        return expr

    ops = dict([('>', lambda x, y: x.__gt__(y)),
                ('<', lambda x, y: x.__lt__(y)),
                ('=', lambda x, y: x.eq(y)),
                ('!=', lambda x, y: x.neq(y)),
                ('>=', lambda x, y: x.__ge__(y)),
                ('<=', lambda x, y: x.__le__(y)),
                ('IN', pyop.contains),
                ('NOT IN', lambda x, y: not pyop.contains(x, y))])

    if op in ('IN', 'NOT IN'):

        res = (op == 'NOT IN')

        error = False

        if other == RDF.nil:
            other = []

        for x in other:
            try:
                if x == expr:
                    return Literal(True ^ res)
            except SPARQLError, e:
                error = e
        if not error:
            return Literal(False ^ res)
        else:
            raise error

    if not op in ('=', '!=', 'IN', 'NOT IN'):
        if not isinstance(expr, Literal):
            raise SPARQLError(
                "Compare other than =, != of non-literals is an error: %s" %
                expr)
        if not isinstance(other, Literal):
            raise SPARQLError(
                "Compare other than =, != of non-literals is an error: %s" %
                other)
    else:
        if not isinstance(expr, Node):
            raise SPARQLError('I cannot compare this non-node: %s' % expr)
        if not isinstance(other, Node):
            raise SPARQLError('I cannot compare this non-node: %s' % other)

    if isinstance(expr, Literal) and isinstance(other, Literal):

        if expr.datatype != None and expr.datatype not in XSD_DTs and other.datatype != None and other.datatype not in XSD_DTs:
            # in SPARQL for non-XSD DT Literals we can only do =,!=
            if op not in ('=', '!='):
                raise SPARQLError(
                    'Can only do =,!= comparisons of non-XSD Literals')

    try:
        r = ops[op](expr, other)
        if r == NotImplemented:
            raise SPARQLError('Error when comparing')
    except TypeError, te:
        raise SPARQLError(*te.args)
    return Literal(r)


def ConditionalAndExpression(e, ctx):

    # TODO: handle returned errors

    expr = e.expr
    other = e.other

    # because of the way the add-expr production handled operator precedence
    # we sometimes have nothing to do
    if other is None:
        return expr

    return Literal(all(EBV(x) for x in [expr] + other))


def ConditionalOrExpression(e, ctx):

    # TODO: handle errors

    expr = e.expr
    other = e.other

    # because of the way the add-expr production handled operator precedence
    # we sometimes have nothing to do
    if other is None:
        return expr
    # A logical-or that encounters an error on only one branch
    # will return TRUE if the other branch is TRUE and an error
    # if the other branch is FALSE.
    error = None
    for x in [expr] + other:
        try:
            if EBV(x):
                return Literal(True)
        except SPARQLError, e:
            error = e
    if error:
        raise error
    return Literal(False)


def not_(arg):
    return Expr('UnaryNot', UnaryNot, expr=arg)


def and_(*args):
    if len(args) == 1:
        return args[0]

    return Expr('ConditionalAndExpression', ConditionalAndExpression,
                expr=args[0], other=list(args[1:]))

TrueFilter = Expr('TrueFilter', lambda _1, _2: Literal(True))


def simplify(expr):
    if isinstance(expr, ParseResults) and len(expr) == 1:
        return simplify(expr[0])

    if isinstance(expr, (list, ParseResults)):
        return map(simplify, expr)
    if not isinstance(expr, CompValue):
        return expr
    if expr.name.endswith('Expression'):
        if expr.other is None:
            return simplify(expr.expr)

    for k in expr.keys():
        expr[k] = simplify(expr[k])
        # expr['expr']=simplify(expr.expr)
        #    expr['other']=simplify(expr.other)

    return expr


def literal(s):
    if not isinstance(s, Literal):
        raise SPARQLError("Non-literal passed as string: %s" % s)
    return s


def datetime(e):
    if not isinstance(e, Literal):
        raise SPARQLError("Non-literal passed as datetime: %s" % e)
    if not e.datatype == XSD.dateTime:
        raise SPARQLError(
            "Literal with wrong datatype passed as datetime: %s" % e)
    return e.toPython()


def string(s):
    """
    Make sure the passed thing is a string literal
    i.e. plain literal, xsd:string literal or lang-tagged literal
    """
    if not isinstance(s, Literal):
        raise SPARQLError("Non-literal passes as string: %s" % s)
    if s.datatype and s.datatype != XSD.string:
        raise SPARQLError(
            "Non-string datatype-literal passes as string: %s" % s)
    return s


def numeric(expr):
    """
    return a number from a literal
    http://www.w3.org/TR/xpath20/#promotion

    or TypeError
    """

    if not isinstance(expr, Literal):
        raise SPARQLTypeError("%s is not a literal!" % expr)

    if expr.datatype not in (XSD.float, XSD.double,
                             XSD.decimal, XSD.integer,
                             XSD.nonPositiveInteger, XSD.negativeInteger,
                             XSD.nonNegativeInteger, XSD.positiveInteger,
                             XSD.unsignedLong, XSD.unsignedInt,
                             XSD.unsignedShort, XSD.unsignedByte,
                             XSD.long, XSD.int, XSD.short, XSD.byte):
        raise SPARQLTypeError("%s does not have a numeric datatype!" % expr)

    return expr.toPython()


def EBV(rt):
    """
    * If the argument is a typed literal with a datatype of xsd:boolean,
      the EBV is the value of that argument.
    * If the argument is a plain literal or a typed literal with a
      datatype of xsd:string, the EBV is false if the operand value
      has zero length; otherwise the EBV is true.
    * If the argument is a numeric type or a typed literal with a datatype
      derived from a numeric type, the EBV is false if the operand value is
      NaN or is numerically equal to zero; otherwise the EBV is true.
    * All other arguments, including unbound arguments, produce a type error.

    """

    if isinstance(rt, Literal):

        if rt.datatype == XSD.boolean:
            return rt.toPython()

        elif rt.datatype == XSD.string or rt.datatype is None:
            return len(rt) > 0

        else:
            pyRT = rt.toPython()

            if isinstance(pyRT, Literal):
                # Type error, see: http://www.w3.org/TR/rdf-sparql-query/#ebv
                raise SPARQLTypeError(
                    "http://www.w3.org/TR/rdf-sparql-query/#ebv - ' + \
                    'Could not determine the EBV for : %s" % rt)
            else:
                return bool(pyRT)

    else:
        raise SPARQLTypeError(
            "http://www.w3.org/TR/rdf-sparql-query/#ebv - ' + \
            'Only literals have Boolean values! %s" % rt)


def _lang_range_check(range, lang):
    """
    Implementation of the extended filtering algorithm, as defined in point
    3.3.2, of U{RFC 4647<http://www.rfc-editor.org/rfc/rfc4647.txt>}, on
    matching language ranges and language tags.
    Needed to handle the C{rdf:PlainLiteral} datatype.
    @param range: language range
    @param lang: language tag
    @rtype: boolean

        @author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}

        Taken from `RDFClosure/RestrictedDatatype.py`__

    .. __:http://dev.w3.org/2004/PythonLib-IH/RDFClosure/RestrictedDatatype.py

    """
    def _match(r, l):
        """
        Matching of a range and language item: either range is a wildcard
        or the two are equal
        @param r: language range item
        @param l: language tag item
        @rtype: boolean
        """
        return r == '*' or r == l

    rangeList = range.strip().lower().split('-')
    langList = lang.strip().lower().split('-')
    if not _match(rangeList[0], langList[0]):
        return False
    if len(rangeList) > len(langList):
        return False

    return all(_match(*x) for x in zip(rangeList, langList))
