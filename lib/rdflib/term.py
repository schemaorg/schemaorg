"""
This module defines the different types of terms. Terms are the kinds of
objects that can appear in a quoted/asserted triple. This includes those
that are core to RDF:

* :class:`Blank Nodes <rdflib.term.BNode>`
* :class:`URI References <rdflib.term.URIRef>`
* :class:`Literals <rdflib.term.Literal>` (which consist of a literal value,datatype and language tag)

Those that extend the RDF model into N3:

* :class:`Formulae <rdflib.graph.QuotedGraph>`
* :class:`Universal Quantifications (Variables) <rdflib.term.Variable>`

And those that are primarily for matching against 'Nodes' in the
underlying Graph:

* REGEX Expressions
* Date Ranges
* Numerical Ranges

"""

__all__ = [
    'bind',

    'Node',
    'Identifier',

    'URIRef',
    'BNode',
    'Literal',

    'Variable',
    'Statement',
]

import logging
logger = logging.getLogger(__name__)
import warnings

import base64
import xml.dom.minidom

from urlparse import urlparse, urljoin, urldefrag
from datetime import date, time, datetime
from re import sub, compile
from collections import defaultdict

from isodate import parse_time, parse_date, parse_datetime


try:
    from hashlib import md5
    assert md5
except ImportError:
    from md5 import md5


import rdflib
from . import py3compat
from rdflib.compat import numeric_greater



b = py3compat.b

skolem_genid = "/.well-known/genid/"
rdflib_skolem_genid = "/.well-known/genid/rdflib/"
skolems = {}


_invalid_uri_chars = '<>" {}|\\^`'

def _is_valid_uri(uri):
    for c in _invalid_uri_chars:
        if c in uri: return False
    return True

_lang_tag_regex = compile('^[a-zA-Z]+(?:-[a-zA-Z0-9]+)*$')

def _is_valid_langtag(tag):
    return bool(_lang_tag_regex.match(tag))


class Node(object):
    """
    A Node in the Graph.
    """

    __slots__ = ()


class Identifier(Node, unicode):  # allow Identifiers to be Nodes in the Graph
    """
    See http://www.w3.org/2002/07/rdf-identifer-terminology/
    regarding choice of terminology.
    """

    __slots__ = ()

    def __new__(cls, value):
        return unicode.__new__(cls, value)

    def eq(self, other):
        """A "semantic"/interpreted equality function,
        by default, same as __eq__"""
        return self.__eq__(other)

    def neq(self, other):
        """A "semantic"/interpreted not equal function,
        by default, same as __ne__"""
        return self.__ne__(other)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        """
        Equality for Nodes.

        >>> BNode("foo")==None
        False
        >>> BNode("foo")==URIRef("foo")
        False
        >>> URIRef("foo")==BNode("foo")
        False
        >>> BNode("foo")!=URIRef("foo")
        True
        >>> URIRef("foo")!=BNode("foo")
        True
        >>> Variable('a')!=URIRef('a')
        True
        >>> Variable('a')!=Variable('a')
        False
        """

        if type(self) == type(other):
            return unicode(self) == unicode(other)
        else:
            return False

    def __gt__(self, other):
        """
        This implements ordering for Nodes,

        This tries to implement this:
        http://www.w3.org/TR/sparql11-query/#modOrderBy

        Variables are not included in the SPARQL list, but
        they are greater than BNodes and smaller than everything else

        """
        if other is None:
            return True  # everything bigger than None
        elif type(self) == type(other):
            return unicode(self) > unicode(other)
        elif isinstance(other, Node):
            return _ORDERING[type(self)] > _ORDERING[type(other)]

        return NotImplemented

    def __lt__(self, other):
        if other is None:
            return False  # Nothing is less than None
        elif type(self) == type(other):
            return unicode(self) < unicode(other)
        elif isinstance(other, Node):
            return _ORDERING[type(self)] < _ORDERING[type(other)]

        return NotImplemented

    def __le__(self, other):
        r = self.__lt__(other)
        if r:
            return True
        return self == other

    def __ge__(self, other):
        r = self.__gt__(other)
        if r:
            return True
        return self == other

    def __hash__(self):
        t = type(self)
        fqn = t.__module__ + '.' + t.__name__
        return hash(fqn) ^ hash(unicode(self))


class URIRef(Identifier):
    """
    RDF URI Reference: http://www.w3.org/TR/rdf-concepts/#section-Graph-URIref
    """

    __slots__ = ()

    def __new__(cls, value, base=None):
        if base is not None:
            ends_in_hash = value.endswith("#")
            value = urljoin(base, value, allow_fragments=1)
            if ends_in_hash:
                if not value.endswith("#"):
                    value += "#"

        if not _is_valid_uri(value):
            logger.warning('%s does not look like a valid URI, trying to serialize this will break.'%value)


        try:
            rt = unicode.__new__(cls, value)
        except UnicodeDecodeError:
            rt = unicode.__new__(cls, value, 'utf-8')
        return rt

    def toPython(self):
        return unicode(self)

    def n3(self, namespace_manager = None):
        """
        This will do a limited check for valid URIs,
        essentially just making sure that the string includes no illegal
        characters (``<, >, ", {, }, |, \\, `, ^``)

        :param namespace_manager: if not None, will be used to make up
             a prefixed name
        """

        if not _is_valid_uri(self):
            raise Exception('"%s" does not look like a valid URI, I cannot serialize this as N3/Turtle. Perhaps you wanted to urlencode it?'%self)

        if namespace_manager:
            return namespace_manager.normalizeUri(self)
        else:
            return "<%s>" % self

    def defrag(self):
        if "#" in self:
            url, frag = urldefrag(self)
            return URIRef(url)
        else:
            return self

    def __reduce__(self):
        return (URIRef, (unicode(self),))

    def __getnewargs__(self):
        return (unicode(self), )

    if not py3compat.PY3:
        def __str__(self):
            return self.encode()

    def __repr__(self):
        if self.__class__ is URIRef:
            clsName = "rdflib.term.URIRef"
        else:
            clsName = self.__class__.__name__

        return """%s(%s)""" % (clsName, super(URIRef, self).__repr__())

    def __add__(self, other):
        return self.__class__(unicode(self) + other)

    def __radd__(self, other):
        return self.__class__(other + unicode(self))

    def __mod__(self, other):
        return self.__class__(unicode(self) % other)

    def md5_term_hash(self):
        """a string of hex that will be the same for two URIRefs that
        are the same. It is not a suitable unique id.

        Supported for backwards compatibility; new code should
        probably just use __hash__
        """
        warnings.warn(
            "method md5_term_hash is deprecated, and will be removed " +
            "in the future. If you use this please let rdflib-dev know!",
            category=DeprecationWarning, stacklevel=2)
        d = md5(self.encode())
        d.update(b("U"))
        return d.hexdigest()

    def de_skolemize(self):
        """ Create a Blank Node from a skolem URI, in accordance
        with http://www.w3.org/TR/rdf11-concepts/#section-skolemization.
        This function accepts only rdflib type skolemization, to provide
        a round-tripping within the system.

        .. versionadded:: 4.0
        """
        if isinstance(self, RDFLibGenid):
            parsed_uri = urlparse("%s" % self)
            return BNode(
                value=parsed_uri.path[len(rdflib_skolem_genid):])
        elif isinstance(self, Genid):
            bnode_id = "%s" % self
            if bnode_id in skolems:
                return skolems[bnode_id]
            else:
                retval = BNode()
                skolems[bnode_id] = retval
                return retval
        else:
            raise Exception("<%s> is not a skolem URI" % self)


