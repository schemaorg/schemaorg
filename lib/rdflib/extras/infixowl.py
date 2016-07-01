#!/usr/bin/env python
# -*- coding: utf-8 -*-
from rdflib import py3compat

__doc__ = py3compat.format_doctest_out("""
RDFLib Python binding for OWL Abstract Syntax

see: http://www.w3.org/TR/owl-semantics/syntax.html
     http://owl-workshop.man.ac.uk/acceptedLong/submission_9.pdf

3.2.3 Axioms for complete classes without using owl:equivalentClass

Named class description of type 2 (with owl:oneOf) or type 4-6
(with owl:intersectionOf, owl:unionOf or owl:complementOf


Uses Manchester Syntax for __repr__

>>> exNs = Namespace('http://example.com/')
>>> namespace_manager = NamespaceManager(Graph())
>>> namespace_manager.bind('ex', exNs, override=False)
>>> namespace_manager.bind('owl', OWL_NS, override=False)
>>> g = Graph()
>>> g.namespace_manager = namespace_manager

Now we have an empty graph, we can construct OWL classes in it
using the Python classes defined in this module

>>> a = Class(exNs.Opera, graph=g)

Now we can assert rdfs:subClassOf and owl:equivalentClass relationships
(in the underlying graph) with other classes using the 'subClassOf'
and 'equivalentClass' descriptors which can be set to a list
of objects for the corresponding predicates.

>>> a.subClassOf = [exNs.MusicalWork]

We can then access the rdfs:subClassOf relationships

>>> print(list(a.subClassOf))
[Class: ex:MusicalWork ]

This can also be used against already populated graphs:

>>> owlGraph = Graph().parse(OWL_NS) #doctest: +SKIP
>>> namespace_manager.bind('owl', OWL_NS, override=False) #doctest: +SKIP
>>> owlGraph.namespace_manager = namespace_manager #doctest: +SKIP
>>> list(Class(OWL_NS.Class, graph=owlGraph).subClassOf) #doctest: +SKIP
[Class: rdfs:Class ]

Operators are also available. For instance we can add ex:Opera to the extension
of the ex:CreativeWork class via the '+=' operator

>>> a #doctest: +SKIP
Class: ex:Opera SubClassOf: ex:MusicalWork
>>> b = Class(exNs.CreativeWork, graph=g)
>>> b += a
>>> print(sorted(a.subClassOf, key=lambda c:c.identifier)) #doctest: +SKIP
[Class: ex:CreativeWork , Class: ex:MusicalWork ]

And we can then remove it from the extension as well

>>> b -= a
>>> a #doctest: +SKIP
Class: ex:Opera SubClassOf: ex:MusicalWork

Boolean class constructions can also  be created with Python operators.
For example, The | operator can be used to construct a class consisting of a
owl:unionOf the operands:

>>> c =  a | b | Class(exNs.Work, graph=g)
>>> c #doctest: +SKIP
( ex:Opera OR ex:CreativeWork OR ex:Work )

Boolean class expressions can also be operated as lists (using python list
operators)

>>> del c[c.index(Class(exNs.Work, graph=g))]
>>> c #doctest: +SKIP
( ex:Opera OR ex:CreativeWork )

The '&' operator can be used to construct class intersection:

>>> woman = Class(exNs.Female, graph=g) & Class(exNs.Human, graph=g)
>>> woman.identifier = exNs.Woman
>>> woman #doctest: +SKIP
( ex:Female AND ex:Human )
>>> len(woman)
2

Enumerated classes can also be manipulated

>>> contList = [Class(exNs.Africa, graph=g), Class(exNs.NorthAmerica, graph=g)]
>>> EnumeratedClass(members=contList, graph=g) #doctest: +SKIP
{ ex:Africa ex:NorthAmerica }

owl:Restrictions can also be instantiated:

>>> Restriction(exNs.hasParent, graph=g, allValuesFrom=exNs.Human) #doctest: +SKIP
( ex:hasParent ONLY ex:Human )

Restrictions can also be created using Manchester OWL syntax in 'colloquial'
Python
>>> exNs.hasParent | some | Class(exNs.Physician, graph=g) #doctest: +SKIP
( ex:hasParent SOME ex:Physician )

>>> Property(exNs.hasParent,graph=g) | max | Literal(1) #doctest: +SKIP
( ex:hasParent MAX 1 )

>>> print(g.serialize(format='pretty-xml')) #doctest: +SKIP

""")

import itertools

from rdflib import (
    BNode,
    Literal,
    Namespace,
    RDF,
    RDFS,
    URIRef,
    Variable
)
from rdflib.graph import Graph
from rdflib.collection import Collection
from rdflib.namespace import XSD as _XSD_NS
from rdflib.namespace import NamespaceManager
from rdflib.term import Identifier
from rdflib.util import first

import logging
logger = logging.getLogger(__name__)


"""
From: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/384122

Python has the wonderful "in" operator and it would be nice to have additional
infix operator like this. This recipe shows how (almost) arbitrary infix
operators can be defined.

"""

__all__ = [
    'OWL_NS',
    'nsBinds',
    'ACE_NS',
    'CLASS_RELATIONS',
    'some',
    'only',
    'max',
    'min',
    'exactly',
    'value',
    'PropertyAbstractSyntax',
    'AllClasses',
    'AllDifferent',
    'AllProperties',
    'AnnotatableTerms',
    'BooleanClass',
    'Callable',
    'CastClass',
    'Class',
    'ClassNamespaceFactory',
    'classOrIdentifier',
    'classOrTerm',
    'CommonNSBindings',
    'ComponentTerms',
    'DeepClassClear',
    'EnumeratedClass',
    'generateQName',
    'GetIdentifiedClasses',
    'Individual',
    'MalformedClass',
    'manchesterSyntax',
    'Ontology',
    'OWLRDFListProxy',
    'Property',
    'propertyOrIdentifier',
    'Restriction',
    'termDeletionDecorator',
]

# definition of an Infix operator class
# this recipe also works in jython
# calling sequence for the infix is either:
#  x |op| y
# or:
# x <<op>> y


class Infix:
    def __init__(self, function):
        self.function = function

    def __ror__(self, other):
        return Infix(lambda x, self=self, other=other: self.function(other, x))

    def __or__(self, other):
        return self.function(other)

    def __rlshift__(self, other):
        return Infix(lambda x, self=self, other=other: self.function(other, x))

    def __rshift__(self, other):
        return self.function(other)

    def __call__(self, value1, value2):
        return self.function(value1, value2)

OWL_NS = Namespace("http://www.w3.org/2002/07/owl#")

nsBinds = {
    'skos': 'http://www.w3.org/2004/02/skos/core#',
    'rdf': RDF,
    'rdfs': RDFS,
    'owl': OWL_NS,
    'list': URIRef('http://www.w3.org/2000/10/swap/list#'),
    'dc': "http://purl.org/dc/elements/1.1/",
}


def generateQName(graph, uri):
    prefix, uri, localName = graph.compute_qname(classOrIdentifier(uri))
    return u':'.join([prefix, localName])


def classOrTerm(thing):
    if isinstance(thing, Class):
        return thing.identifier
    else:
        assert isinstance(thing, (URIRef, BNode, Literal))
        return thing


def classOrIdentifier(thing):
    if isinstance(thing, (Property, Class)):
        return thing.identifier
    else:
        assert isinstance(thing, (URIRef, BNode)), \
            "Expecting a Class, Property, URIRef, or BNode.. not a %s" % thing
        return thing


def propertyOrIdentifier(thing):
    if isinstance(thing, Property):
        return thing.identifier
    else:
        assert isinstance(thing, URIRef)
        return thing


