from rdflib.py3compat import format_doctest_out

__doc__ = format_doctest_out("""
===================
Namespace Utilities
===================

RDFLib provides mechanisms for managing Namespaces.

In particular, there is a :class:`~rdflib.namespace.Namespace` class
that takes as its argument the base URI of the namespace.

.. code-block:: pycon

    >>> from rdflib.namespace import Namespace
    >>> owl = Namespace('http://www.w3.org/2002/07/owl#')

Fully qualified URIs in the namespace can be constructed either by attribute
or by dictionary access on Namespace instances:

.. code-block:: pycon

    >>> owl.seeAlso
    rdflib.term.URIRef(%(u)s'http://www.w3.org/2002/07/owl#seeAlso')
    >>> owl['seeAlso']
    rdflib.term.URIRef(%(u)s'http://www.w3.org/2002/07/owl#seeAlso')


Automatic handling of unknown predicates
-----------------------------------------

As a programming convenience, a namespace binding is automatically
created when :class:`rdflib.term.URIRef` predicates are added to the graph.

Importable namespaces
-----------------------

The following namespaces are available by directly importing from rdflib:

* RDF
* RDFS
* OWL
* XSD
* FOAF
* SKOS
* DOAP
* DC
* DCTERMS
* VOID

.. code-block:: pycon

    >>> from rdflib import OWL
    >>> OWL.seeAlso
    rdflib.term.URIRef(%(u)s'http://www.w3.org/2002/07/owl#seeAlso')

""")

import logging
logger = logging.getLogger(__name__)

import os

from urlparse import urljoin, urldefrag
from urllib import pathname2url

from rdflib.term import URIRef, Variable, _XSD_PFX, _is_valid_uri

__all__ = [
    'is_ncname', 'split_uri', 'Namespace',
    'ClosedNamespace', 'NamespaceManager',
    'XMLNS', 'RDF', 'RDFS', 'XSD', 'OWL',
    'SKOS', 'DOAP', 'FOAF', 'DC', 'DCTERMS', 'VOID']


class Namespace(unicode):

    __doc__ = format_doctest_out("""
    Utility class for quickly generating URIRefs with a common prefix

    >>> from rdflib import Namespace
    >>> n = Namespace("http://example.org/")
    >>> n.Person # as attribute
    rdflib.term.URIRef(%(u)s'http://example.org/Person')
    >>> n['first-name'] # as item - for things that are not valid python identifiers
    rdflib.term.URIRef(%(u)s'http://example.org/first-name')

    """)


    def __new__(cls, value):
        try:
            rt = unicode.__new__(cls, value)
        except UnicodeDecodeError:
            rt = unicode.__new__(cls, value, 'utf-8')
        return rt


    @property
    def title(self):
        return URIRef(self + 'title')

    def term(self, name):
        # need to handle slices explicitly because of __getitem__ override
        return URIRef(self + (name if isinstance(name, basestring) else ''))

    def __getitem__(self, key, default=None):
        return self.term(key)

    def __getattr__(self, name):
        if name.startswith("__"):  # ignore any special Python names!
            raise AttributeError
        else:
            return self.term(name)

    def __repr__(self):
        return "Namespace(%s)"%unicode.__repr__(self)


class URIPattern(unicode):

    __doc__ = format_doctest_out("""
    Utility class for creating URIs according to some pattern
    This supports either new style formatting with .format
    or old-style with %% operator

    >>> u=URIPattern("http://example.org/%%s/%%d/resource")
    >>> u%%('books', 12345)
    rdflib.term.URIRef(%(u)s'http://example.org/books/12345/resource')

    """)

    def __new__(cls, value):
        try:
            rt = unicode.__new__(cls, value)
        except UnicodeDecodeError:
            rt = unicode.__new__(cls, value, 'utf-8')
        return rt

    def __mod__(self, *args, **kwargs):
        return URIRef(unicode(self).__mod__(*args, **kwargs))

    def format(self, *args, **kwargs):
        return URIRef(unicode.format(self, *args, **kwargs))

    def __repr__(self):
        return "URIPattern(%r)"%unicode.__repr__(self)



class ClosedNamespace(object):
    """
    A namespace with a closed list of members

    Trying to create terms not listen is an error
    """

    def __init__(self, uri, terms):
        self.uri = uri
        self.__uris = {}
        for t in terms:
            self.__uris[t] = URIRef(self.uri + t)

    def term(self, name):
        uri = self.__uris.get(name)
        if uri is None:
            raise Exception(
                "term '%s' not in namespace '%s'" % (name, self.uri))
        else:
            return uri

    def __getitem__(self, key, default=None):
        return self.term(key)

    def __getattr__(self, name):
        if name.startswith("__"):  # ignore any special Python names!
            raise AttributeError
        else:
            return self.term(name)

    def __str__(self):
        return str(self.uri)

    def __repr__(self):
        return """rdf.namespace.ClosedNamespace('%s')""" % str(self.uri)