class Genid(URIRef):
    __slots__ = ()

    @staticmethod
    def _is_external_skolem(uri):
        if not isinstance(uri, basestring):
            uri = str(uri)
        parsed_uri = urlparse(uri)
        gen_id = parsed_uri.path.rfind(skolem_genid)
        if gen_id != 0:
            return False
        return True


class RDFLibGenid(Genid):
    __slots__ = ()

    @staticmethod
    def _is_rdflib_skolem(uri):
        if not isinstance(uri, basestring):
            uri = str(uri)
        parsed_uri = urlparse(uri)
        if parsed_uri.params != "" \
                or parsed_uri.query != "" \
                or parsed_uri.fragment != "":
            return False
        gen_id = parsed_uri.path.rfind(rdflib_skolem_genid)
        if gen_id != 0:
            return False
        return True


def _unique_id():
    # Used to read: """Create a (hopefully) unique prefix"""
    # now retained merely to leave interal API unchanged.
    # From BNode.__new__() below ...
    #
    # acceptable bnode value range for RDF/XML needs to be
    # something that can be serialzed as a nodeID for N3
    #
    # BNode identifiers must be valid NCNames" _:[A-Za-z][A-Za-z0-9]*
    # http://www.w3.org/TR/2004/REC-rdf-testcases-20040210/#nodeID
    return "N"  # ensure that id starts with a letter


def _serial_number_generator():
    """
    Generates UUID4-based but ncname-compliant identifiers.
    """
    from uuid import uuid4

    def _generator():
        return uuid4().hex

    return _generator


class BNode(Identifier):
    """
    Blank Node: http://www.w3.org/TR/rdf-concepts/#section-blank-nodes

    """
    __slots__ = ()

    def __new__(cls, value=None,
                _sn_gen=_serial_number_generator(), _prefix=_unique_id()):
        """
        # only store implementations should pass in a value
        """
        if value is None:
            # so that BNode values do not collide with ones created with
            # a different instance of this module at some other time.
            node_id = _sn_gen()
            value = "%s%s" % (_prefix, node_id)
        else:
            # TODO: check that value falls within acceptable bnode value range
            # for RDF/XML needs to be something that can be serialzed
            # as a nodeID for N3 ??  Unless we require these
            # constraints be enforced elsewhere?
            pass  # assert is_ncname(unicode(value)), "BNode identifiers
                 # must be valid NCNames" _:[A-Za-z][A-Za-z0-9]*
                 # http://www.w3.org/TR/2004/REC-rdf-testcases-20040210/#nodeID
        return Identifier.__new__(cls, value)

    def toPython(self):
        return unicode(self)

    def n3(self, namespace_manager=None):
        return "_:%s" % self

    def __getnewargs__(self):
        return (unicode(self), )

    def __reduce__(self):
        return (BNode, (unicode(self),))

    if not py3compat.PY3:
        def __str__(self):
            return self.encode()

    def __repr__(self):
        if self.__class__ is BNode:
            clsName = "rdflib.term.BNode"
        else:
            clsName = self.__class__.__name__
        return """%s('%s')""" % (clsName, str(self))

    def md5_term_hash(self):
        """a string of hex that will be the same for two BNodes that
        are the same. It is not a suitable unique id.

        Supported for backwards compatibility; new code should
        probably just use __hash__
        """
        warnings.warn(
            "method md5_term_hash is deprecated, and will be removed " +
            "in the future. If you use this please let rdflib-dev know!",
            category=DeprecationWarning, stacklevel=2)
        d = md5(self.encode())
        d.update(b("B"))
        return d.hexdigest()

    def skolemize(self, authority="http://rdlib.net/"):
        """ Create a URIRef "skolem" representation of the BNode, in accordance
        with http://www.w3.org/TR/rdf11-concepts/#section-skolemization

        .. versionadded:: 4.0
        """
        skolem = "%s%s" % (rdflib_skolem_genid, unicode(self))
        return URIRef(urljoin(authority, skolem))