def manchesterSyntax(thing, store, boolean=None, transientList=False):
    """
    Core serialization
    """
    assert thing is not None
    if boolean:
        if transientList:
            liveChildren = iter(thing)
            children = [manchesterSyntax(child, store) for child in thing]
        else:
            liveChildren = iter(Collection(store, thing))
            children = [manchesterSyntax(
                child, store) for child in Collection(store, thing)]
        if boolean == OWL_NS.intersectionOf:
            childList = []
            named = []
            for child in liveChildren:
                if isinstance(child, URIRef):
                    named.append(child)
                else:
                    childList.append(child)
            if named:
                def castToQName(x):
                    prefix, uri, localName = store.compute_qname(x)
                    return ':'.join([prefix, localName])

                if len(named) > 1:
                    prefix = u'( ' + u' AND '.join(map(
                        castToQName, named)) + u' )'
                else:
                    prefix = manchesterSyntax(named[0], store)
                if childList:
                    return str(prefix) + u' THAT ' + u' AND '.join(
                        [str(manchesterSyntax(x, store)) for x in childList])
                else:
                    return prefix
            else:
                return u'( ' + u' AND '.join(
                    [str(c) for c in children]) + u' )'
        elif boolean == OWL_NS.unionOf:
            return u'( ' + u' OR '.join([str(c) for c in children]) + ' )'
        elif boolean == OWL_NS.oneOf:
            return u'{ ' + u' '.join([str(c) for c in children]) + ' }'
        else:
            assert boolean == OWL_NS.complementOf
    elif OWL_NS.Restriction in store.objects(
            subject=thing, predicate=RDF.type):
        prop = list(
            store.objects(subject=thing, predicate=OWL_NS.onProperty))[0]
        prefix, uri, localName = store.compute_qname(prop)
        propString = u':'.join([prefix, localName])
        label = first(store.objects(subject=prop, predicate=RDFS.label))
        if label:
            propString = "'%s'" % label
        for onlyClass in store.objects(
                subject=thing, predicate=OWL_NS.allValuesFrom):
            return u'( %s ONLY %s )' % (
                propString, manchesterSyntax(onlyClass, store))
        for val in store.objects(subject=thing, predicate=OWL_NS.hasValue):
            return u'( %s VALUE %s )' % (
                propString,
                manchesterSyntax(val.encode('utf-8', 'ignore'), store))
        for someClass in store.objects(
                subject=thing, predicate=OWL_NS.someValuesFrom):
            return u'( %s SOME %s )' % (
                propString, manchesterSyntax(someClass, store))
        cardLookup = {OWL_NS.maxCardinality: 'MAX',
                      OWL_NS.minCardinality: 'MIN',
                      OWL_NS.cardinality: 'EQUALS'}
        for s, p, o in store.triples_choices(
                (thing, list(cardLookup.keys()), None)):
            return u'( %s %s %s )' % (
                propString, cardLookup[p], o.encode('utf-8', 'ignore'))
    compl = list(store.objects(subject=thing, predicate=OWL_NS.complementOf))
    if compl:
        return '( NOT %s )' % (manchesterSyntax(compl[0], store))
    else:
        prolog = '\n'.join(
            ["PREFIX %s: <%s>" % (k, nsBinds[k]) for k in nsBinds])
        qstr = \
            prolog + \
            "\nSELECT ?p ?bool WHERE {?class a owl:Class; ?p ?bool ." + \
            "?bool rdf:first ?foo }"
        initb = {Variable("?class"): thing}
        for boolProp, col in \
                store.query(qstr, processor="sparql", initBindings=initb):
            if not isinstance(thing, URIRef):
                return manchesterSyntax(col, store, boolean=boolProp)
        try:
            prefix, uri, localName = store.compute_qname(thing)
            qname = u':'.join([prefix, localName])
        except Exception:
            if isinstance(thing, BNode):
                return thing.n3()
            return u"<" + thing + ">"
            logger.debug(list(store.objects(subject=thing, predicate=RDF.type)))
            raise
            return '[]'  # +thing._id.encode('utf-8')+'</em>'
        label = first(Class(thing, graph=store).label)
        if label:
            return label.encode('utf-8', 'ignore')
        else:
            return qname.encode('utf-8', 'ignore')


def GetIdentifiedClasses(graph):
    for c in graph.subjects(predicate=RDF.type, object=OWL_NS.Class):
        if isinstance(c, URIRef):
            yield Class(c)


def termDeletionDecorator(prop):
    def someFunc(func):
        func.property = prop
        return func
    return someFunc


class TermDeletionHelper:
    def __init__(self, prop):
        self.prop = prop

    def __call__(self, f):
        def _remover(inst):
            inst.graph.remove((inst.identifier, self.prop, None))
        return _remover


class Individual(object):
    """
    A typed individual
    """
    factoryGraph = Graph()

    def serialize(self, graph):
        for fact in self.factoryGraph.triples((self.identifier, None, None)):
            graph.add(fact)

    def __init__(self, identifier=None, graph=None):
        self.__identifier = identifier is not None and identifier or BNode()
        if graph is None:
            self.graph = self.factoryGraph
        else:
            self.graph = graph
        self.qname = None
        if not isinstance(self.identifier, BNode):
            try:
                prefix, uri, localName = self.graph.compute_qname(
                    self.identifier)
                self.qname = u':'.join([prefix, localName])
            except:
                pass

    def clearInDegree(self):
        self.graph.remove((None, None, self.identifier))

    def clearOutDegree(self):
        self.graph.remove((self.identifier, None, None))

    def delete(self):
        self.clearInDegree()
        self.clearOutDegree()

    def replace(self, other):
        for s, p, o in self.graph.triples((None, None, self.identifier)):
            self.graph.add((s, p, classOrIdentifier(other)))
        self.delete()

    def _get_type(self):
        for _t in self.graph.objects(
                subject=self.identifier, predicate=RDF.type):
            yield _t

    def _set_type(self, kind):
        if not kind:
            return
        if isinstance(kind, (Individual, Identifier)):
            self.graph.add(
                (self.identifier, RDF.type, classOrIdentifier(kind)))
        else:
            for c in kind:
                assert isinstance(c, (Individual, Identifier))
                self.graph.add(
                    (self.identifier, RDF.type, classOrIdentifier(c)))

    @TermDeletionHelper(RDF.type)
    def _delete_type(self):
        """
        >>> g = Graph()
        >>> b=Individual(OWL_NS.Restriction,g)
        >>> b.type = RDF.Resource
        >>> len(list(b.type))
        1
        >>> del b.type
        >>> len(list(b.type))
        0
        """
        pass

    type = property(_get_type, _set_type, _delete_type)

    def _get_identifier(self):
        return self.__identifier

    def _set_identifier(self, i):
        assert i
        if i != self.__identifier:
            oldStmtsOut = [(p, o) for s, p, o in self.graph.triples(
                (self.__identifier, None, None))]
            oldStmtsIn = [(s, p) for s, p, o in self.graph.triples(
                (None, None, self.__identifier))]
            for p1, o1 in oldStmtsOut:
                self.graph.remove((self.__identifier, p1, o1))
            for s1, p1 in oldStmtsIn:
                self.graph.remove((s1, p1, self.__identifier))
            self.__identifier = i
            self.graph.addN(
                [(i, p1, o1, self.graph) for p1, o1 in oldStmtsOut])
            self.graph.addN([(s1, p1, i, self.graph) for s1, p1 in oldStmtsIn])
        if not isinstance(i, BNode):
            try:
                prefix, uri, localName = self.graph.compute_qname(i)
                self.qname = u':'.join([prefix, localName])
            except:
                pass

    identifier = property(_get_identifier, _set_identifier)

    def _get_sameAs(self):
        for _t in self.graph.objects(
                subject=self.identifier, predicate=OWL_NS.sameAs):
            yield _t

    def _set_sameAs(self, term):
        # if not kind:
        #     return
        if isinstance(term, (Individual, Identifier)):
            self.graph.add(
                (self.identifier, OWL_NS.sameAs, classOrIdentifier(term)))
        else:
            for c in term:
                assert isinstance(c, (Individual, Identifier))
                self.graph.add(
                    (self.identifier, OWL_NS.sameAs, classOrIdentifier(c)))

    @TermDeletionHelper(OWL_NS.sameAs)
    def _delete_sameAs(self):
        pass

    sameAs = property(_get_sameAs, _set_sameAs, _delete_sameAs)


ACE_NS = Namespace('http://attempto.ifi.uzh.ch/ace_lexicon#')


