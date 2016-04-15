# -*- coding: utf-8 -*-
from rdflib import py3compat

__doc__ = py3compat.format_doctest_out("""
The :class:`~rdflib.resource.Resource` class wraps a
:class:`~rdflib.graph.Graph`
and a resource reference (i.e. a :class:`rdflib.term.URIRef` or
:class:`rdflib.term.BNode`) to support a resource-oriented way of
working with a graph.

It contains methods directly corresponding to those methods of the Graph
interface that relate to reading and writing data. The difference is that a
Resource also binds a resource identifier, making it possible to work without
tracking both the graph and a current subject. This makes for a "resource
oriented" style, as compared to the triple orientation of the Graph API.

Resulting generators are also wrapped so that any resource reference values
(:class:`rdflib.term.URIRef`s and :class:`rdflib.term.BNode`s) are in turn
wrapped as Resources. (Note that this behaviour differs from the corresponding
methods in :class:`~rdflib.graph.Graph`, where no such conversion takes place.)


Basic Usage Scenario
--------------------

Start by importing things we need and define some namespaces::

    >>> from rdflib import *
    >>> FOAF = Namespace("http://xmlns.com/foaf/0.1/")
    >>> CV = Namespace("http://purl.org/captsolo/resume-rdf/0.2/cv#")

Load some RDF data::

    >>> graph = Graph().parse(format='n3', data='''
    ... @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    ... @prefix xsd: <http://www.w3.org/2001/XMLSchema#>.
    ... @prefix foaf: <http://xmlns.com/foaf/0.1/> .
    ... @prefix cv: <http://purl.org/captsolo/resume-rdf/0.2/cv#> .
    ...
    ... @base <http://example.org/> .
    ...
    ... </person/some1#self> a foaf:Person;
    ...     rdfs:comment "Just a Python & RDF hacker."@en;
    ...     foaf:depiction </images/person/some1.jpg>;
    ...     foaf:homepage <http://example.net/>;
    ...     foaf:name "Some Body" .
    ...
    ... </images/person/some1.jpg> a foaf:Image;
    ...     rdfs:label "some 1"@en;
    ...     rdfs:comment "Just an image"@en;
    ...     foaf:thumbnail </images/person/some1-thumb.jpg> .
    ...
    ... </images/person/some1-thumb.jpg> a foaf:Image .
    ...
    ... [] a cv:CV;
    ...     cv:aboutPerson </person/some1#self>;
    ...     cv:hasWorkHistory [ cv:employedIn </#company>;
    ...             cv:startDate "2009-09-04"^^xsd:date ] .
    ... ''')

Create a Resource::

    >>> person = Resource(
    ...     graph, URIRef("http://example.org/person/some1#self"))

Retrieve some basic facts::

    >>> person.identifier
    rdflib.term.URIRef(%(u)s'http://example.org/person/some1#self')

    >>> person.value(FOAF.name)
    rdflib.term.Literal(%(u)s'Some Body')

    >>> person.value(RDFS.comment)
    rdflib.term.Literal(%(u)s'Just a Python & RDF hacker.', lang=%(u)s'en')

Resources can be sliced (like graphs, but the subject is fixed)::

    >>> for name in person[FOAF.name]:
    ...     print(name)
    Some Body
    >>> person[FOAF.name : Literal("Some Body")]
    True

Resources as unicode are represented by their identifiers as unicode::

    >>> %(unicode)s(person)  #doctest: +SKIP
    %(u)s'Resource(http://example.org/person/some1#self'

Resource references are also Resources, so you can easily get e.g. a qname
for the type of a resource, like::

    >>> person.value(RDF.type).qname()
    %(u)s'foaf:Person'

Or for the predicates of a resource::

    >>> sorted(
    ...     p.qname() for p in person.predicates()
    ... )  #doctest: +NORMALIZE_WHITESPACE +SKIP
    [%(u)s'foaf:depiction', %(u)s'foaf:homepage',
     %(u)s'foaf:name', %(u)s'rdf:type', %(u)s'rdfs:comment']

Follow relations and get more data from their Resources as well::

    >>> for pic in person.objects(FOAF.depiction):
    ...     print(pic.identifier)
    ...     print(pic.value(RDF.type).qname())
    ...     print(pic.label())
    ...     print(pic.comment())
    ...     print(pic.value(FOAF.thumbnail).identifier)
    http://example.org/images/person/some1.jpg
    foaf:Image
    some 1
    Just an image
    http://example.org/images/person/some1-thumb.jpg

    >>> for cv in person.subjects(CV.aboutPerson):
    ...     work = list(cv.objects(CV.hasWorkHistory))[0]
    ...     print(work.value(CV.employedIn).identifier)
    ...     print(work.value(CV.startDate))
    http://example.org/#company
    2009-09-04

It's just as easy to work with the predicates of a resource::

    >>> for s, p in person.subject_predicates():
    ...     print(s.value(RDF.type).qname())
    ...     print(p.qname())
    ...     for s, o in p.subject_objects():
    ...         print(s.value(RDF.type).qname())
    ...         print(o.value(RDF.type).qname())
    cv:CV
    cv:aboutPerson
    cv:CV
    foaf:Person

This is useful for e.g. inspection::

    >>> thumb_ref = URIRef("http://example.org/images/person/some1-thumb.jpg")
    >>> thumb = Resource(graph, thumb_ref)
    >>> for p, o in thumb.predicate_objects():
    ...     print(p.qname())
    ...     print(o.qname())
    rdf:type
    foaf:Image

Similarly, adding, setting and removing data is easy::

    >>> thumb.add(RDFS.label, Literal("thumb"))
    >>> print(thumb.label())
    thumb
    >>> thumb.set(RDFS.label, Literal("thumbnail"))
    >>> print(thumb.label())
    thumbnail
    >>> thumb.remove(RDFS.label)
    >>> list(thumb.objects(RDFS.label))
    []


Schema Example
--------------

With this artificial schema data::

    >>> graph = Graph().parse(format='n3', data='''
    ... @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    ... @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    ... @prefix owl: <http://www.w3.org/2002/07/owl#> .
    ... @prefix v: <http://example.org/def/v#> .
    ...
    ... v:Artifact a owl:Class .
    ...
    ... v:Document a owl:Class;
    ...     rdfs:subClassOf v:Artifact .
    ...
    ... v:Paper a owl:Class;
    ...     rdfs:subClassOf v:Document .
    ...
    ... v:Choice owl:oneOf (v:One v:Other) .
    ...
    ... v:Stuff a rdf:Seq; rdf:_1 v:One; rdf:_2 v:Other .
    ...
    ... ''')

From this class::

    >>> artifact = Resource(graph, URIRef("http://example.org/def/v#Artifact"))

we can get at subclasses::

    >>> subclasses = list(artifact.transitive_subjects(RDFS.subClassOf))
    >>> [c.qname() for c in subclasses]
    [%(u)s'v:Artifact', %(u)s'v:Document', %(u)s'v:Paper']

and superclasses from the last subclass::

    >>> [c.qname() for c in subclasses[-1].transitive_objects(RDFS.subClassOf)]
    [%(u)s'v:Paper', %(u)s'v:Document', %(u)s'v:Artifact']

Get items from the Choice::

    >>> choice = Resource(graph, URIRef("http://example.org/def/v#Choice"))
    >>> [it.qname() for it in choice.value(OWL.oneOf).items()]
    [%(u)s'v:One', %(u)s'v:Other']

And the sequence of Stuff::

    >>> stuff = Resource(graph, URIRef("http://example.org/def/v#Stuff"))
    >>> [it.qname() for it in stuff.seq()]
    [%(u)s'v:One', %(u)s'v:Other']

On add, other resources are auto-unboxed:
    >>> paper = Resource(graph, URIRef("http://example.org/def/v#Paper"))
    >>> paper.add(RDFS.subClassOf, artifact)
    >>> artifact in paper.objects(RDFS.subClassOf) # checks Resource instance
    True
    >>> (paper._identifier, RDFS.subClassOf, artifact._identifier) in graph
    True


Technical Details
-----------------

Comparison is based on graph and identifier::

    >>> g1 = Graph()
    >>> t1 = Resource(g1, URIRef("http://example.org/thing"))
    >>> t2 = Resource(g1, URIRef("http://example.org/thing"))
    >>> t3 = Resource(g1, URIRef("http://example.org/other"))
    >>> t4 = Resource(Graph(), URIRef("http://example.org/other"))

    >>> t1 is t2
    False

    >>> t1 == t2
    True
    >>> t1 != t2
    False

    >>> t1 == t3
    False
    >>> t1 != t3
    True

    >>> t3 != t4
    True

    >>> t3 < t1 and t1 > t3
    True
    >>> t1 >= t1 and t1 >= t3
    True
    >>> t1 <= t1 and t3 <= t1
    True

    >>> t1 < t1 or t1 < t3 or t3 > t1 or t3 > t3
    False

Hash is computed from graph and identifier::

    >>> g1 = Graph()
    >>> t1 = Resource(g1, URIRef("http://example.org/thing"))

    >>> hash(t1) == hash(Resource(g1, URIRef("http://example.org/thing")))
    True

    >>> hash(t1) == hash(Resource(Graph(), t1.identifier))
    False
    >>> hash(t1) == hash(Resource(Graph(), URIRef("http://example.org/thing")))
    False

The Resource class is suitable as a base class for mapper toolkits. For
example, consider this utility for accessing RDF properties via qname-like
attributes::

    >>> class Item(Resource):
    ...
    ...     def __getattr__(self, p):
    ...         return list(self.objects(self._to_ref(*p.split('_', 1))))
    ...
    ...     def _to_ref(self, pfx, name):
    ...         return URIRef(self._graph.store.namespace(pfx) + name)

It works as follows::

    >>> graph = Graph().parse(format='n3', data='''
    ... @prefix rdfs: <http://www.w3.org/2000/01/rdf-schema#> .
    ... @prefix foaf: <http://xmlns.com/foaf/0.1/> .
    ...
    ... @base <http://example.org/> .
    ... </person/some1#self>
    ...     foaf:name "Some Body";
    ...     foaf:depiction </images/person/some1.jpg> .
    ... </images/person/some1.jpg> rdfs:comment "Just an image"@en .
    ... ''')

    >>> person = Item(graph, URIRef("http://example.org/person/some1#self"))

    >>> print(person.foaf_name[0])
    Some Body

The mechanism for wrapping references as resources cooperates with subclasses.
Therefore, accessing referenced resources automatically creates new ``Item``
objects::

    >>> isinstance(person.foaf_depiction[0], Item)
    True

    >>> print(person.foaf_depiction[0].rdfs_comment[0])
    Just an image

""")