class Literal(Identifier):
    __doc__ = py3compat.format_doctest_out("""
    RDF Literal: http://www.w3.org/TR/rdf-concepts/#section-Graph-Literal

    The lexical value of the literal is the unicode object
    The interpreted, datatyped value is available from .value

    Language tags must be valid according to :rfc:5646

    For valid XSD datatypes, the lexical form is optionally normalized
    at construction time. Default behaviour is set by rdflib.NORMALIZE_LITERALS
    and can be overridden by the normalize parameter to __new__

    Equality and hashing of Literals are done based on the lexical form, i.e.:

    >>> from rdflib.namespace import XSD

    >>> Literal('01')!=Literal('1') # clear - strings differ
    True

    but with data-type they get normalized:

    >>> Literal('01', datatype=XSD.integer)!=Literal('1', datatype=XSD.integer)
    False

    unless disabled:

    >>> Literal('01', datatype=XSD.integer, normalize=False)!=Literal('1', datatype=XSD.integer)
    True


    Value based comparison is possible:

    >>> Literal('01', datatype=XSD.integer).eq(Literal('1', datatype=XSD.float))
    True

    The eq method also provides limited support for basic python types:

    >>> Literal(1).eq(1) # fine - int compatible with xsd:integer
    True
    >>> Literal('a').eq('b') # fine - str compatible with plain-lit
    False
    >>> Literal('a', datatype=XSD.string).eq('a') # fine - str compatible with xsd:string
    True
    >>> Literal('a').eq(1) # not fine, int incompatible with plain-lit
    NotImplemented

    Greater-than/less-than ordering comparisons are also done in value
    space, when compatible datatypes are used.  Incompatible datatypes
    are ordered by DT, or by lang-tag.  For other nodes the ordering
    is None < BNode < URIRef < Literal

    Any comparison with non-rdflib Node are "NotImplemented"
    In PY2.X some stable order will be made up by python

    In PY3 this is an error.

    >>> from rdflib import Literal, XSD
    >>> lit2006 = Literal('2006-01-01',datatype=XSD.date)
    >>> lit2006.toPython()
    datetime.date(2006, 1, 1)
    >>> lit2006 < Literal('2007-01-01',datatype=XSD.date)
    True
    >>> Literal(datetime.utcnow()).datatype
    rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#dateTime')
    >>> Literal(1) > Literal(2) # by value
    False
    >>> Literal(1) > Literal(2.0) # by value
    False
    >>> Literal('1') > Literal(1) # by DT
    True
    >>> Literal('1') < Literal('1') # by lexical form
    False
    >>> Literal('a', lang='en') > Literal('a', lang='fr') # by lang-tag
    False
    >>> Literal(1) > URIRef('foo') # by node-type
    True

    The > < operators will eat this NotImplemented and either make up
    an ordering (py2.x) or throw a TypeError (py3k):

    >>> Literal(1).__gt__(2.0)
    NotImplemented


    """)


    if not py3compat.PY3:
        __slots__ = ("language", "datatype", "value", "_language",
                     "_datatype", "_value")
    else:
        __slots__ = ("_language", "_datatype", "_value")

    def __new__(cls, lexical_or_value, lang=None, datatype=None, normalize=None):

        if lang == '':
            lang = None  # no empty lang-tags in RDF

        normalize = normalize if normalize != None else rdflib.NORMALIZE_LITERALS

        if lang is not None and datatype is not None:
            raise TypeError(
                "A Literal can only have one of lang or datatype, "
                "per http://www.w3.org/TR/rdf-concepts/#section-Graph-Literal")

        if lang and not _is_valid_langtag(lang):
            raise Exception("'%s' is not a valid language tag!"%lang)

        if datatype:
            datatype = URIRef(datatype)

        value = None
        if isinstance(lexical_or_value, Literal):
            # create from another Literal instance

            lang = lang or lexical_or_value.language
            if datatype:
                # override datatype
                value = _castLexicalToPython(lexical_or_value, datatype)
            else:
                datatype = lexical_or_value.datatype
                value = lexical_or_value.value

        elif isinstance(lexical_or_value, basestring):
                # passed a string
                # try parsing lexical form of datatyped literal
                value = _castLexicalToPython(lexical_or_value, datatype)

                if value is not None and normalize:
                    _value, _datatype = _castPythonToLiteral(value)
                    if _value is not None:
                        lexical_or_value = _value

        else:
            # passed some python object
            value = lexical_or_value
            _value, _datatype = _castPythonToLiteral(lexical_or_value)

            datatype = datatype or _datatype
            if _value is not None:
                lexical_or_value = _value
            if datatype:
                lang = None


        if py3compat.PY3 and isinstance(lexical_or_value, bytes):
            lexical_or_value = lexical_or_value.decode('utf-8')

        try:
            inst = unicode.__new__(cls, lexical_or_value)
        except UnicodeDecodeError:
            inst = unicode.__new__(cls, lexical_or_value, 'utf-8')

        inst._language = lang
        inst._datatype = datatype
        inst._value = value
        return inst

    @py3compat.format_doctest_out
    def normalize(self):
        """
        Returns a new literal with a normalised lexical representation
        of this literal
        >>> from rdflib import XSD
        >>> Literal("01", datatype=XSD.integer, normalize=False).normalize()
        rdflib.term.Literal(%(u)s'1', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))

        Illegal lexical forms for the datatype given are simply passed on
        >>> Literal("a", datatype=XSD.integer, normalize=False)
        rdflib.term.Literal(%(u)s'a', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))

        """

        if self.value != None:
            return Literal(self.value, datatype=self.datatype, lang=self.language)
        else:
            return self

    @property
    def value(self):
        return self._value

    @property
    def language(self):
        return self._language

    @property
    def datatype(self):
        return self._datatype

    def __reduce__(self):
        return (Literal, (unicode(self), self.language, self.datatype),)

    def __getstate__(self):
        return (None, dict(language=self.language, datatype=self.datatype))

    def __setstate__(self, arg):
        _, d = arg
        self._language = d["language"]
        self._datatype = d["datatype"]

    @py3compat.format_doctest_out
    def __add__(self, val):
        """
        >>> Literal(1) + 1
        rdflib.term.Literal(%(u)s'2', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))
        >>> Literal("1") + "1"
        rdflib.term.Literal(%(u)s'11')
        """

        py = self.toPython()
        if not isinstance(py, Literal):
            try:
                return Literal(py + val)
            except TypeError:
                pass  # fall-through

        s = unicode.__add__(self, val)
        return Literal(s, self.language, self.datatype)

    def __nonzero__(self):
        """
        Is the Literal "True"
        This is used for if statements, bool(literal), etc.
        """
        if self.value != None:
            return bool(self.value)
        return len(self) != 0

    @py3compat.format_doctest_out
    def __neg__(self):
        """
        >>> (- Literal(1))
        rdflib.term.Literal(%(u)s'-1', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))
        >>> (- Literal(10.5))
        rdflib.term.Literal(%(u)s'-10.5', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#double'))
        >>> from rdflib.namespace import XSD
        >>> (- Literal("1", datatype=XSD.integer))
        rdflib.term.Literal(%(u)s'-1', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))

        >>> (- Literal("1"))
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        TypeError: Not a number; rdflib.term.Literal(%(u)s'1')
        >>>
        """

        if isinstance(self.value, (int, long, float)):
            return Literal(self.value.__neg__())
        else:
            raise TypeError("Not a number; %s" % repr(self))

    @py3compat.format_doctest_out
    def __pos__(self):
        """
        >>> (+ Literal(1))
        rdflib.term.Literal(%(u)s'1', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))
        >>> (+ Literal(-1))
        rdflib.term.Literal(%(u)s'-1', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))
        >>> from rdflib.namespace import XSD
        >>> (+ Literal("-1", datatype=XSD.integer))
        rdflib.term.Literal(%(u)s'-1', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))

        >>> (+ Literal("1"))
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        TypeError: Not a number; rdflib.term.Literal(%(u)s'1')
        """
        if isinstance(self.value, (int, long, float)):
            return Literal(self.value.__pos__())
        else:
            raise TypeError("Not a number; %s" % repr(self))

    @py3compat.format_doctest_out
    def __abs__(self):
        """
        >>> abs(Literal(-1))
        rdflib.term.Literal(%(u)s'1', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))

        >>> from rdflib.namespace import XSD
        >>> abs( Literal("-1", datatype=XSD.integer))
        rdflib.term.Literal(%(u)s'1', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))

        >>> abs(Literal("1"))
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        TypeError: Not a number; rdflib.term.Literal(%(u)s'1')
        """
        if isinstance(self.value, (int, long, float)):
            return Literal(self.value.__abs__())
        else:
            raise TypeError("Not a number; %s" % repr(self))

    @py3compat.format_doctest_out
    def __invert__(self):
        """
        >>> ~(Literal(-1))
        rdflib.term.Literal(%(u)s'0', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))

        >>> from rdflib.namespace import XSD
        >>> ~( Literal("-1", datatype=XSD.integer))
        rdflib.term.Literal(%(u)s'0', datatype=rdflib.term.URIRef(%(u)s'http://www.w3.org/2001/XMLSchema#integer'))

        Not working:

        >>> ~(Literal("1"))
        Traceback (most recent call last):
          File "<stdin>", line 1, in <module>
        TypeError: Not a number; rdflib.term.Literal(%(u)s'1')
        """
        if isinstance(self.value, (int, long, float)):
            return Literal(self.value.__invert__())
        else:
            raise TypeError("Not a number; %s" % repr(self))

    def __gt__(self, other):
        """

        This implements ordering for Literals,
        the other comparison methods delegate here

        This tries to implement this:
        http://www.w3.org/TR/sparql11-query/#modOrderBy

        In short, Literals with compatible data-types are orderd in value space,
        i.e.
        >>> from rdflib import XSD

        >>> Literal(1)>Literal(2) # int/int
        False
        >>> Literal(2.0)>Literal(1) # double/int
        True
        >>> from decimal import Decimal
        >>> Literal(Decimal("3.3")) > Literal(2.0) # decimal/double
        True
        >>> Literal(Decimal("3.3")) < Literal(4.0) # decimal/double
        True
        >>> Literal('b')>Literal('a') # plain lit/plain lit
        True
        >>> Literal('b')>Literal('a', datatype=XSD.string) # plain lit/xsd:string
        True

        Incompatible datatype mismatches ordered by DT

        >>> Literal(1)>Literal("2") # int>string
        False

        Langtagged literals by lang tag
        >>> Literal("a", lang="en")>Literal("a", lang="fr")
        False
        """
        if other is None:
            return True  # Everything is greater than None
        if isinstance(other, Literal):

            if self.datatype in _NUMERIC_LITERAL_TYPES and \
                    other.datatype in _NUMERIC_LITERAL_TYPES:
                return numeric_greater(self.value, other.value)

            # plain-literals and xsd:string literals
            # are "the same"
            dtself = self.datatype or _XSD_STRING
            dtother = other.datatype or _XSD_STRING

            if dtself != dtother:
                if rdflib.DAWG_LITERAL_COLLATION:
                    return NotImplemented
                else:
                    return dtself > dtother

            if self.language != other.language:
                if not self.language:
                    return False
                elif not other.language:
                    return True
                else:
                    return self.language > other.language

            if self.value != None and other.value != None:
                return self.value > other.value

            if unicode(self) != unicode(other):
                return unicode(self) > unicode(other)

            # same language, same lexical form, check real dt
            # plain-literals come before xsd:string!
            if self.datatype != other.datatype:
                if not self.datatype:
                    return False
                elif not other.datatype:
                    return True
                else:
                    return self.datatype > other.datatype

            return False  # they are the same

        elif isinstance(other, Node):
            return True  # Literal are the greatest!
        else:
            return NotImplemented  # we can only compare to nodes

    def __lt__(self, other):
        if other is None:
            return False  # Nothing is less than None
        if isinstance(other, Literal):
            try:
                return not self.__gt__(other) and not self.eq(other)
            except TypeError:
                return NotImplemented
        if isinstance(other, Node):
            return False  # all nodes are less-than Literals

        return NotImplemented

    def __le__(self, other):
        """
        >>> from rdflib.namespace import XSD
        >>> Literal('2007-01-01T10:00:00', datatype=XSD.dateTime
        ...     ) <= Literal('2007-01-01T10:00:00', datatype=XSD.dateTime)
        True
        """
        r = self.__lt__(other)
        if r:
            return True
        try:
            return self.eq(other)
        except TypeError:
            return NotImplemented

    def __ge__(self, other):
        r = self.__gt__(other)
        if r:
            return True
        try:
            return self.eq(other)
        except TypeError:
            return NotImplemented

    def _comparable_to(self, other):
        """
        Helper method to decide which things are meaningful to
        rich-compare with this literal
        """
        if isinstance(other, Literal):
            if (self.datatype and other.datatype):
                # two datatyped literals
                if not self.datatype in XSDToPython or not other.datatype in XSDToPython:
                    # non XSD DTs must match
                    if self.datatype != other.datatype:
                        return False

            else:
                # xsd:string may be compared with plain literals
                if not (self.datatype == _XSD_STRING and not other.datatype) or \
                        (other.datatype == _XSD_STRING and not self.datatype):
                    return False

                # if given lang-tag has to be case insensitive equal
                if (self.language or "").lower() != (other.language or "").lower():
                    return False

        return True

    def __hash__(self):
        """
        >>> from rdflib.namespace import XSD
        >>> a = {Literal('1', datatype=XSD.integer):'one'}
        >>> Literal('1', datatype=XSD.double) in a
        False


        "Called for the key object for dictionary operations,
        and by the built-in function hash(). Should return
        a 32-bit integer usable as a hash value for
        dictionary operations. The only required property
        is that objects which compare equal have the same
        hash value; it is advised to somehow mix together
        (e.g., using exclusive or) the hash values for the
        components of the object that also play a part in
        comparison of objects." -- 3.4.1 Basic customization (Python)

        "Two literals are equal if and only if all of the following hold:
        * The strings of the two lexical forms compare equal, character by
        character.
        * Either both or neither have language tags.
        * The language tags, if any, compare equal.
        * Either both or neither have datatype URIs.
        * The two datatype URIs, if any, compare equal, character by
        character."
        -- 6.5.1 Literal Equality (RDF: Concepts and Abstract Syntax)

        """
        res = super(Literal, self).__hash__()
        if self.language:
            res ^= hash(self.language.lower())
        if self.datatype:
            res ^= hash(self.datatype)
        return res

    @py3compat.format_doctest_out
    def __eq__(self, other):
        """
        Literals are only equal to other literals.

        "Two literals are equal if and only if all of the following hold:
        * The strings of the two lexical forms compare equal, character by character.
        * Either both or neither have language tags.
        * The language tags, if any, compare equal.
        * Either both or neither have datatype URIs.
        * The two datatype URIs, if any, compare equal, character by character."
        -- 6.5.1 Literal Equality (RDF: Concepts and Abstract Syntax)

        >>> Literal("1", datatype=URIRef("foo")) == Literal("1", datatype=URIRef("foo"))
        True
        >>> Literal("1", datatype=URIRef("foo")) == Literal("1", datatype=URIRef("foo2"))
        False

        >>> Literal("1", datatype=URIRef("foo")) == Literal("2", datatype=URIRef("foo"))
        False
        >>> Literal("1", datatype=URIRef("foo")) == "asdf"
        False
        >>> from rdflib import XSD
        >>> Literal('2007-01-01', datatype=XSD.date) == Literal('2007-01-01', datatype=XSD.date)
        True
        >>> Literal('2007-01-01', datatype=XSD.date) == date(2007, 1, 1)
        False
        >>> Literal("one", lang="en") == Literal("one", lang="en")
        True
        >>> Literal("hast", lang='en') == Literal("hast", lang='de')
        False
        >>> Literal("1", datatype=XSD.integer) == Literal(1)
        True
        >>> Literal("1", datatype=XSD.integer) == Literal("01", datatype=XSD.integer)
        True

        """
        if self is other:
            return True
        if other is None:
            return False
        if isinstance(other, Literal):
            return self.datatype == other.datatype \
                and (self.language.lower() if self.language else None) == (other.language.lower() if other.language else None) \
                and unicode.__eq__(self, other)

        return False

    def eq(self, other):
        """
        Compare the value of this literal with something else

        Either, with the value of another literal
        comparisons are then done in literal "value space",
        and according to the rules of XSD subtype-substitution/type-promotion

        OR, with a python object:

        basestring objects can be compared with plain-literals,
        or those with datatype xsd:string

        bool objects with xsd:boolean

        a int, long or float with numeric xsd types

        isodate date,time,datetime objects with xsd:date,xsd:time or xsd:datetime

        Any other operations returns NotImplemented

        """
        if isinstance(other, Literal):

            if self.datatype in _NUMERIC_LITERAL_TYPES  \
                    and other.datatype in _NUMERIC_LITERAL_TYPES:
                if self.value != None and other.value != None:
                    return self.value == other.value
                else:
                    if unicode.__eq__(self, other):
                        return True
                    raise TypeError(
                        'I cannot know that these two lexical forms do not map to the same value: %s and %s' % (self, other))
            if (self.language or "").lower() != (other.language or "").lower():
                return False

            dtself = self.datatype or _XSD_STRING
            dtother = other.datatype or _XSD_STRING

            if (dtself == _XSD_STRING and dtother == _XSD_STRING):
                # string/plain literals, compare on lexical form
                return unicode.__eq__(self, other)

            if dtself != dtother:
                if rdflib.DAWG_LITERAL_COLLATION:
                    raise TypeError("I don't know how to compare literals with datatypes %s and %s" % (
                        self.datatype, other.datatype))
                else:
                    return False

            # matching non-string DTs now - do we compare values or
            # lexical form first?  comparing two ints is far quicker -
            # maybe there are counter examples

            if self.value != None and other.value != None:

                if self.datatype in (_RDF_XMLLITERAL, _RDF_HTMLLITERAL):
                    return _isEqualXMLNode(self.value, other.value)

                return self.value == other.value
            else:

                if unicode.__eq__(self, other):
                    return True

                if self.datatype == _XSD_STRING:
                    return False  # string value space=lexical space

                # matching DTs, but not matching, we cannot compare!
                raise TypeError(
                    'I cannot know that these two lexical forms do not map to the same value: %s and %s' % (self, other))

        elif isinstance(other, Node):
            return False  # no non-Literal nodes are equal to a literal

        elif isinstance(other, basestring):
            # only plain-literals can be directly compared to strings

            # TODO: Is "blah"@en eq "blah" ?
            if self.language is not None:
                return False

            if (self.datatype == _XSD_STRING or self.datatype is None):
                return unicode(self) == other

        elif isinstance(other, (int, long, float)):
            if self.datatype in _NUMERIC_LITERAL_TYPES:
                return self.value == other
        elif isinstance(other, (date, datetime, time)):
            if self.datatype in (_XSD_DATETIME, _XSD_DATE, _XSD_TIME):
                return self.value == other
        elif isinstance(other, bool):
            if self.datatype == _XSD_BOOLEAN:
                return self.value == other

        return NotImplemented

    def neq(self, other):
        return not self.eq(other)

    @py3compat.format_doctest_out
    def n3(self, namespace_manager = None):
        r'''
        Returns a representation in the N3 format.

        Examples::

            >>> Literal("foo").n3()
            %(u)s'"foo"'

        Strings with newlines or triple-quotes::

            >>> Literal("foo\nbar").n3()
            %(u)s'"""foo\nbar"""'

            >>> Literal("''\'").n3()
            %(u)s'"\'\'\'"'

            >>> Literal('"""').n3()
            %(u)s'"\\"\\"\\""'

        Language::

            >>> Literal("hello", lang="en").n3()
            %(u)s'"hello"@en'

        Datatypes::

            >>> Literal(1).n3()
            %(u)s'"1"^^<http://www.w3.org/2001/XMLSchema#integer>'

            >>> Literal(1.0).n3()
            %(u)s'"1.0"^^<http://www.w3.org/2001/XMLSchema#double>'

            >>> Literal(True).n3()
            %(u)s'"true"^^<http://www.w3.org/2001/XMLSchema#boolean>'

        Datatype and language isn't allowed (datatype takes precedence)::

            >>> Literal(1, lang="en").n3()
            %(u)s'"1"^^<http://www.w3.org/2001/XMLSchema#integer>'

        Custom datatype::

            >>> footype = URIRef("http://example.org/ns#foo")
            >>> Literal("1", datatype=footype).n3()
            %(u)s'"1"^^<http://example.org/ns#foo>'

        Passing a namespace-manager will use it to abbreviate datatype URIs:

            >>> from rdflib import Graph
            >>> Literal(1).n3(Graph().namespace_manager)
            %(u)s'"1"^^xsd:integer'
        '''
        if namespace_manager:
            return self._literal_n3(qname_callback =
                                    namespace_manager.normalizeUri)
        else:
            return self._literal_n3()

    @py3compat.format_doctest_out
    def _literal_n3(self, use_plain=False, qname_callback=None):
        '''
        Using plain literal (shorthand) output::
            >>> from rdflib.namespace import XSD

            >>> Literal(1)._literal_n3(use_plain=True)
            %(u)s'1'

            >>> Literal(1.0)._literal_n3(use_plain=True)
            %(u)s'1e+00'

            >>> Literal(1.0, datatype=XSD.decimal)._literal_n3(use_plain=True)
            %(u)s'1.0'

            >>> Literal(1.0, datatype=XSD.float)._literal_n3(use_plain=True)
            %(u)s'"1.0"^^<http://www.w3.org/2001/XMLSchema#float>'

            >>> Literal("foo", datatype=XSD.string)._literal_n3(
            ...         use_plain=True)
            %(u)s'"foo"^^<http://www.w3.org/2001/XMLSchema#string>'

            >>> Literal(True)._literal_n3(use_plain=True)
            %(u)s'true'

            >>> Literal(False)._literal_n3(use_plain=True)
            %(u)s'false'

            >>> Literal(1.91)._literal_n3(use_plain=True)
            %(u)s'1.91e+00'

            Only limited precision available for floats:
            >>> Literal(0.123456789)._literal_n3(use_plain=True)
            %(u)s'1.234568e-01'

            >>> Literal('0.123456789',
            ...     datatype=XSD.decimal)._literal_n3(use_plain=True)
            %(u)s'0.123456789'

        Using callback for datatype QNames::

            >>> Literal(1)._literal_n3(
            ...         qname_callback=lambda uri: "xsd:integer")
            %(u)s'"1"^^xsd:integer'

        '''
        if use_plain and self.datatype in _PLAIN_LITERAL_TYPES:
            if self.value is not None:

                # this is a bit of a mess -
                # in py >=2.6 the string.format function makes this easier
                # we try to produce "pretty" output
                if self.datatype == _XSD_DOUBLE:
                    return sub("\\.?0*e", "e", u'%e' % float(self))
                elif self.datatype == _XSD_DECIMAL:
                    s = '%s' % self
                    if '.' not in s:
                        s += '.0'
                    return s

                elif self.datatype == _XSD_BOOLEAN:
                    return (u'%s' % self).lower()
                else:
                    return u'%s' % self

        encoded = self._quote_encode()

        datatype = self.datatype
        quoted_dt = None
        if datatype:
            if qname_callback:
                quoted_dt = qname_callback(datatype)
            if not quoted_dt:
                quoted_dt = "<%s>" % datatype

        language = self.language
        if language:
            return '%s@%s' % (encoded, language)
        elif datatype:
            return '%s^^%s' % (encoded, quoted_dt)
        else:
            return '%s' % encoded

    def _quote_encode(self):
        # This simpler encoding doesn't work; a newline gets encoded as "\\n",
        # which is ok in sourcecode, but we want "\n".
        # encoded = self.encode('unicode-escape').replace(
        #        '\\', '\\\\').replace('"','\\"')
        # encoded = self.replace.replace('\\', '\\\\').replace('"','\\"')

        # NOTE: Could in theory chose quotes based on quotes appearing in the
        # string, i.e. '"' and "'", but N3/turtle doesn't allow "'"(?).

        if "\n" in self:
            # Triple quote this string.
            encoded = self.replace('\\', '\\\\')
            if '"""' in self:
                # is this ok?
                encoded = encoded.replace('"""', '\\"\\"\\"')
            if encoded[-1] == '"' and encoded[-2] != '\\':
                encoded = encoded[:-1] + '\\' + '"'

            return '"""%s"""' % encoded.replace('\r', '\\r')
        else:
            return '"%s"' % self.replace(
                '\n', '\\n').replace(
                    '\\', '\\\\').replace(
                        '"', '\\"').replace(
                            '\r', '\\r')

    if not py3compat.PY3:
        def __str__(self):
            return self.encode()

    def __repr__(self):
        args = [super(Literal, self).__repr__()]
        if self.language is not None:
            args.append("lang=%s" % repr(self.language))
        if self.datatype is not None:
            args.append("datatype=%s" % repr(self.datatype))
        if self.__class__ == Literal:
            clsName = "rdflib.term.Literal"
        else:
            clsName = self.__class__.__name__
        return """%s(%s)""" % (clsName, ", ".join(args))

    def toPython(self):
        """
        Returns an appropriate python datatype derived from this RDF Literal
        """

        if self.value is not None:
            return self.value
        return self

    def md5_term_hash(self):
        """a string of hex that will be the same for two Literals that
        are the same. It is not a suitable unique id.

        Supported for backwards compatibility; new code should
        probably just use __hash__
        """
        warnings.warn(
            "method md5_term_hash is deprecated, and will be removed " +
            "removed in the future. If you use this please let rdflib-dev know!",
            category=DeprecationWarning, stacklevel=2)
        d = md5(self.encode())
        d.update(b("L"))
        return d.hexdigest()