class AnnotatableTerms(Individual):
    """
    Terms in an OWL ontology with rdfs:label and rdfs:comment
    """
    def __init__(self,
                 identifier,
                 graph=None,
                 nameAnnotation=None,
                 nameIsLabel=False):
        super(AnnotatableTerms, self).__init__(identifier, graph)
        if nameAnnotation:
            self.setupACEAnnotations()
            self.PN_sgProp.extent = [(self.identifier,
                                      self.handleAnnotation(nameAnnotation))]
            if nameIsLabel:
                self.label = [nameAnnotation]

    def handleAnnotation(self, val):
        return val if isinstance(val, Literal) else Literal(val)

    def setupACEAnnotations(self):
        self.graph.bind('ace', ACE_NS, override=False)

        # PN_sg singular form of a proper name ()
        self.PN_sgProp = Property(ACE_NS.PN_sg,
                                  baseType=OWL_NS.AnnotationProperty,
                                  graph=self.graph)

        # CN_sg singular form of a common noun
        self.CN_sgProp = Property(ACE_NS.CN_sg,
                                  baseType=OWL_NS.AnnotationProperty,
                                  graph=self.graph)

        # CN_pl plural form of a common noun
        self.CN_plProp = Property(ACE_NS.CN_pl,
                                  baseType=OWL_NS.AnnotationProperty,
                                  graph=self.graph)

        # singular form of a transitive verb
        self.TV_sgProp = Property(ACE_NS.TV_sg,
                                  baseType=OWL_NS.AnnotationProperty,
                                  graph=self.graph)

        # plural form of a transitive verb
        self.TV_plProp = Property(ACE_NS.TV_pl,
                                  baseType=OWL_NS.AnnotationProperty,
                                  graph=self.graph)

        # past participle form a transitive verb
        self.TV_vbgProp = Property(ACE_NS.TV_vbg,
                                   baseType=OWL_NS.AnnotationProperty,
                                   graph=self.graph)

    def _get_comment(self):
        for comment in self.graph.objects(
                subject=self.identifier, predicate=RDFS.comment):
            yield comment

    def _set_comment(self, comment):
        if not comment:
            return
        if isinstance(comment, Identifier):
            self.graph.add((self.identifier, RDFS.comment, comment))
        else:
            for c in comment:
                self.graph.add((self.identifier, RDFS.comment, c))

    @TermDeletionHelper(RDFS.comment)
    def _del_comment(self):
        pass

    comment = property(_get_comment, _set_comment, _del_comment)

    def _get_seeAlso(self):
        for sA in self.graph.objects(
                subject=self.identifier, predicate=RDFS.seeAlso):
            yield sA

    def _set_seeAlso(self, seeAlsos):
        if not seeAlsos:
            return
        for s in seeAlsos:
            self.graph.add((self.identifier, RDFS.seeAlso, s))

    @TermDeletionHelper(RDFS.seeAlso)
    def _del_seeAlso(self):
        pass
    seeAlso = property(_get_seeAlso, _set_seeAlso, _del_seeAlso)

    def _get_label(self):
        for label in self.graph.objects(
                subject=self.identifier, predicate=RDFS.label):
            yield label

    def _set_label(self, label):
        if not label:
            return
        if isinstance(label, Identifier):
            self.graph.add((self.identifier, RDFS.label, label))
        else:
            for l in label:
                self.graph.add((self.identifier, RDFS.label, l))

    @TermDeletionHelper(RDFS.label)
    def _delete_label(self):
        """
        >>> g=Graph()
        >>> b=Individual(OWL_NS.Restriction,g)
        >>> b.label = Literal('boo')
        >>> len(list(b.label))
        1
        >>> del b.label
        >>> len(list(b.label))
        0
        """
        pass

    label = property(_get_label, _set_label, _delete_label)


class Ontology(AnnotatableTerms):
    """ The owl ontology metadata"""
    def __init__(self,
                 identifier=None, imports=None, comment=None, graph=None):
        super(Ontology, self).__init__(identifier, graph)
        self.imports = imports and imports or []
        self.comment = comment and comment or []
        if (self.identifier, RDF.type, OWL_NS.Ontology) not in self.graph:
            self.graph.add((self.identifier, RDF.type, OWL_NS.Ontology))

    def setVersion(self, version):
        self.graph.set((self.identifier, OWL_NS.versionInfo, version))

    def _get_imports(self):
        for owl in self.graph.objects(
                subject=self.identifier, predicate=OWL_NS['imports']):
            yield owl

    def _set_imports(self, other):
        if not other:
            return
        for o in other:
            self.graph.add((self.identifier, OWL_NS['imports'], o))

    @TermDeletionHelper(OWL_NS['imports'])
    def _del_imports(self):
        pass

    imports = property(_get_imports, _set_imports, _del_imports)


def AllClasses(graph):
    prevClasses = set()
    for c in graph.subjects(predicate=RDF.type, object=OWL_NS.Class):
        if c not in prevClasses:
            prevClasses.add(c)
            yield Class(c)


def AllProperties(graph):
    prevProps = set()
    for s, p, o in graph.triples_choices(
        (None, RDF.type, [OWL_NS.SymmetricProperty,
                          OWL_NS.FunctionalProperty,
                          OWL_NS.InverseFunctionalProperty,
                          OWL_NS.TransitiveProperty,
                          OWL_NS.DatatypeProperty,
                          OWL_NS.ObjectProperty,
                          OWL_NS.AnnotationProperty])):
        if o in [OWL_NS.SymmetricProperty,
                 OWL_NS.InverseFunctionalProperty,
                 OWL_NS.TransitiveProperty,
                 OWL_NS.ObjectProperty]:
            bType = OWL_NS.ObjectProperty
        else:
            bType = OWL_NS.DatatypeProperty
        if s not in prevProps:
            prevProps.add(s)
            yield Property(s,
                           graph=graph,
                           baseType=bType)


class ClassNamespaceFactory(Namespace):
    def term(self, name):
        return Class(URIRef(self + name))

    def __getitem__(self, key, default=None):
        return self.term(key)

    def __getattr__(self, name):
        if name.startswith("__"):  # ignore any special Python names!
            raise AttributeError
        else:
            return self.term(name)

CLASS_RELATIONS = set(
    OWL_NS.resourceProperties
).difference([OWL_NS.onProperty,
              OWL_NS.allValuesFrom,
              OWL_NS.hasValue,
              OWL_NS.someValuesFrom,
              OWL_NS.inverseOf,
              OWL_NS.imports,
              OWL_NS.versionInfo,
              OWL_NS.backwardCompatibleWith,
              OWL_NS.incompatibleWith,
              OWL_NS.unionOf,
              OWL_NS.intersectionOf,
              OWL_NS.oneOf])


def ComponentTerms(cls):
    """
    Takes a Class instance and returns a generator over the classes that
    are involved in its definition, ignoring unamed classes
    """
    if OWL_NS.Restriction in cls.type:
        try:
            cls = CastClass(cls, Individual.factoryGraph)
            for s, p, innerClsId in cls.factoryGraph.triples_choices(
                (cls.identifier,
                 [OWL_NS.allValuesFrom,
                  OWL_NS.someValuesFrom],
                 None)):
                innerCls = Class(innerClsId, skipOWLClassMembership=True)
                if isinstance(innerClsId, BNode):
                    for _c in ComponentTerms(innerCls):
                        yield _c
                else:
                    yield innerCls
        except:
            pass
    else:
        cls = CastClass(cls, Individual.factoryGraph)
        if isinstance(cls, BooleanClass):
            for _cls in cls:
                _cls = Class(_cls, skipOWLClassMembership=True)
                if isinstance(_cls.identifier, BNode):
                    for _c in ComponentTerms(_cls):
                        yield _c
                else:
                    yield _cls
        else:
            for innerCls in cls.subClassOf:
                if isinstance(innerCls.identifier, BNode):
                    for _c in ComponentTerms(innerCls):
                        yield _c
                else:
                    yield innerCls
            for s, p, o in cls.factoryGraph.triples_choices(
                (classOrIdentifier(cls),
                 CLASS_RELATIONS,
                 None)
            ):
                if isinstance(o, BNode):
                    for _c in ComponentTerms(
                            CastClass(o, Individual.factoryGraph)):
                        yield _c
                else:
                    yield innerCls


def DeepClassClear(classToPrune):
    """
    Recursively clear the given class, continuing
    where any related class is an anonymous class

    >>> EX = Namespace('http://example.com/')
    >>> namespace_manager = NamespaceManager(Graph())
    >>> namespace_manager.bind('ex', EX, override=False)
    >>> namespace_manager.bind('owl', OWL_NS, override=False)
    >>> g = Graph()
    >>> g.namespace_manager = namespace_manager
    >>> Individual.factoryGraph = g
    >>> classB = Class(EX.B)
    >>> classC = Class(EX.C)
    >>> classD = Class(EX.D)
    >>> classE = Class(EX.E)
    >>> classF = Class(EX.F)
    >>> anonClass = EX.someProp | some | classD #doctest: +SKIP
    >>> classF += anonClass #doctest: +SKIP
    >>> list(anonClass.subClassOf) #doctest: +SKIP
    [Class: ex:F ]
    >>> classA = classE | classF | anonClass #doctest: +SKIP
    >>> classB += classA #doctest: +SKIP
    >>> classA.equivalentClass = [Class()] #doctest: +SKIP
    >>> classB.subClassOf = [EX.someProp | some | classC] #doctest: +SKIP
    >>> classA #doctest: +SKIP
    ( ex:E OR ex:F OR ( ex:someProp SOME ex:D ) )
    >>> DeepClassClear(classA) #doctest: +SKIP
    >>> classA #doctest: +SKIP
    (  )
    >>> list(anonClass.subClassOf) #doctest: +SKIP
    []
    >>> classB #doctest: +SKIP
    Class: ex:B SubClassOf: ( ex:someProp SOME ex:C )

    >>> otherClass = classD | anonClass #doctest: +SKIP
    >>> otherClass #doctest: +SKIP
    ( ex:D OR ( ex:someProp SOME ex:D ) )
    >>> DeepClassClear(otherClass) #doctest: +SKIP
    >>> otherClass #doctest: +SKIP
    (  )
    >>> otherClass.delete() #doctest: +SKIP
    >>> list(g.triples((otherClass.identifier, None, None))) #doctest: +SKIP
    []
    """
    def deepClearIfBNode(_class):
        if isinstance(classOrIdentifier(_class), BNode):
            DeepClassClear(_class)
    classToPrune = CastClass(classToPrune, Individual.factoryGraph)
    for c in classToPrune.subClassOf:
        deepClearIfBNode(c)
    classToPrune.graph.remove((classToPrune.identifier, RDFS.subClassOf, None))
    for c in classToPrune.equivalentClass:
        deepClearIfBNode(c)
    classToPrune.graph.remove(
        (classToPrune.identifier, OWL_NS.equivalentClass, None))
    inverseClass = classToPrune.complementOf
    if inverseClass:
        classToPrune.graph.remove(
            (classToPrune.identifier, OWL_NS.complementOf, None))
        deepClearIfBNode(inverseClass)
    if isinstance(classToPrune, BooleanClass):
        for c in classToPrune:
            deepClearIfBNode(c)
        classToPrune.clear()
        classToPrune.graph.remove((classToPrune.identifier,
                                   classToPrune._operator,
                                   None))