from rdflib.term import Node, BNode, URIRef
from rdflib.namespace import RDF
from rdflib.paths import Path

__all__ = ['Resource']


class Resource(object):

    def __init__(self, graph, subject):
        self._graph = graph
        self._identifier = subject

    graph = property(lambda self: self._graph)

    identifier = property(lambda self: self._identifier)

    def __hash__(self):
        return hash(Resource) ^ hash(self._graph) ^ hash(self._identifier)

    def __eq__(self, other):
        return (isinstance(other, Resource) and
                self._graph == other._graph and
                self._identifier == other._identifier)

    __ne__ = lambda self, other: not self == other

    def __lt__(self, other):
        if isinstance(other, Resource):
            return self._identifier < other._identifier
        else:
            return False

    __gt__ = lambda self, other: not (self < other or self == other)
    __le__ = lambda self, other: self < other or self == other
    __ge__ = lambda self, other: not self < other

    def __unicode__(self):
        return unicode(self._identifier)

    if py3compat.PY3:
        __str__ = __unicode__

    def add(self, p, o):
        if isinstance(o, Resource):
            o = o._identifier

        self._graph.add((self._identifier, p, o))

    def remove(self, p, o=None):
        if isinstance(o, Resource):
            o = o._identifier

        self._graph.remove((self._identifier, p, o))

    def set(self, p, o):
        if isinstance(o, Resource):
            o = o._identifier

        self._graph.set((self._identifier, p, o))

    def subjects(self, predicate=None):  # rev
        return self._resources(
            self._graph.subjects(predicate, self._identifier))

    def predicates(self, o=None):
        if isinstance(o, Resource):
            o = o._identifier

        return self._resources(
            self._graph.predicates(self._identifier, o))

    def objects(self, predicate=None):
        return self._resources(
            self._graph.objects(self._identifier, predicate))

    def subject_predicates(self):
        return self._resource_pairs(
            self._graph.subject_predicates(self._identifier))

    def subject_objects(self):
        return self._resource_pairs(
            self._graph.subject_objects(self._identifier))

    def predicate_objects(self):
        return self._resource_pairs(
            self._graph.predicate_objects(self._identifier))

    def value(self, p=RDF.value, o=None, default=None, any=True):
        if isinstance(o, Resource):
            o = o._identifier

        return self._cast(
            self._graph.value(self._identifier, p, o, default, any))

    def label(self):
        return self._graph.label(self._identifier)

    def comment(self):
        return self._graph.comment(self._identifier)

    def items(self):
        return self._resources(self._graph.items(self._identifier))

    def transitive_objects(self, predicate, remember=None):
        return self._resources(self._graph.transitive_objects(
            self._identifier, predicate, remember))

    def transitive_subjects(self, predicate, remember=None):
        return self._resources(self._graph.transitive_subjects(
            predicate, self._identifier, remember))

    def seq(self):
        return self._resources(self._graph.seq(self._identifier))

    def qname(self):
        return self._graph.qname(self._identifier)

    def _resource_pairs(self, pairs):
        for s1, s2 in pairs:
            yield self._cast(s1), self._cast(s2)

    def _resource_triples(self, triples):
        for s,p,o in triples:
            yield self._cast(s), self._cast(p), self._cast(o)

    def _resources(self, nodes):
        for node in nodes:
            yield self._cast(node)

    def _cast(self, node):
        if isinstance(node, (BNode, URIRef)):
            return self._new(node)
        else:
            return node

    def __iter__(self):
        return self._resource_triples(self._graph.triples((self.identifier, None, None)))

    def __getitem__(self, item):
        if isinstance(item, slice):
            if item.step:
                raise TypeError("Resources fix the subject for slicing, and can only be sliced by predicate/object. ")
            p,o=item.start,item.stop
            if p is None and o is None:
                return self.predicate_objects()
            elif p is None:
                return self.predicates(o)
            elif o is None:
                return self.objects(p)
            else:
                return (self.identifier, p, o) in self._graph
        elif isinstance(item, (Node, Path)):
            return self.objects(item)
        else:
            raise TypeError("You can only index a resource by a single rdflib term, a slice of rdflib terms, not %s (%s)"%(item, type(item)))

    def __setitem__(self, item, value):
        self.set(item, value)

    def _new(self, subject):
        return type(self)(self._graph, subject)

    def __str__(self):
        return 'Resource(%s)' % self._identifier

    def __repr__(self):
        return 'Resource(%s,%s)' % (self._graph, self._identifier)