def _parseXML(xmlstring):
    if not py3compat.PY3:
        xmlstring = xmlstring.encode('utf-8')
    retval = xml.dom.minidom.parseString(
        "<rdflibtoplevelelement>%s</rdflibtoplevelelement>" % xmlstring)
    retval.normalize()
    return retval


def _parseHTML(htmltext):
    try:
        import html5lib
        parser = html5lib.HTMLParser(
            tree=html5lib.treebuilders.getTreeBuilder("dom"))
        retval = parser.parseFragment(htmltext)
        retval.normalize()
        return retval
    except ImportError:
        raise ImportError(
            "HTML5 parser not available. Try installing" +
            " html5lib <http://code.google.com/p/html5lib>")


def _writeXML(xmlnode):
    if isinstance(xmlnode, xml.dom.minidom.DocumentFragment):
        d = xml.dom.minidom.Document()
        d.childNodes += xmlnode.childNodes
        xmlnode = d
    s = xmlnode.toxml('utf-8')
    # for clean round-tripping, remove headers -- I have great and
    # specific worries that this will blow up later, but this margin
    # is too narrow to contain them
    if s.startswith(b('<?xml version="1.0" encoding="utf-8"?>')):
        s = s[38:]
    if s.startswith(b('<rdflibtoplevelelement>')):
        s = s[23:-24]
    if s == b('<rdflibtoplevelelement/>'):
        s = b('')
    return s