class MalformedClass(Exception):
    def __init__(self, msg):
        self.msg = msg

    def __repr__(self):
        return self.msg


def CastClass(c, graph=None):
    graph = graph is None and c.factoryGraph or graph
    for kind in graph.objects(subject=classOrIdentifier(c),
                              predicate=RDF.type):
        if kind == OWL_NS.Restriction:
            kwArgs = {'identifier': classOrIdentifier(c),
                      'graph': graph}
            for s, p, o in graph.triples((classOrIdentifier(c),
                                          None,
                                          None)):
                if p != RDF.type:
                    if p == OWL_NS.onProperty:
                        kwArgs['onProperty'] = o
                    else:
                        if p not in Restriction.restrictionKinds:
                            continue
                        kwArgs[str(p.split(OWL_NS)[-1])] = o
            if not set([str(i.split(OWL_NS)[-1])
                        for i in Restriction.restrictionKinds]
                       ).intersection(kwArgs):
                raise MalformedClass("Malformed owl:Restriction")
            return Restriction(**kwArgs)
        else:
            for s, p, o in graph.triples_choices((classOrIdentifier(c),
                                                  [OWL_NS.intersectionOf,
                                                 OWL_NS.unionOf,
                                                 OWL_NS.oneOf],
                                                  None)):
                if p == OWL_NS.oneOf:
                    return EnumeratedClass(classOrIdentifier(c), graph=graph)
                else:
                    return BooleanClass(
                        classOrIdentifier(c), operator=p, graph=graph)
            # assert (classOrIdentifier(c),RDF.type,OWL_NS.Class) in graph
            return Class(
                classOrIdentifier(c), graph=graph, skipOWLClassMembership=True)


