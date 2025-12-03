#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import standard python libraries
import collections
import copy
import glob
import logging
import os
import rdflib
import re
import sys
import threading
import typing


# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software
import software.SchemaTerms.sdoterm as sdoterm
import software.SchemaTerms.sdocollaborators as sdocollaborators
import software.SchemaTerms.localmarkdown as localmarkdown

import software.util.pretty_logger as pretty_logger

log = logging.getLogger(__name__)

DEFVOCABURI = "https://schema.org/"
VOCABURI = None
DATATYPEURI = None
ENUMERATIONURI = None
THINGURI = None

CORE = "core"
DEFTRIPLESFILESGLOB = ("data/*.ttl", "data/ext/*/*.ttl")
LOADEDDEFAULT = False


def bindNameSpaces(graph):
    # --- Standard / W3C / Dublin Core ---
    graph.bind("dc", "http://purl.org/dc/elements/1.1/")
    graph.bind("dcat", "http://www.w3.org/ns/dcat#")
    graph.bind("dct", "http://purl.org/dc/terms/")
    graph.bind("dctype", "http://purl.org/dc/dcmitype/")
    graph.bind("foaf", "http://xmlns.com/foaf/0.1/")
    graph.bind("owl", "http://www.w3.org/2002/07/owl#")
    graph.bind("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")
    graph.bind("rdfs", "http://www.w3.org/2000/01/rdf-schema#")
    graph.bind("skos", "http://www.w3.org/2004/02/skos/core#")
    graph.bind("void", "http://rdfs.org/ns/void#")

    # --- OMG Commons ---
    graph.bind("cmns-cls", "https://www.omg.org/spec/Commons/Classifiers/")
    graph.bind("cmns-col", "https://www.omg.org/spec/Commons/Collections/")
    graph.bind("cmns-dt", "https://www.omg.org/spec/Commons/DatesAndTimes/")
    graph.bind("cmns-ge", "https://www.omg.org/spec/Commons/GeopoliticalEntities/")
    graph.bind("cmns-id", "https://www.omg.org/spec/Commons/Identifiers/")
    graph.bind("cmns-loc", "https://www.omg.org/spec/Commons/Locations/")
    graph.bind("cmns-q", "https://www.omg.org/spec/Commons/Quantities/")
    graph.bind("cmns-txt", "https://www.omg.org/spec/Commons/Text/")

    # --- OMG LCC (ISO Codes) ---
    graph.bind(
        "lcc-3166-1", "https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/"
    )
    graph.bind(
        "lcc-4217", "https://www.omg.org/spec/LCC/Countries/ISO4217-CurrencyCodes/"
    )
    graph.bind(
        "lcc-lr", "https://www.omg.org/spec/LCC/Languages/LanguageRepresentation/"
    )

    # --- FIBO (Financial Industry Business Ontology) ---
    graph.bind(
        "fibo-be-corp-corp",
        "https://spec.edmcouncil.org/fibo/ontology/BE/Corporations/Corporations/",
    )
    graph.bind(
        "fibo-be-ge-ge",
        "https://spec.edmcouncil.org/fibo/ontology/BE/GovernmentEntities/GovernmentEntities/",
    )
    graph.bind(
        "fibo-be-le-cb",
        "https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/CorporateBodies/",
    )
    graph.bind(
        "fibo-be-le-lp",
        "https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/LegalPersons/",
    )
    graph.bind(
        "fibo-be-nfp-nfp",
        "https://spec.edmcouncil.org/fibo/ontology/BE/NotForProfitOrganizations/NotForProfitOrganizations/",
    )
    graph.bind(
        "fibo-be-oac-cctl",
        "https://spec.edmcouncil.org/fibo/ontology/BE/OwnershipAndControl/CorporateControl/",
    )
    graph.bind(
        "fibo-fbc-dae-dbt",
        "https://spec.edmcouncil.org/fibo/ontology/FBC/DebtAndEquities/Debt/",
    )
    graph.bind(
        "fibo-fbc-pas-fpas",
        "https://spec.edmcouncil.org/fibo/ontology/FBC/ProductsAndServices/FinancialProductsAndServices/",
    )
    graph.bind(
        "fibo-fnd-acc-cur",
        "https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/",
    )
    graph.bind(
        "fibo-fnd-agr-ctr",
        "https://spec.edmcouncil.org/fibo/ontology/FND/Agreements/Contracts/",
    )
    graph.bind(
        "fibo-fnd-arr-doc",
        "https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Documents/",
    )
    graph.bind(
        "fibo-fnd-arr-lif",
        "https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Lifecycles/",
    )
    graph.bind(
        "fibo-fnd-dt-oc",
        "https://spec.edmcouncil.org/fibo/ontology/FND/DatesAndTimes/Occurrences/",
    )
    graph.bind(
        "fibo-fnd-org-org",
        "https://spec.edmcouncil.org/fibo/ontology/FND/Organizations/Organizations/",
    )
    graph.bind(
        "fibo-fnd-pas-pas",
        "https://spec.edmcouncil.org/fibo/ontology/FND/ProductsAndServices/ProductsAndServices/",
    )
    graph.bind(
        "fibo-fnd-plc-adr",
        "https://spec.edmcouncil.org/fibo/ontology/FND/Places/Addresses/",
    )
    graph.bind(
        "fibo-fnd-plc-fac",
        "https://spec.edmcouncil.org/fibo/ontology/FND/Places/Facilities/",
    )
    graph.bind(
        "fibo-fnd-plc-loc",
        "https://spec.edmcouncil.org/fibo/ontology/FND/Places/Locations/",
    )
    graph.bind(
        "fibo-fnd-pty-pty",
        "https://spec.edmcouncil.org/fibo/ontology/FND/Parties/Parties/",
    )
    graph.bind(
        "fibo-fnd-rel-rel",
        "https://spec.edmcouncil.org/fibo/ontology/FND/Relations/Relations/",
    )
    graph.bind(
        "fibo-pay-ps-ps",
        "https://spec.edmcouncil.org/fibo/ontology/PAY/PaymentServices/PaymentServices/",
    )

    # --- Other External Vocabularies ---
    graph.bind("gleif-L1", "https://www.gleif.org/ontology/L1/")
    graph.bind("gs1", "https://ref.gs1.org/voc/")
    graph.bind(
        "lcc-cr", "https://www.omg.org/spec/LCC/Countries/CountryRepresentation/"
    )
    graph.bind("unece", "http://unece.org/vocab#")
    graph.bind("vcard", "http://www.w3.org/2006/vcard/ns#")
    graph.bind("bibo", "http://purl.org/ontology/bibo/")
    graph.bind("sarif", "http://sarif.info/")

    # --- Libraries and Health ---
    graph.bind("lrmoo", "http://iflastandards.info/ns/lrm/lrmoo/")
    graph.bind("snomed", "http://purl.bioontology.org/ontology/SNOMEDCT/")

    # --- European Legislation Identifier (ELI) ---
    graph.bind("eli", "http://data.europa.eu/eli/ontology#")

    # --- W3C Standard extensions ---
    graph.bind("prov", "http://www.w3.org/ns/prov#")
    graph.bind("hydra", "http://www.w3.org/ns/hydra/core#")

    # --- Music Ontology ---
    graph.bind("mo", "http://purl.org/ontology/mo/")