# Cannot import Namespace/XSD because of circular dependencies
_XSD_PFX = 'http://www.w3.org/2001/XMLSchema#'
_RDF_PFX = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'

_RDF_XMLLITERAL = URIRef(_RDF_PFX + 'XMLLiteral')
_RDF_HTMLLITERAL = URIRef(_RDF_PFX + 'HTML')

_XSD_STRING = URIRef(_XSD_PFX + 'string')

_XSD_FLOAT = URIRef(_XSD_PFX + 'float')
_XSD_DOUBLE = URIRef(_XSD_PFX + 'double')
_XSD_DECIMAL = URIRef(_XSD_PFX + 'decimal')
_XSD_INTEGER = URIRef(_XSD_PFX + 'integer')
_XSD_BOOLEAN = URIRef(_XSD_PFX + 'boolean')

_XSD_DATETIME = URIRef(_XSD_PFX + 'dateTime')
_XSD_DATE = URIRef(_XSD_PFX + 'date')
_XSD_TIME = URIRef(_XSD_PFX + 'time')

# TODO: duration, gYearMonth, gYear, gMonthDay, gDay, gMonth

_NUMERIC_LITERAL_TYPES = (
    _XSD_INTEGER,
    _XSD_DECIMAL,
    _XSD_DOUBLE,
    URIRef(_XSD_PFX + 'float'),

    URIRef(_XSD_PFX + 'byte'),
    URIRef(_XSD_PFX + 'int'),
    URIRef(_XSD_PFX + 'long'),
    URIRef(_XSD_PFX + 'negativeInteger'),
    URIRef(_XSD_PFX + 'nonNegativeInteger'),
    URIRef(_XSD_PFX + 'nonPositiveInteger'),
    URIRef(_XSD_PFX + 'positiveInteger'),
    URIRef(_XSD_PFX + 'short'),
    URIRef(_XSD_PFX + 'unsignedByte'),
    URIRef(_XSD_PFX + 'unsignedInt'),
    URIRef(_XSD_PFX + 'unsignedLong'),
    URIRef(_XSD_PFX + 'unsignedShort'),

)