class Class(AnnotatableTerms):
    """
    'General form' for classes:

    The Manchester Syntax (supported in Protege) is used as the basis for the
    form of this class

    See: http://owl-workshop.man.ac.uk/acceptedLong/submission_9.pdf:

    [Annotation]
    ‘Class:’ classID {Annotation
                        ( (‘SubClassOf:’ ClassExpression)
                        | (‘EquivalentTo’ ClassExpression)
                        | (’DisjointWith’ ClassExpression)) }

    Appropriate excerpts from OWL Reference:

    ".. Subclass axioms provide us with partial definitions: they represent
     necessary but not sufficient conditions for establishing class
     membership of an individual."

    ".. A class axiom may contain (multiple) owl:equivalentClass statements"

    "..A class axiom may also contain (multiple) owl:disjointWith statements.."

    "..An owl:complementOf property links a class to precisely one class
      description."

    """
    def _serialize(self, graph):
        for cl in self.subClassOf:
            CastClass(cl, self.graph).serialize(graph)
        for cl in self.equivalentClass:
            CastClass(cl, self.graph).serialize(graph)
        for cl in self.disjointWith:
            CastClass(cl, self.graph).serialize(graph)
        if self.complementOf:
            CastClass(self.complementOf, self.graph).serialize(graph)

    def serialize(self, graph):
        for fact in self.graph.triples((self.identifier, None, None)):
            graph.add(fact)
        self._serialize(graph)

    def setupNounAnnotations(self, nounAnnotations):
        if isinstance(nounAnnotations, tuple):
            CN_sgProp, CN_plProp = nounAnnotations
        else:
            CN_sgProp = nounAnnotations
            CN_plProp = nounAnnotations

        if CN_sgProp:
            self.CN_sgProp.extent = [(self.identifier,
                                      self.handleAnnotation(CN_sgProp))]
        if CN_plProp:
            self.CN_plProp.extent = [(self.identifier,
                                      self.handleAnnotation(CN_plProp))]

    def __init__(self, identifier=None, subClassOf=None, equivalentClass=None,
                 disjointWith=None, complementOf=None, graph=None,
                 skipOWLClassMembership=False, comment=None,
                 nounAnnotations=None,
                 nameAnnotation=None,
                 nameIsLabel=False):
        super(Class, self).__init__(identifier, graph,
                                    nameAnnotation, nameIsLabel)

        if nounAnnotations:
            self.setupNounAnnotations(nounAnnotations)
        if not skipOWLClassMembership \
                and (self.identifier, RDF.type, OWL_NS.Class) \
                not in self.graph and \
                (self.identifier, RDF.type, OWL_NS.Restriction) \
                not in self.graph:
            self.graph.add((self.identifier, RDF.type, OWL_NS.Class))

        self.subClassOf = subClassOf and subClassOf or []
        self.equivalentClass = equivalentClass and equivalentClass or []
        self.disjointWith = disjointWith and disjointWith or []
        if complementOf:
            self.complementOf = complementOf
        self.comment = comment and comment or []

    def _get_extent(self, graph=None):
        for member in (
            graph is None and self.graph or graph).subjects(
                predicate=RDF.type, object=self.identifier):
            yield member

    def _set_extent(self, other):
        if not other:
            return
        for m in other:
            self.graph.add((classOrIdentifier(m), RDF.type, self.identifier))

    @TermDeletionHelper(RDF.type)
    def _del_type(self):
        pass

    extent = property(_get_extent, _set_extent, _del_type)

    def _get_annotation(self, term=RDFS.label):
        for annotation in self.graph.objects(subject=self, predicate=term):
            yield annotation

    annotation = property(_get_annotation, lambda x: x)

    def _get_extentQuery(self):
        return (Variable('CLASS'), RDF.type, self.identifier)

    def _set_extentQuery(self, other):
        pass

    extentQuery = property(_get_extentQuery, _set_extentQuery)

    def __hash__(self):
        """
        >>> b=Class(OWL_NS.Restriction)
        >>> c=Class(OWL_NS.Restriction)
        >>> len(set([b,c]))
        1
        """
        return hash(self.identifier)

    def __eq__(self, other):
        assert isinstance(other, Class), repr(other)
        return self.identifier == other.identifier

    def __iadd__(self, other):
        assert isinstance(other, Class)
        other.subClassOf = [self]
        return self

    def __isub__(self, other):
        assert isinstance(other, Class)
        self.graph.remove(
            (classOrIdentifier(other), RDFS.subClassOf, self.identifier))
        return self

    def __invert__(self):
        """
        Shorthand for Manchester syntax's not operator
        """
        return Class(complementOf=self)

    def __or__(self, other):
        """
        Construct an anonymous class description consisting of the union of
        this class and 'other' and return it
        """
        return BooleanClass(
            operator=OWL_NS.unionOf, members=[self, other], graph=self.graph)

    def __and__(self, other):
        """
        Construct an anonymous class description consisting of the
        intersection of this class and 'other' and return it

        >>> exNs = Namespace('http://example.com/')
        >>> namespace_manager = NamespaceManager(Graph())
        >>> namespace_manager.bind('ex', exNs, override=False)
        >>> namespace_manager.bind('owl', OWL_NS, override=False)
        >>> g = Graph()
        >>> g.namespace_manager = namespace_manager

        Chaining 3 intersections

        >>> female = Class(exNs.Female, graph=g)
        >>> human = Class(exNs.Human, graph=g)
        >>> youngPerson = Class(exNs.YoungPerson, graph=g)
        >>> youngWoman = female & human & youngPerson
        >>> youngWoman #doctest: +SKIP
        ex:YoungPerson THAT ( ex:Female AND ex:Human )
        >>> isinstance(youngWoman, BooleanClass)
        True
        >>> isinstance(youngWoman.identifier, BNode)
        True
        """
        return BooleanClass(
            operator=OWL_NS.intersectionOf,
            members=[self, other], graph=self.graph)

    def _get_subClassOf(self):
        for anc in self.graph.objects(
                subject=self.identifier, predicate=RDFS.subClassOf):
            yield Class(anc,
                        graph=self.graph,
                        skipOWLClassMembership=True)

    def _set_subClassOf(self, other):
        if not other:
            return
        for sc in other:
            self.graph.add(
                (self.identifier, RDFS.subClassOf, classOrIdentifier(sc)))

    @TermDeletionHelper(RDFS.subClassOf)
    def _del_subClassOf(self):
        pass

    subClassOf = property(_get_subClassOf, _set_subClassOf, _del_subClassOf)

    def _get_equivalentClass(self):
        for ec in self.graph.objects(
                subject=self.identifier, predicate=OWL_NS.equivalentClass):
            yield Class(ec, graph=self.graph)

    def _set_equivalentClass(self, other):
        if not other:
            return
        for sc in other:
            self.graph.add((self.identifier,
                           OWL_NS.equivalentClass, classOrIdentifier(sc)))

    @TermDeletionHelper(OWL_NS.equivalentClass)
    def _del_equivalentClass(self):
        pass

    equivalentClass = property(
        _get_equivalentClass, _set_equivalentClass, _del_equivalentClass)

    def _get_disjointWith(self):
        for dc in self.graph.objects(
                subject=self.identifier, predicate=OWL_NS.disjointWith):
            yield Class(dc, graph=self.graph)

    def _set_disjointWith(self, other):
        if not other:
            return
        for c in other:
            self.graph.add(
                (self.identifier, OWL_NS.disjointWith, classOrIdentifier(c)))

    @TermDeletionHelper(OWL_NS.disjointWith)
    def _del_disjointWith(self):
        pass

    disjointWith = property(
        _get_disjointWith, _set_disjointWith, _del_disjointWith)

    def _get_complementOf(self):
        comp = list(self.graph.objects(
            subject=self.identifier, predicate=OWL_NS.complementOf))
        if not comp:
            return None
        elif len(comp) == 1:
            return Class(comp[0], graph=self.graph)
        else:
            raise Exception(len(comp))

    def _set_complementOf(self, other):
        if not other:
            return
        self.graph.add(
            (self.identifier, OWL_NS.complementOf, classOrIdentifier(other)))

    @TermDeletionHelper(OWL_NS.complementOf)
    def _del_complementOf(self):
        pass

    complementOf = property(
        _get_complementOf, _set_complementOf, _del_complementOf)

    def _get_parents(self):
        """
        computed attributes that returns a generator over taxonomic 'parents'
        by disjunction, conjunction, and subsumption

        >>> from rdflib.util import first
        >>> exNs = Namespace('http://example.com/')
        >>> namespace_manager = NamespaceManager(Graph())
        >>> namespace_manager.bind('ex', exNs, override=False)
        >>> namespace_manager.bind('owl', OWL_NS, override=False)
        >>> g = Graph()
        >>> g.namespace_manager = namespace_manager
        >>> Individual.factoryGraph = g
        >>> brother = Class(exNs.Brother)
        >>> sister = Class(exNs.Sister)
        >>> sibling = brother | sister
        >>> sibling.identifier = exNs.Sibling
        >>> sibling #doctest: +SKIP
        ( ex:Brother OR ex:Sister )
        >>> first(brother.parents) #doctest: +SKIP
        Class: ex:Sibling EquivalentTo: ( ex:Brother OR ex:Sister )
        >>> parent = Class(exNs.Parent)
        >>> male = Class(exNs.Male)
        >>> father = parent & male
        >>> father.identifier = exNs.Father
        >>> list(father.parents) #doctest: +SKIP
        [Class: ex:Parent , Class: ex:Male ]

        """
        for parent in itertools.chain(self.subClassOf,
                                      self.equivalentClass):
            yield parent

        link = first(self.factoryGraph.subjects(RDF.first, self.identifier))
        if link:
            listSiblings = list(self.factoryGraph.transitive_subjects(RDF.rest,
                                                                      link))
            if listSiblings:
                collectionHead = listSiblings[-1]
            else:
                collectionHead = link
            for disjCls in self.factoryGraph.subjects(
                    OWL_NS.unionOf, collectionHead):
                if isinstance(disjCls, URIRef):
                    yield Class(disjCls, skipOWLClassMembership=True)
        for rdfList in self.factoryGraph.objects(
                self.identifier, OWL_NS.intersectionOf):
            for member in OWLRDFListProxy([rdfList], graph=self.factoryGraph):
                if isinstance(member, URIRef):
                    yield Class(member, skipOWLClassMembership=True)

    parents = property(_get_parents)

    def isPrimitive(self):
        if (self.identifier, RDF.type, OWL_NS.Restriction) in self.graph:
            return False
        # sc = list(self.subClassOf)
        ec = list(self.equivalentClass)
        for boolClass, p, rdfList in self.graph.triples_choices(
            (self.identifier,
             [OWL_NS.intersectionOf,
              OWL_NS.unionOf],
             None)):
            ec.append(manchesterSyntax(rdfList, self.graph, boolean=p))
        for e in ec:
            return False
        if self.complementOf:
            return False
        return True

    def subSumpteeIds(self):
        for s in self.graph.subjects(
                predicate=RDFS.subClassOf, object=self.identifier):
            yield s

    # def __iter__(self):
    #     for s in self.graph.subjects(
    #        predicate=RDFS.subClassOf,object=self.identifier):
    #         yield Class(s,skipOWLClassMembership=True)

    def __repr__(self, full=False, normalization=True):
        """
        Returns the Manchester Syntax equivalent for this class
        """
        exprs = []
        sc = list(self.subClassOf)
        ec = list(self.equivalentClass)
        for boolClass, p, rdfList in self.graph.triples_choices(
            (self.identifier,
             [OWL_NS.intersectionOf,
              OWL_NS.unionOf],
             None)):
            ec.append(manchesterSyntax(rdfList, self.graph, boolean=p))
        dc = list(self.disjointWith)
        c = self.complementOf
        if c:
            dc.append(c)
        klassKind = ''
        label = list(self.graph.objects(self.identifier, RDFS.label))
        label = label and '(' + label[0] + ')' or ''
        if sc:
            if full:
                scJoin = '\n                '
            else:
                scJoin = ', '
            necStatements = [
                isinstance(s, Class) and isinstance(self.identifier, BNode) and
                repr(CastClass(s, self.graph)) or
                # repr(BooleanClass(classOrIdentifier(s),
                #                  operator=None,
                #                  graph=self.graph)) or
                manchesterSyntax(classOrIdentifier(s), self.graph) for s in sc]
            if necStatements:
                klassKind = "Primitive Type %s" % label
            exprs.append("SubClassOf: %s" % scJoin.join(
                [str(n) for n in necStatements]))
            if full:
                exprs[-1] = "\n    " + exprs[-1]
        if ec:
            nec_SuffStatements = [
                isinstance(s, str) and s or
                manchesterSyntax(classOrIdentifier(s), self.graph) for s in ec]
            if nec_SuffStatements:
                klassKind = "A Defined Class %s" % label
            exprs.append("EquivalentTo: %s" % ', '.join(nec_SuffStatements))
            if full:
                exprs[-1] = "\n    " + exprs[-1]
        if dc:
            exprs.append("DisjointWith %s\n" % '\n                 '.join(
                [manchesterSyntax(classOrIdentifier(s), self.graph)
                    for s in dc]))
            if full:
                exprs[-1] = "\n    " + exprs[-1]
        descr = list(self.graph.objects(self.identifier, RDFS.comment))
        if full and normalization:
            klassDescr = klassKind and '\n    ## %s ##' % klassKind +\
                (descr and "\n    %s" % descr[0] or '') + \
                ' . '.join(exprs) or ' . '.join(exprs)
        else:
            klassDescr = full and (descr and "\n    %s" %
                                   descr[0] or '') or '' + ' . '.join(exprs)
        return (isinstance(self.identifier, BNode)
                and "Some Class "
                or "Class: %s " % self.qname) + klassDescr


class OWLRDFListProxy(object):
    def __init__(self, rdfList, members=None, graph=None):
        if graph:
            self.graph = graph
        members = members and members or []
        if rdfList:
            self._rdfList = Collection(self.graph, rdfList[0])
            for member in members:
                if member not in self._rdfList:
                    self._rdfList.append(classOrIdentifier(member))
        else:
            self._rdfList = Collection(self.graph, BNode(),
                                       [classOrIdentifier(m) for m in members])
            self.graph.add(
                (self.identifier, self._operator, self._rdfList.uri))

    def __eq__(self, other):
        """
        Equivalence of boolean class constructors is determined by
        equivalence of its members
        """
        assert isinstance(other, Class), repr(other) + repr(type(other))
        if isinstance(other, BooleanClass):
            length = len(self)
            if length != len(other):
                return False
            else:
                for idx in range(length):
                    if self[idx] != other[idx]:
                        return False
                    return True
        else:
            return self.identifier == other.identifier

    # Redirect python list accessors to the underlying Collection instance
    def __len__(self):
        return len(self._rdfList)

    def index(self, item):
        return self._rdfList.index(classOrIdentifier(item))

    def __getitem__(self, key):
        return self._rdfList[key]

    def __setitem__(self, key, value):
        self._rdfList[key] = classOrIdentifier(value)

    def __delitem__(self, key):
        del self._rdfList[key]

    def clear(self):
        self._rdfList.clear()

    def __iter__(self):
        for item in self._rdfList:
            yield item

    def __contains__(self, item):
        for i in self._rdfList:
            if i == classOrIdentifier(item):
                return 1
        return 0

    def append(self, item):
        self._rdfList.append(item)

    def __iadd__(self, other):
        self._rdfList.append(classOrIdentifier(other))
        return self