class _RDFNamespace(ClosedNamespace):
    """
    Closed namespace for RDF terms
    """
    def __init__(self):
        super(_RDFNamespace, self).__init__(
            URIRef("http://www.w3.org/1999/02/22-rdf-syntax-ns#"),
            terms=[
                # Syntax Names
                "RDF", "Description", "ID", "about", "parseType",
                "resource", "li", "nodeID", "datatype",

                # RDF Classes
                "Seq", "Bag", "Alt", "Statement", "Property",
                "List", "PlainLiteral",

                # RDF Properties
                "subject", "predicate", "object", "type",
                "value", "first", "rest",
                # and _n where n is a non-negative integer

                # RDF Resources
                "nil",

                # Added in RDF 1.1
                "XMLLiteral", "HTML", "langString"]
        )

    def term(self, name):
        try:
            i = int(name)
            return URIRef("%s_%s" % (self.uri, i))
        except ValueError:
            return super(_RDFNamespace, self).term(name)

RDF = _RDFNamespace()

RDFS = ClosedNamespace(
    uri=URIRef("http://www.w3.org/2000/01/rdf-schema#"),
    terms=[
        "Resource", "Class", "subClassOf", "subPropertyOf", "comment", "label",
        "domain", "range", "seeAlso", "isDefinedBy", "Literal", "Container",
        "ContainerMembershipProperty", "member", "Datatype"]
)

OWL = Namespace('http://www.w3.org/2002/07/owl#')

XSD = Namespace(_XSD_PFX)

SKOS = Namespace('http://www.w3.org/2004/02/skos/core#')
DOAP = Namespace('http://usefulinc.com/ns/doap#')
FOAF = Namespace('http://xmlns.com/foaf/0.1/')
DC = Namespace('http://purl.org/dc/elements/1.1/')
DCTERMS = Namespace('http://purl.org/dc/terms/')
VOID = Namespace('http://rdfs.org/ns/void#')



class NamespaceManager(object):
    """

    Class for managing prefix => namespace mappings

    Sample usage from FuXi ...

    .. code-block:: python

        ruleStore = N3RuleStore(additionalBuiltins=additionalBuiltins)
        nsMgr = NamespaceManager(Graph(ruleStore))
        ruleGraph = Graph(ruleStore,namespace_manager=nsMgr)


    and ...

    .. code-block:: pycon

        >>> import rdflib
        >>> from rdflib import Graph
        >>> from rdflib.namespace import Namespace, NamespaceManager
        >>> exNs = Namespace('http://example.com/')
        >>> namespace_manager = NamespaceManager(Graph())
        >>> namespace_manager.bind('ex', exNs, override=False)
        >>> g = Graph()
        >>> g.namespace_manager = namespace_manager
        >>> all_ns = [n for n in g.namespace_manager.namespaces()]
        >>> assert ('ex', rdflib.term.URIRef('http://example.com/')) in all_ns
        >>>

    """
    def __init__(self, graph):
        self.graph = graph
        self.__cache = {}
        self.__log = None
        self.bind("xml", u"http://www.w3.org/XML/1998/namespace")
        self.bind("rdf", RDF)
        self.bind("rdfs", RDFS)
        self.bind("xsd", XSD)

    def reset(self):
        self.__cache = {}

    def __get_store(self):
        return self.graph.store
    store = property(__get_store)

    def qname(self, uri):
        prefix, namespace, name = self.compute_qname(uri)
        if prefix == "":
            return name
        else:
            return ":".join((prefix, name))

    def normalizeUri(self, rdfTerm):
        """
        Takes an RDF Term and 'normalizes' it into a QName (using the
        registered prefix) or (unlike compute_qname) the Notation 3
        form for URIs: <...URI...>
        """
        try:
            namespace, name = split_uri(rdfTerm)
            namespace = URIRef(unicode(namespace))
        except:
            if isinstance(rdfTerm, Variable):
                return "?%s" % rdfTerm
            else:
                return "<%s>" % rdfTerm
        prefix = self.store.prefix(namespace)
        if prefix is None and isinstance(rdfTerm, Variable):
            return "?%s" % rdfTerm
        elif prefix is None:
            return "<%s>" % rdfTerm
        else:
            qNameParts = self.compute_qname(rdfTerm)
            return ':'.join([qNameParts[0], qNameParts[-1]])

    def compute_qname(self, uri, generate=True):

        if not _is_valid_uri(uri):
            raise Exception('"%s" does not look like a valid URI, I cannot serialize this. Perhaps you wanted to urlencode it?'%uri)


        if not uri in self.__cache:
            namespace, name = split_uri(uri)
            namespace = URIRef(namespace)
            prefix = self.store.prefix(namespace)
            if prefix is None:
                if not generate:
                    raise Exception(
                        "No known prefix for %s and generate=False")
                num = 1
                while 1:
                    prefix = "ns%s" % num
                    if not self.store.namespace(prefix):
                        break
                    num += 1
                self.bind(prefix, namespace)
            self.__cache[uri] = (prefix, namespace, name)
        return self.__cache[uri]

    def bind(self, prefix, namespace, override=True, replace=False):

        """bind a given namespace to the prefix

        if override, rebind, even if the given namespace is already
        bound to another prefix.

        if replace, replace any existing prefix with the new namespace

        """

        namespace = URIRef(unicode(namespace))
        # When documenting explain that override only applies in what cases
        if prefix is None:
            prefix = ''
        bound_namespace = self.store.namespace(prefix)
        # Check if the bound_namespace contains a URI
        # and if so convert it into a URIRef for comparison
        # This is to prevent duplicate namespaces with the
        # same URI
        if bound_namespace:
            bound_namespace = URIRef(bound_namespace)
        if bound_namespace and bound_namespace != namespace:

            if replace:
                self.store.bind(prefix, namespace)
                return

            # prefix already in use for different namespace
            #
            # append number to end of prefix until we find one
            # that's not in use.
            if not prefix:
                prefix = "default"
            num = 1
            while 1:
                new_prefix = "%s%s" % (prefix, num)
                tnamespace = self.store.namespace(new_prefix)
                if tnamespace and namespace == URIRef(tnamespace):
                    # the prefix is already bound to the correct
                    # namespace
                    return
                if not self.store.namespace(new_prefix):
                    break
                num += 1
            self.store.bind(new_prefix, namespace)
        else:
            bound_prefix = self.store.prefix(namespace)
            if bound_prefix is None:
                self.store.bind(prefix, namespace)
            elif bound_prefix == prefix:
                pass  # already bound
            else:
                if override or bound_prefix.startswith("_"):  # or a generated
                                                              # prefix
                    self.store.bind(prefix, namespace)

    def namespaces(self):
        for prefix, namespace in self.store.namespaces():
            namespace = URIRef(namespace)
            yield prefix, namespace

    def absolutize(self, uri, defrag=1):
        base = urljoin("file:", pathname2url(os.getcwd()))
        result = urljoin("%s/" % base, uri, allow_fragments=not defrag)
        if defrag:
            result = urldefrag(result)[0]
        if not defrag:
            if uri and uri[-1] == "#" and result[-1] != "#":
                result = "%s#" % result
        return URIRef(result)

