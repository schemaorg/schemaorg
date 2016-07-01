"""A pure Python package providing the core RDF constructs.

The packages is intended to provide the core RDF types and interfaces
for working with RDF. The package defines a plugin interface for
parsers, stores, and serializers that other packages can use to
implement parsers, stores, and serializers that will plug into the
rdflib package.

The primary interface `rdflib` exposes to work with RDF is
`rdflib.graph.Graph`.

A tiny example:

    >>> from rdflib import Graph, URIRef, Literal

    >>> g = Graph()
    >>> result = g.parse("http://www.w3.org/2000/10/swap/test/meet/blue.rdf")

    >>> print("graph has %s statements." % len(g))
    graph has 4 statements.
    >>>
    >>> for s, p, o in g:
    ...     if (s, p, o) not in g:
    ...         raise Exception("It better be!")

    >>> s = g.serialize(format='nt')
    >>>
    >>> sorted(g) == [
    ...  (URIRef(u'http://meetings.example.com/cal#m1'),
    ...   URIRef(u'http://www.example.org/meeting_organization#homePage'),
    ...   URIRef(u'http://meetings.example.com/m1/hp')),
    ...  (URIRef(u'http://www.example.org/people#fred'),
    ...   URIRef(u'http://www.example.org/meeting_organization#attending'),
    ...   URIRef(u'http://meetings.example.com/cal#m1')),
    ...  (URIRef(u'http://www.example.org/people#fred'),
    ...   URIRef(u'http://www.example.org/personal_details#GivenName'),
    ...   Literal(u'Fred')),
    ...  (URIRef(u'http://www.example.org/people#fred'),
    ...   URIRef(u'http://www.example.org/personal_details#hasEmail'),
    ...   URIRef(u'mailto:fred@example.com'))
    ... ]
    True

"""
__docformat__ = "restructuredtext en"

# The format of the __version__ line is matched by a regex in setup.py
__version__ = "4.2.1"
__date__ = "2015/08/12"

__all__ = [
    'URIRef',
    'BNode',
    'Literal',
    'Variable',

    'Namespace',

    'Dataset',
    'Graph',
    'ConjunctiveGraph',

    'RDF',
    'RDFS',
    'OWL',
    'XSD',

    'util',
]

import sys
assert sys.version_info >= (2, 5, 0), "rdflib requires Python 2.5 or higher"
del sys

import logging
try:
    import __main__
    if not hasattr(__main__, '__file__'):
        # show log messages in interactive mode
        logging.basicConfig(level=logging.INFO)
except ImportError:
    #Main already imported from elsewhere
    import warnings
    warnings.warn('__main__ already imported', ImportWarning)
    del warnings
    
logger = logging.getLogger(__name__)
logger.info("RDFLib Version: %s" % __version__)


try:
    unichr(0x10FFFF)
except ValueError:
    import warnings
    warnings.warn(
        'You are using a narrow Python build!\n'
        'This means that your Python does not properly support chars > 16bit.\n'
        'On your system chars like c=u"\\U0010FFFF" will have a len(c)==2.\n'
        'As this can cause hard to debug problems with string processing\n'
        '(slicing, regexp, ...) later on, we strongly advise to use a wide\n'
        'Python build in production systems.',
        ImportWarning)
    del warnings


NORMALIZE_LITERALS = True
"""
If True - Literals lexical forms are normalized when created.
I.e. the lexical forms is parsed according to data-type, then the
stored lexical form is the re-serialized value that was parsed.

Illegal values for a datatype are simply kept.  The normalized keyword
for Literal.__new__ can override this.

For example:

>>> from rdflib import Literal,XSD
>>> Literal("01", datatype=XSD.int)
rdflib.term.Literal(u'1', datatype=rdflib.term.URIRef(u'http://www.w3.org/2001/XMLSchema#integer'))

This flag may be changed at any time, but will only affect literals
created after that time, previously created literals will remain
(un)normalized.

"""


DAWG_LITERAL_COLLATION = False
"""
DAWG_LITERAL_COLLATION determines how literals are ordered or compared
to each other.

In SPARQL, applying the >,<,>=,<= operators to literals of
incompatible data-types is an error, i.e:

Literal(2)>Literal('cake') is neither true nor false, but an error.

This is a problem in PY3, where lists of Literals of incompatible
types can no longer be sorted.

Setting this flag to True gives you strict DAWG/SPARQL compliance,
setting it to False will order Literals with incompatible datatypes by
datatype URI

In particular, this determines how the rich comparison operators for
Literal work, eq, __neq__, __lt__, etc.
"""

from rdflib.term import (
    URIRef, BNode, Literal, Variable)

from rdflib.namespace import Namespace

from rdflib.graph import Dataset, Graph, ConjunctiveGraph

from rdflib.namespace import RDF, RDFS, OWL, XSD

from rdflib import plugin
from rdflib import query
# tedious sop to flake8
assert plugin
assert query

from rdflib import util