# these have "native" syntax in N3/SPARQL
_PLAIN_LITERAL_TYPES = (
    _XSD_INTEGER,
    _XSD_BOOLEAN,
    _XSD_DOUBLE,
    _XSD_DECIMAL,
)


def _castPythonToLiteral(obj):
    """
    Casts a python datatype to a tuple of the lexical value and a
    datatype URI (or None)
    """
    for pType, (castFunc, dType) in _PythonToXSD:
        if isinstance(obj, pType):
            if castFunc:
                return castFunc(obj), dType
            elif dType:
                return obj, dType
            else:
                return obj, None
    return obj, None  # TODO: is this right for the fall through case?

from decimal import Decimal

# Mappings from Python types to XSD datatypes and back (borrowed from sparta)
# datetime instances are also instances of date... so we need to order these.

# SPARQL/Turtle/N3 has shortcuts for integer, double, decimal
# python has only float - to be in tune with sparql/n3/turtle
# we default to XSD.double for float literals

# python ints are promoted to longs when overflowing
# python longs have no limit
# both map to the abstract integer type,
# rather than some concrete bit-limited datatype

_PythonToXSD = [
    (basestring, (None, None)),
    (float, (None, _XSD_DOUBLE)),
    (bool, (lambda i:str(i).lower(), _XSD_BOOLEAN)),
    (int, (None, _XSD_INTEGER)),
    (long, (None, _XSD_INTEGER)),
    (Decimal, (None, _XSD_DECIMAL)),
    (datetime, (lambda i:i.isoformat(), _XSD_DATETIME)),
    (date, (lambda i:i.isoformat(), _XSD_DATE)),
    (time, (lambda i:i.isoformat(), _XSD_TIME)),
    (xml.dom.minidom.Document, (_writeXML, _RDF_XMLLITERAL)),
    # this is a bit dirty - by accident the html5lib parser produces
    # DocumentFragments, and the xml parser Documents, letting this
    # decide what datatype to use makes roundtripping easier, but it a
    # bit random
    (xml.dom.minidom.DocumentFragment, (_writeXML, _RDF_HTMLLITERAL))
]