class EnumeratedClass(OWLRDFListProxy, Class):
    py3compat.format_doctest_out("""
    Class for owl:oneOf forms:

    OWL Abstract Syntax is used

    axiom ::= 'EnumeratedClass('
        classID ['Deprecated'] { annotation } { individualID } ')'


    >>> exNs = Namespace('http://example.com/')
    >>> namespace_manager = NamespaceManager(Graph())
    >>> namespace_manager.bind('ex', exNs, override=False)
    >>> namespace_manager.bind('owl', OWL_NS, override=False)
    >>> g = Graph()
    >>> g.namespace_manager = namespace_manager
    >>> Individual.factoryGraph = g
    >>> ogbujiBros = EnumeratedClass(exNs.ogbujicBros,
    ...                              members=[exNs.chime,
    ...                                       exNs.uche,
    ...                                       exNs.ejike])
    >>> ogbujiBros #doctest: +SKIP
    { ex:chime ex:uche ex:ejike }
    >>> col = Collection(g, first(
    ...    g.objects(predicate=OWL_NS.oneOf, subject=ogbujiBros.identifier)))
    >>> [g.qname(item) for item in col]
    [%(u)s'ex:chime', %(u)s'ex:uche', %(u)s'ex:ejike']
    >>> print(g.serialize(format='n3')) #doctest: +SKIP
    @prefix ex: <http://example.com/> .
    @prefix owl: <http://www.w3.org/2002/07/owl#> .
    @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
    <BLANKLINE>
    ex:ogbujicBros a owl:Class;
        owl:oneOf ( ex:chime ex:uche ex:ejike ) .
    <BLANKLINE>
    <BLANKLINE>
    """)
    _operator = OWL_NS.oneOf

    def isPrimitive(self):
        return False

    def __init__(self, identifier=None, members=None, graph=None):
        Class.__init__(self, identifier, graph=graph)
        members = members and members or []
        rdfList = list(self.graph.objects(
            predicate=OWL_NS.oneOf, subject=self.identifier))
        OWLRDFListProxy.__init__(self, rdfList, members)

    def __repr__(self):
        """
        Returns the Manchester Syntax equivalent for this class
        """
        return manchesterSyntax(
            self._rdfList.uri, self.graph, boolean=self._operator)

    def serialize(self, graph):
        clonedList = Collection(graph, BNode())
        for cl in self._rdfList:
            clonedList.append(cl)
            CastClass(cl, self.graph).serialize(graph)

        graph.add((self.identifier, self._operator, clonedList.uri))
        for s, p, o in self.graph.triples((self.identifier, None, None)):
            if p != self._operator:
                graph.add((s, p, o))
        self._serialize(graph)

BooleanPredicates = [OWL_NS.intersectionOf, OWL_NS.unionOf]


class BooleanClassExtentHelper:
    """
    >>> testGraph = Graph()
    >>> Individual.factoryGraph = testGraph
    >>> EX = Namespace("http://example.com/")
    >>> namespace_manager = NamespaceManager(Graph())
    >>> namespace_manager.bind('ex', EX, override=False)
    >>> testGraph.namespace_manager = namespace_manager
    >>> fire = Class(EX.Fire)
    >>> water = Class(EX.Water)
    >>> testClass = BooleanClass(members=[fire, water])
    >>> testClass2 = BooleanClass(
    ...     operator=OWL_NS.unionOf, members=[fire, water])
    >>> for c in BooleanClass.getIntersections():
    ...     print(c) #doctest: +SKIP
    ( ex:Fire AND ex:Water )
    >>> for c in BooleanClass.getUnions():
    ...     print(c) #doctest: +SKIP
    ( ex:Fire OR ex:Water )
    """
    def __init__(self, operator):
        self.operator = operator

    def __call__(self, f):
        def _getExtent():
            for c in Individual.factoryGraph.subjects(self.operator):
                yield BooleanClass(c, operator=self.operator)
        return _getExtent


class Callable():
    def __init__(self, anycallable):
        self.__call__ = anycallable


class BooleanClass(OWLRDFListProxy, Class):
    """
    See: http://www.w3.org/TR/owl-ref/#Boolean

    owl:complementOf is an attribute of Class, however

    """
    @BooleanClassExtentHelper(OWL_NS.intersectionOf)
    @Callable
    def getIntersections():
        pass
    getIntersections = Callable(getIntersections)

    @BooleanClassExtentHelper(OWL_NS.unionOf)
    @Callable
    def getUnions():
        pass
    getUnions = Callable(getUnions)

    def __init__(self, identifier=None, operator=OWL_NS.intersectionOf,
                 members=None, graph=None):
        if operator is None:
            props = []
            for s, p, o in graph.triples_choices((identifier,
                                                  [OWL_NS.intersectionOf,
                                                 OWL_NS.unionOf],
                                                 None)):
                props.append(p)
                operator = p
            assert len(props) == 1, repr(props)
        Class.__init__(self, identifier, graph=graph)
        assert operator in [OWL_NS.intersectionOf,
                            OWL_NS.unionOf], str(operator)
        self._operator = operator
        rdfList = list(
            self.graph.objects(predicate=operator, subject=self.identifier))
        assert not members or not rdfList, \
            "This is a previous boolean class description!" + \
            repr(Collection(self.graph, rdfList[0]).n3())
        OWLRDFListProxy.__init__(self, rdfList, members)

    def copy(self):
        """
        Create a copy of this class
        """
        copyOfClass = BooleanClass(
            operator=self._operator, members=list(self), graph=self.graph)
        return copyOfClass

    def serialize(self, graph):
        clonedList = Collection(graph, BNode())
        for cl in self._rdfList:
            clonedList.append(cl)
            CastClass(cl, self.graph).serialize(graph)

        graph.add((self.identifier, self._operator, clonedList.uri))

        for s, p, o in self.graph.triples((self.identifier, None, None)):
            if p != self._operator:
                graph.add((s, p, o))
        self._serialize(graph)

    def isPrimitive(self):
        return False

    def changeOperator(self, newOperator):
        """
        Converts a unionOf / intersectionOf class expression into one
        that instead uses the given operator


        >>> testGraph = Graph()
        >>> Individual.factoryGraph = testGraph
        >>> EX = Namespace("http://example.com/")
        >>> namespace_manager = NamespaceManager(Graph())
        >>> namespace_manager.bind('ex', EX, override=False)
        >>> testGraph.namespace_manager = namespace_manager
        >>> fire = Class(EX.Fire)
        >>> water = Class(EX.Water)
        >>> testClass = BooleanClass(members=[fire,water])
        >>> testClass #doctest: +SKIP
        ( ex:Fire AND ex:Water )
        >>> testClass.changeOperator(OWL_NS.unionOf)
        >>> testClass #doctest: +SKIP
        ( ex:Fire OR ex:Water )
        >>> try: testClass.changeOperator(OWL_NS.unionOf)
        ... except Exception%s: print(e)
        The new operator is already being used!

        """ % 'as e' if py3compat.PY3 else ', e'
        assert newOperator != self._operator, \
            "The new operator is already being used!"
        self.graph.remove((self.identifier, self._operator, self._rdfList.uri))
        self.graph.add((self.identifier, newOperator, self._rdfList.uri))
        self._operator = newOperator

    def __repr__(self):
        """
        Returns the Manchester Syntax equivalent for this class
        """
        return manchesterSyntax(
            self._rdfList.uri, self.graph, boolean=self._operator)

    def __or__(self, other):
        """
        Adds other to the list and returns self
        """
        assert self._operator == OWL_NS.unionOf
        self._rdfList.append(classOrIdentifier(other))
        return self


def AllDifferent(members):
    """
    DisjointClasses(' description description { description } ')'

    """
    pass