class _TermAccumulator:
    """Temporary holder to accumulate term information."""

    def __init__(self, term_id):
        self.id = term_id
        self.types = []
        self.sups = []
        self.label = None
        self.layer = None
        self.type = ""

    def appendRow(self, row):
        self.types.append(row.type)
        self.sups.append(row.sup)
        self.type = row.type
        self.label = row.label
        self.layer = layerFromUri(row.layer)


def _loadOneSourceGraph(file_path: str) -> rdflib.Graph:
    """Load the content of one source file."""
    name, extension = os.path.splitext(file_path)
    if extension == ".nt":
        file_format = "nt"
    elif extension == ".ttl":
        file_format = "turtle"
    else:
        raise NotImplementedError("Unsupported file format: %s" % extension)
    try:
        graph = rdflib.Graph()
        graph.parse(source=file_path, format=file_format)
        return graph
    except Exception as e:
        message = "Error parsing source file '%s': %s" % (file_path, e)
        log.warning(message)
        raise IOError(message)


class SdoTermSource:
    """This class acts as the source of information for terms.


    The class acts as a cache of terms keyed by id.
    Instances are kind of factory for terms.

    """

    TYPE = "Class"
    TERMCOUNTS = None

    SOURCEGRAPH = None
    MARKDOWNPROCESS = True
    EXPANDEDTERMS = {}
    TERMS = {}

    TERMSLOCK = threading.Lock()
    RDFLIBLOCK = threading.Lock()

    def __init__(self, uri: str, ttype=None, label: str = "", layer=None):
        term_id = uri2id(uri)
        self.layer = CORE
        if layer:
            self.layer = layer
        self.termdesc = None

        self.parent = None
        self.checkedDataTypeParents = False
        self.supersededBy = None
        self.supersedes = None
        self.supers = None
        self.termStack = None
        self.subs = None
        self.members = None
        self.props = None
        self.propUsedOn = None
        self.ranges = None
        self.domains = None
        self.targetOf = None
        self.equivalents = None
        self.gotinverseOf = False
        self.inverseOf = None
        self.comments = None
        self.comment = None
        self.srcacks = None
        self.sources = None
        self.acks = None
        self.examples = None
        global DATATYPEURI, ENUMERATIONURI
        cls = self.__class__
        if ttype == rdflib.RDFS.Class:
            self.ttype = sdoterm.SdoTermType.TYPE
            if uri == str(DATATYPEURI):  # The base DataType is defined as a Class
                self.ttype = sdoterm.SdoTermType.DATATYPE
            elif uri == str(
                ENUMERATIONURI
            ):  # The base Enumeration Type is defined as a Class
                self.ttype = sdoterm.SdoTermType.ENUMERATION
            elif self._isEnumeration(term_id=term_id):
                self.ttype = sdoterm.SdoTermType.ENUMERATION
        elif ttype == rdflib.RDF.Property:
            self.ttype = sdoterm.SdoTermType.PROPERTY
        elif ttype == ENUMERATIONURI:
            self.ttype = sdoterm.SdoTermType.ENUMERATION
        elif ttype == DATATYPEURI:
            self.ttype = sdoterm.SdoTermType.DATATYPE
        elif not ttype:
            self.ttype = sdoterm.SdoTermType.REFERENCE
            label = term_id
        else:
            self.parent = cls._getTerm(str(ttype), createReference=True)

            if self.parent.termType == sdoterm.SdoTermType.ENUMERATION:
                self.ttype = sdoterm.SdoTermType.ENUMERATIONVALUE
            elif self.parent.termType == sdoterm.SdoTermType.DATATYPE:
                self.ttype = sdoterm.SdoTermType.DATATYPE
            else:
                self.ttype = sdoterm.SdoTermType.REFERENCE

        self.termdesc = sdoterm.SdoTermforType(
            self.ttype, term_id=term_id, uri=uri, label=label
        )
        if self.ttype == sdoterm.SdoTermType.ENUMERATIONVALUE and self.parent:
            self.termdesc.enumerationParent.setId(self.parent.id)

        self.termdesc.acknowledgements = self.getAcknowledgements()
        self.termdesc.comment = self.getComment()
        self.termdesc.comments = self.getComments()
        self.termdesc.equivalents.setIds(self.getEquivalents())
        self.termdesc.pending = self.inLayers("pending")
        self.termdesc.retired = self.inLayers("attic")
        self.termdesc.extLayer = self.getExtLayer()
        self.termdesc.sources = self.getSources()
        self.termdesc.subs.setIds(self.getSubs())
        self.termdesc.supers.setIds(self.getSupers())
        self.termdesc.supersededBy = self.getSupersededBy()
        self.termdesc.supersedes = self.getSupersedes()
        self.termdesc.superseded = self.superseded()
        self.termdesc.termStack.setTerms(self.getTermStack())
        self.termdesc.superPaths = (
            self.getParentPaths()
        )  # MUST be called after supers has been added to self.termdesc

        # Class (Type) Building
        if self.ttype in sdoterm.SdoTerm.TYPE_LIKE_TYPES:
            self.termdesc.properties.setIds(self.getProperties(getall=False))
            self.termdesc.allproperties.setIds(self.getProperties(getall=True))
            self.termdesc.expectedTypeFor.setIds(self.getTargetOf())
            if self.ttype == sdoterm.SdoTermType.ENUMERATION:
                if not len(self.termdesc.properties):
                    self.termdesc.termStack.clear()
                self.termdesc._enumerationMembers.setIds(self.getEnumerationMembers())
        elif self.ttype == sdoterm.SdoTermType.PROPERTY:
            self.termdesc.domainIncludes.setIds(self.getDomains())
            self.termdesc.rangeIncludes.setIds(self.getRanges())
            self.termdesc.inverse.setId(self.getInverseOf())
        elif self.ttype == sdoterm.SdoTermType.ENUMERATIONVALUE:
            pass
        elif self.ttype == sdoterm.SdoTermType.REFERENCE:
            self.termdesc.label = prefixedIdFromUri(uri)
            self.termdesc.comment = self.getComment()

        cls.TERMS[uri] = self.termdesc

    def __str__(self):
        return ("<SdoTermSource: %s '%s'>") % (self.ttype, self.id)

    @property
    def id(self):
        return self.termdesc.id

    @property
    def uri(self):
        return self.termdesc.uri

    def getTermdesc(self) -> sdoterm.SdoType:
        return self.termdesc

    def getType(self) -> sdoterm.SdoTermType:
        return self.ttype

    def isClass(self) -> bool:
        return self.ttype == sdoterm.SdoTermType.TYPE

    def isProperty(self) -> bool:
        return self.ttype == sdoterm.SdoTermType.PROPERTY

    def isDataType(self) -> bool:
        if self.ttype == sdoterm.SdoTermType.DATATYPE:
            return True
        if self.isClass() and not self.checkedDataTypeParents:
            self.checkedDataTypeParents = True
            for super in self.getSupers():
                if super.isDataType():
                    self.ttype = sdoterm.SdoTermType.DATATYPE
                    return True
        return False

    @classmethod
    def _isEnumeration(cls, term_id: str) -> bool:
        global ENUMERATIONURI
        query = """
          ASK  {
                    %s rdfs:subClassOf* %s.
            }""" % (uriWrap(toFullId(term_id)), uriWrap(ENUMERATIONURI))

        result = cls.query(query)
        return result[-1]

    def _isEnumerationValue(self) -> bool:
        return self.ttype == sdoterm.SdoTermType.ENUMERATIONVALUE

    def isReference(self) -> bool:
        return self.ttype == sdoterm.SdoTermType.REFERENCE

    def getParent(self):
        return self.parent

    def getPrefixedId(self) -> str:
        return prefixedIdFromUri(self.uri)

    def getComments(self) -> typing.Sequence[str]:
        if not self.comments:
            self.comments = tuple(map(str, self.loadObjects(rdflib.RDFS.comment)))
        return self.comments

    def getComment(self) -> str:
        if not self.comment:
            self.loadComment()
        return self.comment

    def getSupersededBy(self):
        if not self.supersededBy:
            tmp = []
            ss = self.loadObjects("schema:supersededBy")
            for s in ss:
                t = uri2id(str(s))
                if t:
                    tmp.append(t)

            if len(tmp) > 1:
                log.debug(
                    "Warning '%s' supersededBy more than 1 term (%d)"
                    % (self.id, len(tmp))
                )
            if len(tmp):
                self.supersededBy = tmp[0]
            else:
                self.supersededBy = ""
        return self.supersededBy

    def superseded(self) -> bool:
        return len(self.getSupersededBy()) > 0

    def getSupersedes(self) -> typing.Sequence[str]:
        if not self.supersedes:
            self.supersedes = []
            subs = self.loadSubjects("schema:supersededBy")
            for sub in subs:
                self.supersedes.append(uri2id(str(sub)))
        return self.supersedes

    def getSources(self):
        if not self.sources:
            objs = self.loadObjects("schema:source")  # To accept later ttl versions.
            self.sources = list(objs)
        return self.sources

    def getAcknowledgements(self) -> typing.Sequence[str]:
        if not self.acks:
            acks = []
            objs = self.loadObjects(
                "schema:contributor"
            )  # To accept later ttl versions.
            for obj in objs:
                if obj:
                    cont = sdocollaborators.collaborator.getContributor(obj)
                    if cont:
                        acks.append(cont)
            self.acks = sorted(acks, key=lambda t: t.title)
        return self.acks

    def getLayer(self):
        return self.layer

    def getInverseOf(self):
        if not self.gotinverseOf:
            self.gotinverseOf = True
            inverse = self.loadValue("schema:inverseOf")
            if inverse:
                self.inverseOf = uri2id(str(inverse))
        return self.inverseOf

    def getSupers(self):
        if not self.supers:
            self.loadsupers()
        return self.supers

    def getTermStack(self):
        if not self.termStack:
            self.termStack = []
            for sup in self.getSupers():
                try:
                    s = self.__class__._getTerm(sup, createReference=True)
                    if s.termType == sdoterm.SdoTermType.REFERENCE:
                        continue
                    self.termStack.append(s)
                    if s.termStack:
                        self.termStack.extend(s.termStack.terms)
                except RecursionError as e:
                    e.add_note(f"Circular references with {self.termdesc}")
                    raise
            stack = []
            for t in reversed(self.termStack):
                if t not in stack:
                    stack.append(t)
            self.termStack = list(reversed(stack))
        return self.termStack

    def getSubs(self):
        if not self.subs:
            self.loadsubs()
        return self.subs

    def getProperties(self, getall=False):
        if not self.props:
            self.props = []
            subs = self.loadSubjects("schema:domainIncludes")
            for sub in subs:
                self.props.append(uri2id(str(sub)))
            self.props.sort()
        ret = self.props

        if getall:
            allprop_ids = set(self.props)
            for t in self.termStack:
                if not isinstance(t, sdoterm.SdoTerm):
                    term = self.__class__._getTerm(t, createReference=True)
                else:
                    term = t
                if term.id != self.id:
                    if term.id == "ENUMERATION":
                        break
                    if term.termType in sdoterm.SdoTerm.TYPE_LIKE_TYPES:
                        allprop_ids.update(term.properties.ids)
            ret = sorted(allprop_ids)
        return ret

    def getPropUsedOn(self):
        raise Exception("Not implemented yet")

    def getRanges(self):
        if not self.ranges:
            self.ranges = []
            objs = self.loadObjects("schema:rangeIncludes")
            for obj in objs:
                self.ranges.append(uri2id(str(obj)))
            self.ranges.sort()
        return self.ranges

    def getDomains(self):
        if not self.domains:
            self.domains = []
            objs = self.loadObjects("schema:domainIncludes")
            for obj in objs:
                self.domains.append(uri2id(str(obj)))
            self.domains.sort()
        return self.domains

    def getTargetOf(self, plusparents=False, stopontarget=False):
        global ENUMERATIONURI, THINGURI
        if not self.targetOf:
            self.targetOf = []
            subs = self.loadSubjects("schema:rangeIncludes")
            for sub in subs:
                self.targetOf.append(uri2id(str(sub)))
        ret = self.targetOf
        if not (len(self.targetOf) and stopontarget):
            if plusparents:
                targets = self.targetOf
                for s in self.getSupers():
                    sup = cls._getTerm(s, createReference=True)
                    if sup.uri() == ENUMERATIONURI or sup.uri == THINGURI:
                        break
                    ptargets = sup.expectedTypeFor
                    for t in ptargets:
                        targets.append(t)
                    if len(targets) and stopontarget:
                        break
                ret = targets
        ret.sort()
        return ret

    def getEquivalents(self):
        if not self.equivalents:
            self.equivalents = []
            equivalents = self.loadObjects("owl:equivalentClass")
            equivalents.extend(self.loadObjects("owl:equivalentProperty"))
            for e in equivalents:
                self.equivalents.append(str(e))
        return self.equivalents

    def inLayers(self, layers):
        return self.layer in layers

    def getExtLayer(self):
        ret = ""
        lay = self.layer
        if len(lay) and lay != CORE:
            ret = lay
        return ret

    @classmethod
    def subClassOf(cls, child, parent):
        if isinstance(child, str):
            child = cls.getTerm(child)
        if isinstance(parent, str):
            parent = cls.getTerm(parent)

        if child == parent:
            return True

        parents = child.supers.ids
        if parent.id in parents:
            return True

        for p in parents:
            if cls.subClassOf(p, parent):
                return True
        return False

    def loadComment(self):
        comments = self.getComments()
        wpre = None
        name = self.termdesc.id
        if name.startswith(
            "http:"
        ):  # Wikilinks in markdown default to current site - extermals need overriding
            val = os.path.basename(name)
            wpre = name[: len(name) - len(val)]

        if self.__class__.MARKDOWNPROCESS:
            comment_buffer = [
                localmarkdown.Markdown.parse(comment, wpre=wpre) for comment in comments
            ]
        else:
            comment_buffer = comments
        result = " ".join(comment_buffer)
        self.comment = result.strip()

    def loadValue(self, valType):
        ret = self.loadObjects(valType)
        if not ret or len(ret) == 0:
            return None
        return ret[0]

    def loadObjects(self, pred):
        query = """
        SELECT ?val WHERE {
                %s %s ?val.
         }""" % (uriWrap(toFullId(self.id)), uriWrap(pred))
        res = self.__class__.query(query)
        return [row.val for row in res]

    def loadSubjects(self, pred):
        query = """
        SELECT ?sub WHERE {
                ?sub %s %s.
         }""" % (uriWrap(pred), uriWrap(toFullId(self.id)))
        res = self.__class__.query(query)
        return [row.sub for row in res]

    def loadsupers(self):
        fullId = toFullId(self.id)
        query = """
        SELECT ?sup WHERE {
             {
                 %s rdfs:subClassOf ?sup .
             }UNION{
                 %s rdfs:subPropertyOf ?sup .
             }
         }
         ORDER BY ?sup""" % (uriWrap(fullId), uriWrap(fullId))

        res = self.__class__.query(query)
        self.supers = [uri2id(str(row.sup)) for row in res]

    def loadsubs(self):
        fullId = toFullId(self.id)
        if self.ttype in sdoterm.SdoTerm.TYPE_LIKE_TYPES:
            sel = "rdfs:subClassOf"
        else:
            sel = "rdfs:subPropertyOf"
        query = """
        SELECT ?sub WHERE {
                ?sub %s %s.
         }ORDER BY ?sub""" % (uriWrap(sel), uriWrap(fullId))
        res = self.__class__.query(query)
        self.subs = [uri2id(str(row.sub)) for row in res]

        if self.ttype == sdoterm.SdoTermType.DATATYPE:
            subjects = self.loadSubjects(
                "a"
            )  # Enumerationvalues have an Enumeration as a type
            self.subs.extend([uri2id(str(child)) for child in subjects])

    def getEnumerationMembers(self):
        if not self.members and self.ttype == sdoterm.SdoTermType.ENUMERATION:
            subjects = self.loadSubjects(
                "a"
            )  # Enumerationvalues have an Enumeration as a type
            self.members = [uri2id(str(child)) for child in subjects]
            self.members.sort()
        return self.members

    def getParentPaths(self, cstack: typing.Sequence[str] = None):
        self._pstacks = []
        cstack = cstack or []
        self._pstacks.append(cstack)
        self._getParentPaths(self.termdesc, cstack)

        inserts = []
        if self.ttype == sdoterm.SdoTermType.PROPERTY:
            inserts = ["Property", "Thing"]
        elif self.ttype == sdoterm.SdoTermType.DATATYPE and self.id != "DataType":
            inserts = ["DataType"]
        elif self.ttype == sdoterm.SdoTermType.TYPE:
            base = self._pstacks[0][0]
            if base != self.id:
                basetype = self.__class__._getTerm(base)
            else:
                basetype = self.termdesc
            if basetype.termType == sdoterm.SdoTermType.DATATYPE:
                inserts = ["DataType"]

        for ins in inserts:
            for s in self._pstacks:
                s.insert(0, ins)

        return self._pstacks

    def _getParentPaths(self, term: sdoterm.SdoTerm, cstack):
        cstack.insert(0, term.id)
        tmpStacks = []
        tmpStacks.append(cstack)
        super_ids = list(term.supers.ids)

        if (
            term.termType == sdoterm.SdoTermType.ENUMERATIONVALUE
            and term.enumerationParent
            and term.enumerationParent.id not in super_ids
        ):
            super_ids.append(term.enumerationParent.id)

        if super_ids:
            for i in range(len(super_ids)):
                if i > 0:
                    t = cstack[:]
                    tmpStacks.append(t)
                    self._pstacks.append(t)

            x = 0
            for parent_id in super_ids:
                if not (
                    parent_id.startswith("http:") or parent_id.startswith("https:")
                ):
                    sup = self.__class__._getTerm(parent_id)
                    self._getParentPaths(sup, tmpStacks[x])
                    x += 1

    @classmethod
    def getParentPathTo(cls, start_term_id: str, end_term_id: str = None):
        # Output paths from start_term to only if end_term in path
        end_term_id = end_term_id or "Thing"
        start_term = cls.getTerm(start_term_id, expanded=True)
        outList = []
        for path in start_term.superPaths:
            if end_term_id in path:
                outList.append(path)
        return outList

    def checkForEnumVal(self) -> bool:
        if self.ttype == sdoterm.SdoTermType.ENUMERATION:
            return True

        for super_terms in self.supers:
            if super_terms.checkForEnumVal():
                return True
        return False

    @classmethod
    def expandTerms(cls, terms, depth: int = 2):
        return [cls.expandTerm(t, depth=depth) for t in terms]

    @classmethod
    def expandTerm(cls, termdesc: sdoterm.SdoTerm, depth: int = 2) -> sdoterm.SdoTerm:
        """Expand a term, e.g. expand the properties that only contain term-ids to contain actual SdoTerm instances."""
        assert isinstance(termdesc, sdoterm.SdoTerm), termdesc
        if termdesc.expanded() or depth < 1:
            return termdesc

        termdesc.markExpanded(depth)

        # TODO: optimise expansion.

        termdesc.superPaths = [
            sdoterm.SdoTermSequence.forElements(paths) for paths in termdesc.superPaths
        ]
        termdesc.termStack.setTerms(cls.termsFromIds(termdesc.termStack.ids))
        termdesc.supers.setTerms(cls.termsFromIds(termdesc.supers.ids))
        termdesc.subs.setTerms(cls.termsFromIds(termdesc.subs.ids))
        termdesc.equivalents.setTerms(cls.termsFromIds(termdesc.equivalents.ids))

        if termdesc.termType in sdoterm.SdoTerm.TYPE_LIKE_TYPES:
            if depth > 1:  # Expand the properties but prevent recursion further
                termdesc.properties.setTerms(
                    cls.expandTerms(
                        cls.termsFromIds(termdesc.properties.ids), depth=depth - 1
                    )
                )
                termdesc.expectedTypeFor.setTerms(
                    cls.expandTerms(
                        cls.termsFromIds(termdesc.expectedTypeFor.ids), depth=depth - 1
                    )
                )
            else:
                termdesc.properties.setTerms(cls.termsFromIds(termdesc.properties.ids))
                termdesc.expectedTypeFor.setTerms(
                    cls.termsFromIds(termdesc.expectedTypeFor.ids)
                )

            if termdesc.termType == sdoterm.SdoTermType.ENUMERATION:
                termdesc.enumerationMembers.setTerms(
                    cls.termsFromIds(termdesc.enumerationMembers.ids)
                )
        elif termdesc.termType == sdoterm.SdoTermType.PROPERTY:
            termdesc.domainIncludes.setTerms(
                cls.termsFromIds(termdesc.domainIncludes.ids)
            )
            termdesc.rangeIncludes.setTerms(
                cls.termsFromIds(termdesc.rangeIncludes.ids)
            )
            termdesc.inverse.setTerm(cls.termFromId(termdesc.inverse.id))
        elif termdesc.termType == sdoterm.SdoTermType.ENUMERATIONVALUE:
            termdesc.enumerationParent.setTerm(
                cls.termFromId(termdesc.enumerationParent.id)
            )

        if (
            depth > 0
        ):  # Expand the individual termdescs in the terms' termstack but prevent recursion further.
            termdesc.termStack.setTerms(
                cls.expandTerms(
                    cls.termsFromIds(termdesc.termStack.ids), depth=depth - 1
                )
            )

        return termdesc

    @classmethod
    def termFromId(cls, id: str = "") -> sdoterm.SdoTerm:
        ids = cls.termsFromIds([id])
        if len(ids):
            return ids[0]
        return None

    @classmethod
    def termsFromIds(
        cls, ids: typing.Sequence[str] = None
    ) -> typing.Sequence[sdoterm.SdoTerm]:
        """Convert a sequence of term-identities into a sequence of SdoTerms."""
        ids = ids or []
        ret = []
        for tid in ids:
            if tid and len(tid):
                if type(tid) is str:
                    ret.append(cls._getTerm(tid, createReference=True))
                else:
                    ret.append(tid)
        return ret

    @classmethod
    def _singleTermFromResult(
        cls, res: typing.Sequence[rdflib.query.ResultRow], termId: str
    ) -> sdoterm.SdoTerm:
        """Return a single term matching `termId` from res."""
        tmp = _TermAccumulator(termId)
        for row in res:  # Assumes termdefinition rows are ordered by termId
            if tmp.id != termId:  # New term definition starts on this row
                if tmp.id:
                    term = cls._createTerm(tmp.id)
                    if term:
                        ret.append(term)
                tmp = _TermAccumulator(termId)
            tmp.appendRow(row)

        return cls._createTerm(tmp)

    @classmethod
    def termsFromResults(
        cls, res: typing.Sequence[rdflib.query.ResultRow]
    ) -> typing.Sequence[sdoterm.SdoTerm]:
        rows_by_term_id = {}
        for row in res:
            key = str(row.term)
            if not key in rows_by_term_id:
                rows_by_term_id[key] = _TermAccumulator(key)
            rows_by_term_id[key].appendRow(row)

        return list(
            filter(
                bool,
                [cls._createTerm(acc) for acc in rows_by_term_id.values()],
            )
        )

    @classmethod
    def _createTerm(cls, tmp: _TermAccumulator) -> sdoterm.SdoTerm:
        global DATATYPEURI, ENUMERATIONURI
        if not tmp or not tmp.id:
            return None

        if DATATYPEURI in tmp.types:
            tmp.type = DATATYPEURI
        elif ENUMERATIONURI in tmp.sups:
            tmp.type = ENUMERATIONURI

        term = cls.TERMS.get(tmp.id, None)
        if not term:  # Already created this term ?
            t = cls(tmp.id, ttype=tmp.type, label=tmp.label, layer=tmp.layer)
            term = t.termdesc
        return term

    @classmethod
    def triples4Term(cls, termId: str):
        term = cls.getTerm(termId)
        g = cls.SOURCEGRAPH
        triples = g.triples((rdflib.URIRef(term.uri), None, None))
        return triples

    @classmethod
    def getTermAsRdfString(cls, termId: str, output_format: str, full=False):
        global VOCABURI
        term = cls.getTerm(termId)
        if not term or term.termType == sdoterm.SdoTermType.REFERENCE:
            return ""
        g = rdflib.Graph()

        schema = rdflib.Namespace(VOCABURI)
        g.bind("schema", VOCABURI)

        if not full:  # Only the term definition
            triples = cls.triples4Term(term)
            for trip in triples:
                g.add(trip)
        else:  # full - Include all related terms
            types = []
            props = []
            stack = [term]

            stack.extend(cls.termsFromIds(term.termStack.ids))
            for t in stack:
                if t.termType == sdoterm.SdoTermType.PROPERTY:
                    props.append(t)
                else:
                    types.append(t)
                    if t.termType == sdoterm.SdoTermType.ENUMERATIONVALUE:
                        types.append(cls.termFromId(t.enumerationParent.id))
                    elif t == stack[0]:
                        props.extend(cls.termsFromIds(t.allproperties.ids))

            for t in types:
                triples = cls.triples4Term(t.id)
                for trip in triples:
                    g.add(trip)

            for p in props:
                triples = cls.triples4Term(p.id)
                for trip in triples:
                    g.add(trip)

        if output_format == "rdf":
            output_format = "pretty-xml"
        ret = g.serialize(format=output_format, auto_compact=True, sort_keys=True)
        return ret

    @classmethod
    def getAllTypes(cls, layer=None, expanded=False):
        return cls.getAllTerms(
            ttype=sdoterm.SdoTermType.TYPE, layer=layer, expanded=expanded
        )

    @classmethod
    def getAllProperties(cls, layer=None, expanded=False):
        return cls.getAllTerms(
            ttype=sdoterm.SdoTermType.PROPERTY, layer=layer, expanded=expanded
        )

    @classmethod
    def getAllEnumerations(cls, layer=None, expanded=False):
        return cls.getAllTerms(
            ttype=sdoterm.SdoTermType.ENUMERATION, layer=layer, expanded=expanded
        )

    @classmethod
    def getAllEnumerationvalues(cls, layer=None, expanded=False):
        return cls.getAllTerms(
            ttype=sdoterm.SdoTermType.ENUMERATIONVALUE, layer=layer, expanded=expanded
        )

    @classmethod
    def getAllTerms(
        cls, ttype=None, layer=None, suppressSourceLinks=False, expanded=False
    ):
        with pretty_logger.BlockLog(
            logger=log, message="GetAllTerms", timing=True
        ) as block:
            global DATATYPEURI, ENUMERATIONURI
            typsel = ""
            extra = ""
            if ttype == sdoterm.SdoTermType.TYPE:
                typsel = "a <%s>;" % rdflib.RDFS.Class
            elif ttype == sdoterm.SdoTermType.PROPERTY:
                typsel = "a <%s>;" % rdflib.RDF.Property
            elif ttype == sdoterm.SdoTermType.DATATYPE:
                typsel = "a <%s>;" % DATATYPEURI
            elif ttype == sdoterm.SdoTermType.ENUMERATION:
                typsel = "rdfs:subClassOf* <%s>;" % ENUMERATIONURI
            elif ttype == sdoterm.SdoTermType.ENUMERATIONVALUE:
                extra = "?type rdfs:subClassOf*  <%s>." % ENUMERATIONURI
            elif not ttype:
                typesel = ""
            else:
                log.debug("Invalid type value '%s'" % ttype)

            laysel = ""
            fil = ""
            suppress = ""
            if layer:
                if layer == "core":
                    fil = "FILTER NOT EXISTS { ?term schema:isPartOf ?x. }"
                else:
                    laysel = "schema:isPartOf <%s>;" % uriFromLayer(layer)

            if suppressSourceLinks:
                suppress = "FILTER NOT EXISTS { ?s dc:source ?term. }"

            query = """SELECT DISTINCT ?term ?type ?label ?layer ?sup WHERE {
                 ?term a ?type;
                    %s
                    %s
                    rdfs:label ?label.
                %s
                OPTIONAL {
                    ?term schema:isPartOf ?layer.
                }
                OPTIONAL {
                    ?term rdfs:subClassOf ?sup.
                }
                OPTIONAL {
                    ?term rdfs:subPropertyOf ?sup.
                }
                %s
                %s
            }
            ORDER BY ?term
            """ % (typsel, laysel, extra, fil, suppress)

            log.debug("query %s", query)
            res = cls.query(query)
            log.debug("res %d", len(res))

            terms = []
            if expanded:
                with pretty_logger.BlockLog(
                    logger=log, message=f"Expanding {len(res)} terms", timing=True
                ):
                    terms = cls.termsFromResults(res)

            else:
                for row in res:
                    term = uri2id(str(row.term))
                    if not term in terms:
                        terms.append(term)
            block.message = f"GetAllTerms: {len(terms)} terms, total: {len(cls.TERMS)}"
            return terms

    @classmethod
    def getAcknowledgedTerms(cls, ack):
        query = (
            """SELECT DISTINCT ?term ?type ?label ?layer ?sup WHERE {
             ?term a ?type;
                schema:contributor <%s>;
                rdfs:label ?label.
                OPTIONAL {
                    ?term schema:isPartOf ?layer.
                }
                OPTIONAL {
                    ?term rdfs:subClassOf ?sup.
                }
                OPTIONAL {
                    ?term rdfs:subPropertyOf ?sup.
                }
            }
            ORDER BY ?term
            """
            % ack
        )
        res = cls.query(query)
        terms = cls.termsFromResults(res)
        return terms

    @classmethod
    def setSourceGraph(cls, g: rdflib.graph.Graph):
        global VOCABURI
        cls.SOURCEGRAPH = g
        g.bind("schema", VOCABURI)
        bindNameSpaces(g)

        cls.TERMS = {}  # Clear cache
        cls.EXPANDEDTERMS = {}

    @classmethod
    def loadSourceGraph(
        cls, files=None, init: bool = False, vocaburi: str = None
    ) -> None:
        """Load the source graph.

        Args:
          files: this can be either a string or a sequence of strings.
                 The special file 'default' loads the default set of files.
                 A single string is interpreted as a file-path to load from.
                 A sequence of string is interpreted as a set of file-paths to load from.
          init: if true, reset the `SOURCEGRAPH` class variable.
          vocaburi: the vocabulary to use.
        """
        global VOCABURI, DEFTRIPLESFILESGLOB
        if init:
            cls.SOURCEGRAPH = None
        if not VOCABURI and not vocaburi:
            cls.setVocabUri(DEFVOCABURI)
        elif vocaburi:
            cls.setVocabUri(vocaburi)

        if not files or files == "default":
            if cls.SOURCEGRAPH:
                if not cls.LOADEDDEFAULT:
                    raise Exception(
                        "Sourcegraph already loaded - cannot overwrite with defaults"
                    )
                log.info("Default files already loaded")
                return

            else:
                cls.LOADEDDEFAULT = True
                log.info(
                    "SdoTermSource.loadSourceGraph() loading from default files found in globs: %s",
                    ",".join(DEFTRIPLESFILESGLOB),
                )
                files = []
                for g in DEFTRIPLESFILESGLOB:
                    files.extend(glob.glob(g))
        elif isinstance(files, str):
            cls.LOADEDDEFAULT = False
            log.info("SdoTermSource.loadSourceGraph() loading from file: %s", files)
            files = [files]
        else:
            cls.LOADEDDEFAULT = False
            log.info(
                "SdoTermSource.loadSourceGraph() loading from %d files", len(files)
            )

        if not len(files):
            raise Exception("No triples file(s) to load")

        cls.setSourceGraph(rdflib.Graph())

        for file_path in files:
            cls.SOURCEGRAPH += _loadOneSourceGraph(file_path)
        log.info(
            "Done: Loaded %s triples - %s terms",
            len(cls.sourceGraph()),
            len(cls.getAllTerms()),
        )

    @classmethod
    def sourceGraph(cls) -> rdflib.Graph:
        if cls.SOURCEGRAPH == None:
            cls.loadSourceGraph()
        return cls.SOURCEGRAPH

    @staticmethod
    def setVocabUri(uri: str = None):
        global VOCABURI, DATATYPEURI, ENUMERATIONURI, THINGURI
        VOCABURI = uri or DEFVOCABURI
        DATATYPEURI = rdflib.URIRef(VOCABURI + "DataType")
        ENUMERATIONURI = rdflib.URIRef(VOCABURI + "Enumeration")
        THINGURI = rdflib.URIRef(VOCABURI + "Thing")

    @classmethod
    def vocabUri(cls):
        global VOCABURI
        if not VOCABURI:
            cls.setVocabUri()
        return VOCABURI

    @classmethod
    def query(cls, query_string: str) -> typing.Sequence[rdflib.query.ResultRow]:
        graph = cls.sourceGraph()
        with cls.RDFLIBLOCK:
            result = tuple(graph.query(query_string))
        return result

    @classmethod
    def termCounts(cls) -> int:
        global VOCABURI
        if not cls.TERMCOUNTS:
            count = (
                """SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {
                ?s a ?type .
                FILTER (strStarts(str(?s),"%s"))
            } """
                % VOCABURI
            )
            res = cls.query(count)
            allterms = int(res[0][0])

            count = (
                """SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {
                ?s a rdfs:Class .
                FILTER (strStarts(str(?s),"%s"))
            } """
                % VOCABURI
            )
            res = cls.query(count)
            classes = int(res[0][0])

            count = (
                """SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {
                ?s a rdf:Property .
                FILTER (strStarts(str(?s),"%s"))
            } """
                % VOCABURI
            )
            res = cls.query(count)
            properties = int(res[0][0])

            count = (
                """SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {
                ?s rdfs:subClassOf* schema:Enumeration .
                FILTER (strStarts(str(?s),"%s"))
            } """
                % VOCABURI
            )
            res = cls.query(count)
            enums = int(res[0][0])

            count = (
                """SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {
                ?s a ?type .
                ?type rdfs:subClassOf* schema:Enumeration .
                FILTER (strStarts(str(?s),"%s"))
            } """
                % VOCABURI
            )
            res = cls.query(count)
            enumvals = int(res[0][0])

            count = (
                """SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {
                {
                    ?s a schema:DataType .
                }UNION{
                    ?s rdf:type* schema:DataType .
                }UNION{
                    ?s rdfs:subClassOf* ?x .
                    ?x a schema:DataType .
                }
                FILTER (strStarts(str(?s),"%s"))
           } """
                % VOCABURI
            )
            res = cls.query(count)
            datatypes = int(res[0][0])

            count = (
                """SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {
                ?s rdfs:subClassOf* ?x .
                ?x a schema:DataType .
                FILTER (strStarts(str(?s),"%s"))
           } """
                % VOCABURI
            )
            res = cls.query(count)
            datatypeclasses = int(res[0][0])

            types = classes
            types -= 1  # DataType not counted
            types -= enums
            types -= datatypeclasses
            datatypes -= 1  # Datatype not counted

            cls.TERMCOUNTS = {}
            cls.TERMCOUNTS[sdoterm.SdoTermType.TYPE] = types
            cls.TERMCOUNTS[sdoterm.SdoTermType.PROPERTY] = properties
            cls.TERMCOUNTS[sdoterm.SdoTermType.DATATYPE] = datatypes
            cls.TERMCOUNTS[sdoterm.SdoTermType.ENUMERATION] = enums
            cls.TERMCOUNTS[sdoterm.SdoTermType.ENUMERATIONVALUE] = enumvals
            cls.TERMCOUNTS["All"] = types + properties + datatypes + enums + enumvals
        return cls.TERMCOUNTS

    @classmethod
    def setMarkdownProcess(cls, process: bool):
        cls.MARKDOWNPROCESS = process

    @classmethod
    def termCache(cls):
        return cls.TERMS

    @classmethod
    def getTerm(
        cls,
        termId: str,
        expanded: bool = False,
        refresh: bool = False,
        createReference: bool = False,
    ):
        with cls.TERMSLOCK:
            return cls._getTerm(
                termId,
                expanded=expanded,
                refresh=refresh,
                createReference=createReference,
            )

    @classmethod
    def _getTerm(
        cls,
        termId: str,
        expanded: bool = False,
        refresh: bool = False,
        createReference: bool = False,
    ):
        if not termId:
            return None
        assert isinstance(termId, str), termId
        termId = termId.strip()
        fullId = toFullId(termId)
        term = cls.TERMS.get(fullId, None)

        if term and refresh:
            del cls.TERMS[termId]
            log.info("Term '%s' found and removed" % termId)
            term = None

        query = """
        SELECT ?term ?type ?label ?layer ?sup WHERE {
             %s a ?type;
                rdfs:label ?label.
            OPTIONAL {
                %s schema:isPartOf ?layer.
            }
            OPTIONAL {
                %s rdfs:subClassOf ?sup.
            }
            OPTIONAL {
                %s rdfs:subPropertyOf ?sup.
            }

        }""" % (uriWrap(fullId), uriWrap(fullId), uriWrap(fullId), uriWrap(fullId))

        if not term:
            res = cls.query(query)
            if len(res):
                term = cls._singleTermFromResult(res, termId=fullId)
            elif createReference:
                # Create a new TermSource
                term = cls(fullId).getTermdesc()
            else:
                log.warning("No definition of term %s" % fullId)

        if term and expanded and not term.expanded():
            exterm = cls.EXPANDEDTERMS.get(fullId, None)
            if not exterm:
                exterm = cls.expandTerm(term)
                cls.EXPANDEDTERMS[fullId] = exterm
            term = exterm

        return term