XSDToPython = {
    None : None, # plain literals map directly to value space
    URIRef(_XSD_PFX + 'time'): parse_time,
    URIRef(_XSD_PFX + 'date'): parse_date,
    URIRef(_XSD_PFX + 'dateTime'): parse_datetime,
    URIRef(_XSD_PFX + 'string'): None,
    URIRef(_XSD_PFX + 'normalizedString'): None,
    URIRef(_XSD_PFX + 'token'): None,
    URIRef(_XSD_PFX + 'language'): None,
    URIRef(_XSD_PFX + 'boolean'): lambda i: i.lower() in ['1', 'true'],
    URIRef(_XSD_PFX + 'decimal'): Decimal,
    URIRef(_XSD_PFX + 'integer'): long,
    URIRef(_XSD_PFX + 'nonPositiveInteger'): int,
    URIRef(_XSD_PFX + 'long'): long,
    URIRef(_XSD_PFX + 'nonNegativeInteger'): int,
    URIRef(_XSD_PFX + 'negativeInteger'): int,
    URIRef(_XSD_PFX + 'int'): long,
    URIRef(_XSD_PFX + 'unsignedLong'): long,
    URIRef(_XSD_PFX + 'positiveInteger'): int,
    URIRef(_XSD_PFX + 'short'): int,
    URIRef(_XSD_PFX + 'unsignedInt'): long,
    URIRef(_XSD_PFX + 'byte'): int,
    URIRef(_XSD_PFX + 'unsignedShort'): int,
    URIRef(_XSD_PFX + 'unsignedByte'): int,
    URIRef(_XSD_PFX + 'float'): float,
    URIRef(_XSD_PFX + 'double'): float,
    URIRef(
        _XSD_PFX + 'base64Binary'): lambda s: base64.b64decode(py3compat.b(s)),
    URIRef(_XSD_PFX + 'anyURI'): None,
    _RDF_XMLLITERAL: _parseXML,
    _RDF_HTMLLITERAL: _parseHTML
}