class Restriction(Class):
    """
    restriction ::= 'restriction('
                            datavaluedPropertyID dataRestrictionComponent
                                 { dataRestrictionComponent } ')'
                  | 'restriction(' individualvaluedPropertyID
                      individualRestrictionComponent
                      { individualRestrictionComponent } ')'
    """

    restrictionKinds = [OWL_NS.allValuesFrom,
                        OWL_NS.someValuesFrom,
                        OWL_NS.hasValue,
                        OWL_NS.maxCardinality,
                        OWL_NS.minCardinality]

    def __init__(self,
                 onProperty,
                 graph=Graph(),
                 allValuesFrom=None,
                 someValuesFrom=None,
                 value=None,
                 cardinality=None,
                 maxCardinality=None,
                 minCardinality=None,
                 identifier=None):
        super(Restriction, self).__init__(identifier,
                                          graph=graph,
                                          skipOWLClassMembership=True)
        if (self.identifier,
            OWL_NS.onProperty,
                propertyOrIdentifier(onProperty)) not in graph:
            graph.add((self.identifier, OWL_NS.onProperty,
                      propertyOrIdentifier(onProperty)))
        self.onProperty = onProperty
        restrTypes = [
            (allValuesFrom, OWL_NS.allValuesFrom),
            (someValuesFrom, OWL_NS.someValuesFrom),
            (value, OWL_NS.hasValue),
            (cardinality, OWL_NS.cardinality),
            (maxCardinality, OWL_NS.maxCardinality),
            (minCardinality, OWL_NS.minCardinality)]
        validRestrProps = [(i, oTerm) for (i, oTerm) in restrTypes if i]
        assert len(validRestrProps)
        restrictionRange, restrictionType = validRestrProps.pop()
        self.restrictionType = restrictionType
        if isinstance(restrictionRange, Identifier):
            self.restrictionRange = restrictionRange
        elif isinstance(restrictionRange, Class):
            self.restrictionRange = classOrIdentifier(restrictionRange)
        else:
            self.restrictionRange = first(self.graph.objects(self.identifier,
                                                             restrictionType))
        if (self.identifier,
            restrictionType,
                self.restrictionRange) not in self.graph:
            self.graph.add(
                (self.identifier, restrictionType, self.restrictionRange))
        assert self.restrictionRange is not None, Class(self.identifier)
        if (self.identifier, RDF.type, OWL_NS.Restriction) not in self.graph:
            self.graph.add((self.identifier, RDF.type, OWL_NS.Restriction))
            self.graph.remove((self.identifier, RDF.type, OWL_NS.Class))

    @py3compat.format_doctest_out
    def serialize(self, graph):
        """
        >>> g1 = Graph()
        >>> g2 = Graph()
        >>> EX = Namespace("http://example.com/")
        >>> namespace_manager = NamespaceManager(g1)
        >>> namespace_manager.bind('ex', EX, override=False)
        >>> namespace_manager = NamespaceManager(g2)
        >>> namespace_manager.bind('ex', EX, override=False)
        >>> Individual.factoryGraph = g1
        >>> prop = Property(EX.someProp, baseType=OWL_NS.DatatypeProperty)
        >>> restr1 = (Property(
        ...    EX.someProp,
        ...    baseType=OWL_NS.DatatypeProperty)) | some | (Class(EX.Foo))
        >>> restr1 #doctest: +SKIP
        ( ex:someProp SOME ex:Foo )
        >>> restr1.serialize(g2)
        >>> Individual.factoryGraph = g2
        >>> list(Property(
        ...     EX.someProp,baseType=None).type
        ... ) #doctest: +NORMALIZE_WHITESPACE +SKIP
        [rdflib.term.URIRef(
            %(u)s'http://www.w3.org/2002/07/owl#DatatypeProperty')]
        """
        Property(
            self.onProperty, graph=self.graph, baseType=None).serialize(graph)
        for s, p, o in self.graph.triples((self.identifier, None, None)):
            graph.add((s, p, o))
            if p in [OWL_NS.allValuesFrom, OWL_NS.someValuesFrom]:
                CastClass(o, self.graph).serialize(graph)

    def isPrimitive(self):
        return False

    def __hash__(self):
        return hash((self.onProperty, self.restrictionRange))

    def __eq__(self, other):
        """
        Equivalence of restrictions is determined by equivalence of the
        property in question and the restriction 'range'
        """
        assert isinstance(other, Class), repr(other) + repr(type(other))
        if isinstance(other, Restriction):
            return other.onProperty == self.onProperty and \
                other.restrictionRange == self.restrictionRange
        else:
            return False

    def _get_onProperty(self):
        return list(self.graph.objects(
            subject=self.identifier, predicate=OWL_NS.onProperty))[0]

    def _set_onProperty(self, prop):
        triple = (
            self.identifier, OWL_NS.onProperty, propertyOrIdentifier(prop))
        if not prop:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)

    @TermDeletionHelper(OWL_NS.onProperty)
    def _del_onProperty(self):
        pass

    onProperty = property(_get_onProperty, _set_onProperty, _del_onProperty)

    def _get_allValuesFrom(self):
        for i in self.graph.objects(
                subject=self.identifier, predicate=OWL_NS.allValuesFrom):
            return Class(i, graph=self.graph)
        return None

    def _set_allValuesFrom(self, other):
        triple = (
            self.identifier, OWL_NS.allValuesFrom, classOrIdentifier(other))
        if not other:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)

    @TermDeletionHelper(OWL_NS.allValuesFrom)
    def _del_allValuesFrom(self):
        pass

    allValuesFrom = property(
        _get_allValuesFrom, _set_allValuesFrom, _del_allValuesFrom)

    def _get_someValuesFrom(self):
        for i in self.graph.objects(
                subject=self.identifier, predicate=OWL_NS.someValuesFrom):
            return Class(i, graph=self.graph)
        return None

    def _set_someValuesFrom(self, other):
        triple = (
            self.identifier, OWL_NS.someValuesFrom, classOrIdentifier(other))
        if not other:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)

    @TermDeletionHelper(OWL_NS.someValuesFrom)
    def _del_someValuesFrom(self):
        pass

    someValuesFrom = property(
        _get_someValuesFrom, _set_someValuesFrom, _del_someValuesFrom)

    def _get_hasValue(self):
        for i in self.graph.objects(
                subject=self.identifier, predicate=OWL_NS.hasValue):
            return Class(i, graph=self.graph)
        return None

    def _set_hasValue(self, other):
        triple = (self.identifier, OWL_NS.hasValue, classOrIdentifier(other))
        if not other:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)

    @TermDeletionHelper(OWL_NS.hasValue)
    def _del_hasValue(self):
        pass

    hasValue = property(_get_hasValue, _set_hasValue, _del_hasValue)

    def _get_cardinality(self):
        for i in self.graph.objects(
                subject=self.identifier, predicate=OWL_NS.cardinality):
            return Class(i, graph=self.graph)
        return None

    def _set_cardinality(self, other):
        triple = (
            self.identifier, OWL_NS.cardinality, classOrIdentifier(other))
        if not other:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)

    @TermDeletionHelper(OWL_NS.cardinality)
    def _del_cardinality(self):
        pass

    cardinality = property(
        _get_cardinality, _set_cardinality, _del_cardinality)

    def _get_maxCardinality(self):
        for i in self.graph.objects(
                subject=self.identifier, predicate=OWL_NS.maxCardinality):
            return Class(i, graph=self.graph)
        return None

    def _set_maxCardinality(self, other):
        triple = (
            self.identifier, OWL_NS.maxCardinality, classOrIdentifier(other))
        if not other:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)

    @TermDeletionHelper(OWL_NS.maxCardinality)
    def _del_maxCardinality(self):
        pass

    maxCardinality = property(
        _get_maxCardinality, _set_maxCardinality, _del_maxCardinality)

    def _get_minCardinality(self):
        for i in self.graph.objects(
                subject=self.identifier, predicate=OWL_NS.minCardinality):
            return Class(i, graph=self.graph)
        return None

    def _set_minCardinality(self, other):
        triple = (
            self.identifier, OWL_NS.minCardinality, classOrIdentifier(other))
        if not other:
            return
        elif triple in self.graph:
            return
        else:
            self.graph.set(triple)

    @TermDeletionHelper(OWL_NS.minCardinality)
    def _del_minCardinality(self):
        pass

    minCardinality = property(
        _get_minCardinality, _set_minCardinality, _del_minCardinality)

    def restrictionKind(self):
        for p in self.graph.triple_choices((self.identifier,
                                            self.restrictionKinds,
                                            None)):
            return p.split(OWL_NS)[-1]
        raise

    def __repr__(self):
        """
        Returns the Manchester Syntax equivalent for this restriction
        """
        return manchesterSyntax(self.identifier, self.graph)

### Infix Operators ###

some = Infix(lambda prop, _class: Restriction(prop, graph=_class.graph,
                                              someValuesFrom=_class))
only = Infix(lambda prop, _class: Restriction(prop, graph=_class.graph,
                                              allValuesFrom=_class))
max = Infix(lambda prop, _class: Restriction(prop, graph=prop.graph,
                                             maxCardinality=_class))
min = Infix(lambda prop, _class: Restriction(prop, graph=prop.graph,
                                             minCardinality=_class))
exactly = Infix(lambda prop, _class: Restriction(prop, graph=prop.graph,
                                                 cardinality=_class))
value = Infix(
    lambda prop, _class: Restriction(prop, graph=prop.graph, value=_class))