# From: http://www.w3.org/TR/REC-xml#NT-CombiningChar
#
# * Name start characters must have one of the categories Ll, Lu, Lo,
#   Lt, Nl.
#
# * Name characters other than Name-start characters must have one of
#   the categories Mc, Me, Mn, Lm, or Nd.
#
# * Characters in the compatibility area (i.e. with character code
#   greater than #xF900 and less than #xFFFE) are not allowed in XML
#   names.
#
# * Characters which have a font or compatibility decomposition
#   (i.e. those with a "compatibility formatting tag" in field 5 of the
#   database -- marked by field 5 beginning with a "<") are not allowed.
#
# * The following characters are treated as name-start characters rather
#   than name characters, because the property file classifies them as
#   Alphabetic: [#x02BB-#x02C1], #x0559, #x06E5, #x06E6.
#
# * Characters #x20DD-#x20E0 are excluded (in accordance with Unicode
#   2.0, section 5.14).
#
# * Character #x00B7 is classified as an extender, because the property
#   list so identifies it.
#
# * Character #x0387 is added as a name character, because #x00B7 is its
#   canonical equivalent.
#
# * Characters ':' and '_' are allowed as name-start characters.
#
# * Characters '-' and '.' are allowed as name characters.

from unicodedata import category

NAME_START_CATEGORIES = ["Ll", "Lu", "Lo", "Lt", "Nl"]
NAME_CATEGORIES = NAME_START_CATEGORIES + ["Mc", "Me", "Mn", "Lm", "Nd"]
ALLOWED_NAME_CHARS = [u"\u00B7", u"\u0387", u"-", u".", u"_"]

# http://www.w3.org/TR/REC-xml-names/#NT-NCName
#  [4] NCName ::= (Letter | '_') (NCNameChar)* /* An XML Name, minus
#      the ":" */
#  [5] NCNameChar ::= Letter | Digit | '.' | '-' | '_' | CombiningChar
#      | Extender


def is_ncname(name):
    first = name[0]
    if first == "_" or category(first) in NAME_START_CATEGORIES:
        for i in xrange(1, len(name)):
            c = name[i]
            if not category(c) in NAME_CATEGORIES:
                if c in ALLOWED_NAME_CHARS:
                    continue
                return 0
            # if in compatibility area
            # if decomposition(c)!='':
            #    return 0

        return 1
    else:
        return 0

XMLNS = "http://www.w3.org/XML/1998/namespace"


def split_uri(uri):
    if uri.startswith(XMLNS):
        return (XMLNS, uri.split(XMLNS)[1])
    length = len(uri)
    for i in xrange(0, length):
        c = uri[-i - 1]
        if not category(c) in NAME_CATEGORIES:
            if c in ALLOWED_NAME_CHARS:
                continue
            for j in xrange(-1 - i, length):
                if category(uri[j]) in NAME_START_CATEGORIES or uri[j] == "_":
                    ns = uri[:j]
                    if not ns:
                        break
                    ln = uri[j:]
                    return (ns, ln)
            break
    raise Exception("Can't split '%s'" % uri)