_toPythonMapping = {}

_toPythonMapping.update(XSDToPython)

def _castLexicalToPython(lexical, datatype):
    """
    Map a lexical form to the value-space for the given datatype
    :returns: a python object for the value or ``None``
    """
    convFunc = _toPythonMapping.get(datatype, False)
    if convFunc:
        try:
            return convFunc(lexical)
        except:
            # not a valid lexical representation for this dt
            return None
    elif convFunc is None:
        # no conv func means 1-1 lexical<->value-space mapping
        try:
            return unicode(lexical)
        except UnicodeDecodeError:
            return unicode(lexical, 'utf-8')
    else:
        # no convFunc - unknown data-type
        return None

def bind(datatype, pythontype, constructor=None, lexicalizer=None):
    """
    register a new datatype<->pythontype binding

    :param constructor: an optional function for converting lexical forms
                        into a Python instances, if not given the pythontype
                        is used directly

    :param lexicalizer: an optinoal function for converting python objects to
                        lexical form, if not given object.__str__ is used

    """
    if datatype in _toPythonMapping:
        logger.warning("datatype '%s' was already bound. Rebinding." %
                        datatype)

    if constructor == None:
        constructor = pythontype
    _toPythonMapping[datatype] = constructor
    _PythonToXSD.append((pythontype, (lexicalizer, datatype)))


class Variable(Identifier):
    """
    A Variable - this is used for querying, or in Formula aware
    graphs, where Variables can stored in the graph
    """
    __slots__ = ()

    def __new__(cls, value):
        if len(value) == 0:
            raise Exception(
                "Attempted to create variable with empty string as name!")
        if value[0] == '?':
            value = value[1:]
        return unicode.__new__(cls, value)

    def __repr__(self):
        if self.__class__ is Variable:
            clsName = "rdflib.term.Variable"
        else:
            clsName = self.__class__.__name__

        return """%s(%s)""" % (clsName, super(Variable, self).__repr__())

    def toPython(self):
        return "?%s" % self

    def n3(self, namespace_manager = None):
        return "?%s" % self

    def __reduce__(self):
        return (Variable, (unicode(self),))

    def md5_term_hash(self):
        """a string of hex that will be the same for two Variables that
        are the same. It is not a suitable unique id.

        Supported for backwards compatibility; new code should
        probably just use __hash__
        """
        warnings.warn(
            "method md5_term_hash is deprecated, and will be removed " +
            "removed in the future. If you use this please let rdflib-dev know!",
            category=DeprecationWarning, stacklevel=2)
        d = md5(self.encode())
        d.update(b("V"))
        return d.hexdigest()


class Statement(Node, tuple):

    def __new__(cls, (subject, predicate, object), context):
        warnings.warn(
            "Class Statement is deprecated, and will be removed in " +
            "the future. If you use this please let rdflib-dev know!",
            category=DeprecationWarning, stacklevel=2)
        return tuple.__new__(cls, ((subject, predicate, object), context))

    def __reduce__(self):
        return (Statement, (self[0], self[1]))

    def toPython(self):
        return (self[0], self[1])

# Nodes are ordered like this
# See http://www.w3.org/TR/sparql11-query/#modOrderBy
# we leave "space" for more subclasses of Node elsewhere
# default-dict to grazefully fail for new subclasses
_ORDERING = defaultdict(int)
_ORDERING.update({
    BNode: 10,
    Variable: 20,
    URIRef: 30,
    Literal: 40
    })


def _isEqualXMLNode(node, other):
    from xml.dom.minidom import Node

    def recurse():
        # Recursion through the children
        # In Python2, the semantics of 'map' is such that the check on
        # length would be unnecessary. In Python 3,
        # the semantics of map has changed (why, oh why???) and the check
        # for the length becomes necessary...
        if len(node.childNodes) != len(other.childNodes):
            return False
        for (nc, oc) in map(
                lambda x, y: (x, y), node.childNodes, other.childNodes):
            if not _isEqualXMLNode(nc, oc):
                return False
        # if we got here then everything is fine:
        return True

    if node is None or other is None:
        return False

    if node.nodeType != other.nodeType:
        return False

    if node.nodeType in [Node.DOCUMENT_NODE, Node.DOCUMENT_FRAGMENT_NODE]:
        return recurse()

    elif node.nodeType == Node.ELEMENT_NODE:
        # Get the basics right
        if not (node.tagName == other.tagName
                and node.namespaceURI == other.namespaceURI):
            return False

        # Handle the (namespaced) attributes; the namespace setting key
        # should be ignored, though
        # Note that the minidom orders the keys already, so we do not have
        # to worry about that, which is a bonus...
        n_keys = [
            k for k in node.attributes.keysNS()
            if k[0] != 'http://www.w3.org/2000/xmlns/']
        o_keys = [
            k for k in other.attributes.keysNS()
            if k[0] != 'http://www.w3.org/2000/xmlns/']
        if len(n_keys) != len(o_keys):
            return False
        for k in n_keys:
            if not (k in o_keys
                    and node.getAttributeNS(k[0], k[1]) ==
                    other.getAttributeNS(k[0], k[1])):
                return False

        # if we got here, the attributes are all right, we can go down
        # the tree recursively
        return recurse()

    elif node.nodeType in [
            Node.TEXT_NODE, Node.COMMENT_NODE, Node.CDATA_SECTION_NODE,
            Node.NOTATION_NODE]:
        return node.data == other.data

    elif node.nodeType == Node.PROCESSING_INSTRUCTION_NODE:
        return node.data == other.data and node.target == other.target

    elif node.nodeType == Node.ENTITY_NODE:
        return node.nodeValue == other.nodeValue

    elif node.nodeType == Node.DOCUMENT_TYPE_NODE:
        return node.publicId == other.publicId \
            and node.systemId == other.system.Id

    else:
        # should not happen, in fact
        raise Exception(
            'I dont know how to compare XML Node type: %s' % node.nodeType)

if __name__ == '__main__':
    import doctest
    doctest.testmod()