def toFullId(termId: str) -> str:
    global VOCABURI
    assert VOCABURI
    if not ":" in termId:  # Includes full path or namespaces
        return VOCABURI + termId

    if termId.startswith("http"):
        return termId
    prefix, id_component = termId.split(":")
    return "%s%s" % (uriForPrefix(prefix), id_component)


def uriWrap(identity_str: str) -> str:
    if identity_str.startswith("http://") or identity_str.startswith("https://"):
        return "<%s>" % identity_str
    return identity_str


LAYERPATTERN = None


def layerFromUri(uri: str) -> str:
    global VOCABURI
    global LAYERPATTERN
    assert VOCABURI
    if uri:
        if not LAYERPATTERN:
            voc = VOCABURI
            if voc.endswith("/") or voc.endswith("#"):
                voc = voc[: len(voc) - 1]
            prto, root = getProtoAndRoot(voc)
            LAYERPATTERN = "^%s([\w]*)\.%s" % (prto, root)

        if LAYERPATTERN:
            m = re.search(LAYERPATTERN, str(uri))
            if m:
                return m.group(1)
    return None


def uriFromLayer(layer: str = None) -> str:
    global VOCABURI
    voc = VOCABURI
    if voc.endswith("/") or voc.endswith("#"):
        voc = voc[: len(voc) - 1]
    if not layer:
        return voc
    prto, root = getProtoAndRoot(voc)
    return "%s%s.%s" % (prto, layer, root)


ProtoAndRoot = collections.namedtuple("ProtoAndRoot", ["proto", "root"])


def getProtoAndRoot(uri: str) -> ProtoAndRoot:
    m = re.search("^(http[s]?:\/\/)(.*)", uri)
    if m:
        prto = m.group(1)
        root = m.group(2)
        return ProtoAndRoot(prto, root)
    return ProtoAndRoot(None, None)


def uri2id(uri: str) -> str:
    global VOCABURI
    if uri.startswith(VOCABURI):
        return uri[len(VOCABURI) :]
    return uri


def prefixFromUri(uri: str) -> rdflib.term.URIRef:
    for pref, pth in SdoTermSource.SOURCEGRAPH.namespaces():
        if uri.startswith(str(pth)):
            return pref
    return None


def uriForPrefix(pre: str) -> str:
    for pref, pth in SdoTermSource.SOURCEGRAPH.namespaces():
        if pre == pref:
            return pth
    return None


def prefixedIdFromUri(uri: str) -> str:
    """Converts a URI into a string of the form namespace:term."""
    prefix = prefixFromUri(uri)
    if prefix:
        base = os.path.basename(uri)
        if "#" in base:
            base = base.split("#")[1]
        return "%s:%s" % (prefix, base)
    return uri