PropertyAbstractSyntax =\
    """
%s( %s { %s }
%s
{ 'super(' datavaluedPropertyID ')'} ['Functional']
{ domain( %s ) } { range( %s ) } )"""


class Property(AnnotatableTerms):
    """
    axiom ::= 'DatatypeProperty(' datavaluedPropertyID ['Deprecated']
                { annotation }
                { 'super(' datavaluedPropertyID ')'} ['Functional']
                { 'domain(' description ')' } { 'range(' dataRange ')' } ')'
            | 'ObjectProperty(' individualvaluedPropertyID ['Deprecated']
                { annotation }
                { 'super(' individualvaluedPropertyID ')' }
                [ 'inverseOf(' individualvaluedPropertyID ')' ] [ 'Symmetric' ]
                [ 'Functional' | 'InverseFunctional' |
                  'Functional' 'InverseFunctional' |
                  'Transitive' ]
                { 'domain(' description ')' } { 'range(' description ')' } ')
    """

    def setupVerbAnnotations(self, verbAnnotations):
        if isinstance(verbAnnotations, tuple):
            TV_sgProp, TV_plProp, TV_vbg = verbAnnotations
        else:
            TV_sgProp = verbAnnotations
            TV_plProp = verbAnnotations
            TV_vbg = verbAnnotations
        if TV_sgProp:
            self.TV_sgProp.extent = [(self.identifier,
                                      self.handleAnnotation(TV_sgProp))]
        if TV_plProp:
            self.TV_plProp.extent = [(self.identifier,
                                      self.handleAnnotation(TV_plProp))]
        if TV_vbg:
            self.TV_vbgProp.extent = [(self.identifier,
                                       self.handleAnnotation(TV_vbg))]

    def __init__(
        self, identifier=None, graph=None, baseType=OWL_NS.ObjectProperty,
        subPropertyOf=None, domain=None, range=None, inverseOf=None,
        otherType=None, equivalentProperty=None,
        comment=None,
        verbAnnotations=None,
        nameAnnotation=None,
            nameIsLabel=False):
        super(Property, self).__init__(identifier, graph,
                                       nameAnnotation, nameIsLabel)
        if verbAnnotations:
            self.setupVerbAnnotations(verbAnnotations)

        assert not isinstance(self.identifier, BNode)
        if baseType is None:
            # None give, determine via introspection
            self._baseType = first(
                Individual(self.identifier, graph=self.graph).type)
        else:
            if (self.identifier, RDF.type, baseType) not in self.graph:
                self.graph.add((self.identifier, RDF.type, baseType))
            self._baseType = baseType
        self.subPropertyOf = subPropertyOf
        self.inverseOf = inverseOf
        self.domain = domain
        self.range = range
        self.comment = comment and comment or []

    def serialize(self, graph):
        for fact in self.graph.triples((self.identifier, None, None)):
            graph.add(fact)
        for p in itertools.chain(self.subPropertyOf,
                                 self.inverseOf):
            p.serialize(graph)
        for c in itertools.chain(self.domain,
                                 self.range):
            CastClass(c, self.graph).serialize(graph)

    def _get_extent(self, graph=None):
        for triple in (graph is None and self.graph or graph).triples(
                (None, self.identifier, None)):
            yield triple

    def _set_extent(self, other):
        if not other:
            return
        for subj, obj in other:
            self.graph.add((subj, self.identifier, obj))

    extent = property(_get_extent, _set_extent)

    def __repr__(self):
        rt = []
        if OWL_NS.ObjectProperty in self.type:
            rt.append('ObjectProperty( %s annotation(%s)'
                      % (self.qname, first(self.comment)
                          and first(self.comment) or ''))
            if first(self.inverseOf):
                twoLinkInverse = first(first(self.inverseOf).inverseOf)
                if twoLinkInverse \
                        and twoLinkInverse.identifier == self.identifier:
                    inverseRepr = first(self.inverseOf).qname
                else:
                    inverseRepr = repr(first(self.inverseOf))
                rt.append("  inverseOf( %s )%s" % (
                    inverseRepr,
                    OWL_NS.SymmetricProperty in self.type
                    and ' Symmetric'
                    or ''))
            for s, p, roleType in self.graph.triples_choices(
                (self.identifier,
                 RDF.type,
                 [OWL_NS.FunctionalProperty,
                  OWL_NS.InverseFunctionalProperty,
                  OWL_NS.TransitiveProperty])):
                rt.append(str(roleType.split(OWL_NS)[-1]))
        else:
            rt.append('DatatypeProperty( %s %s'
                      % (self.qname, first(self.comment)
                         and first(self.comment)
                         or ''))
            for s, p, roleType in self.graph.triples((
                    self.identifier, RDF.type, OWL_NS.FunctionalProperty)):
                rt.append('   Functional')

        def canonicalName(term, g):
            normalizedName = classOrIdentifier(term)
            if isinstance(normalizedName, BNode):
                return term
            elif normalizedName.startswith(_XSD_NS):
                return str(term)
            elif first(g.triples_choices((
                                         normalizedName,
                                         [OWL_NS.unionOf,
                       OWL_NS.intersectionOf], None))):
                return repr(term)
            else:
                return str(term.qname)
        rt.append(' '.join(["   super( %s )" % canonicalName(
            superP, self.graph)
            for superP in self.subPropertyOf]))
        rt.append(' '.join(["   domain( %s )" % canonicalName(
            domain, self.graph)
            for domain in self.domain]))
        rt.append(' '.join(["   range( %s )" % canonicalName(
            range, self.graph)
            for range in self.range]))
        rt = '\n'.join([expr for expr in rt if expr])
        rt += '\n)'
        return str(rt).encode('utf-8')

    def _get_subPropertyOf(self):
        for anc in self.graph.objects(
                subject=self.identifier, predicate=RDFS.subPropertyOf):
            yield Property(anc, graph=self.graph, baseType=None)

    def _set_subPropertyOf(self, other):
        if not other:
            return
        for sP in other:
            self.graph.add(
                (self.identifier, RDFS.subPropertyOf, classOrIdentifier(sP)))

    @TermDeletionHelper(RDFS.subPropertyOf)
    def _del_subPropertyOf(self):
        pass

    subPropertyOf = property(
        _get_subPropertyOf, _set_subPropertyOf, _del_subPropertyOf)

    def _get_inverseOf(self):
        for anc in self.graph.objects(
                subject=self.identifier, predicate=OWL_NS.inverseOf):
            yield Property(anc, graph=self.graph, baseType=None)

    def _set_inverseOf(self, other):
        if not other:
            return
        self.graph.add(
            (self.identifier, OWL_NS.inverseOf, classOrIdentifier(other)))

    @TermDeletionHelper(OWL_NS.inverseOf)
    def _del_inverseOf(self):
        pass

    inverseOf = property(_get_inverseOf, _set_inverseOf, _del_inverseOf)

    def _get_domain(self):
        for dom in self.graph.objects(
                subject=self.identifier, predicate=RDFS.domain):
            yield Class(dom, graph=self.graph)

    def _set_domain(self, other):
        if not other:
            return
        if isinstance(other, (Individual, Identifier)):
            self.graph.add(
                (self.identifier, RDFS.domain, classOrIdentifier(other)))
        else:
            for dom in other:
                self.graph.add(
                    (self.identifier, RDFS.domain, classOrIdentifier(dom)))

    @TermDeletionHelper(RDFS.domain)
    def _del_domain(self):
        pass

    domain = property(_get_domain, _set_domain, _del_domain)

    def _get_range(self):
        for ran in self.graph.objects(
                subject=self.identifier, predicate=RDFS.range):
            yield Class(ran, graph=self.graph)

    def _set_range(self, ranges):
        if not ranges:
            return
        if isinstance(ranges, (Individual, Identifier)):
            self.graph.add(
                (self.identifier, RDFS.range, classOrIdentifier(ranges)))
        else:
            for range in ranges:
                self.graph.add(
                    (self.identifier, RDFS.range, classOrIdentifier(range)))

    @TermDeletionHelper(RDFS.range)
    def _del_range(self):
        pass

    range = property(_get_range, _set_range, _del_range)

    def replace(self, other):
        # extension = []
        for s, p, o in self.extent:
            self.graph.add((s, propertyOrIdentifier(other), o))
        self.graph.remove((None, self.identifier, None))


def CommonNSBindings(graph, additionalNS={}):
    """
    Takes a graph and binds the common namespaces (rdf,rdfs, & owl)
    """
    namespace_manager = NamespaceManager(graph)
    namespace_manager.bind('rdfs', RDFS)
    namespace_manager.bind('rdf', RDF)
    namespace_manager.bind('owl', OWL_NS)
    for prefix, uri in list(additionalNS.items()):
        namespace_manager.bind(prefix, uri, override=False)
    graph.namespace_manager = namespace_manager


def test():
    import doctest
    doctest.testmod()

if __name__ == '__main__':
    test()
