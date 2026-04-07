#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import collections
import copy
import glob
import json
import logging
import rdflib
import re
import sys
import threading
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union, Iterable, Sequence, Set, Type, cast

if Path.cwd() not in [Path(p).resolve() for p in sys.path]:
    sys.path.insert(1, str(Path.cwd()))

import software
import software.SchemaTerms.sdoterm as sdoterm
import software.SchemaTerms.sdocollaborators as sdocollaborators
import software.SchemaTerms.localmarkdown as localmarkdown

import software.util.pretty_logger as pretty_logger
from software.util.sort_dict import sort_dict

log: logging.Logger = logging.getLogger(__name__)

DEFVOCABURI: str = "https://schema.org/"
VOCABURI: Optional[str] = None
DATATYPEURI: Optional[rdflib.URIRef] = None
ENUMERATIONURI: Optional[rdflib.URIRef] = None
THINGURI: Optional[rdflib.URIRef] = None

CORE: str = "core"
DEFTRIPLESFILESGLOB: Tuple[str, str] = ("data/*.ttl", "data/ext/*/*.ttl")
LOADEDDEFAULT: bool = False


def bindNameSpaces(graph: rdflib.Graph) -> None:
    namespaces: Dict[str, str] = {
        "dc": "http://purl.org/dc/elements/1.1/",
        "dcat": "http://www.w3.org/ns/dcat#",
        "dct": "http://purl.org/dc/terms/",
        "dctype": "http://purl.org/dc/dcmitype/",
        "foaf": "http://xmlns.com/foaf/0.1/",
        "owl": "http://www.w3.org/2002/07/owl#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "skos": "http://www.w3.org/2004/02/skos/core#",
        "void": "http://rdfs.org/ns/void#",
        "cmns-cls": "https://www.omg.org/spec/Commons/Classifiers/",
        "cmns-col": "https://www.omg.org/spec/Commons/Collections/",
        "cmns-dt": "https://www.omg.org/spec/Commons/DatesAndTimes/",
        "cmns-ge": "https://www.omg.org/spec/Commons/GeopoliticalEntities/",
        "cmns-id": "https://www.omg.org/spec/Commons/Identifiers/",
        "cmns-loc": "https://www.omg.org/spec/Commons/Locations/",
        "cmns-q": "https://www.omg.org/spec/Commons/Quantities/",
        "cmns-txt": "https://www.omg.org/spec/Commons/Text/",
        "lcc-3166-1": "https://www.omg.org/spec/LCC/Countries/ISO3166-1-CountryCodes/",
        "lcc-4217": "https://www.omg.org/spec/LCC/Countries/ISO4217-CurrencyCodes/",
        "lcc-lr": "https://www.omg.org/spec/LCC/Languages/LanguageRepresentation/",
        "fibo-be-corp-corp": "https://spec.edmcouncil.org/fibo/ontology/BE/Corporations/Corporations/",
        "fibo-be-ge-ge": "https://spec.edmcouncil.org/fibo/ontology/BE/GovernmentEntities/GovernmentEntities/",
        "fibo-be-le-cb": "https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/CorporateBodies/",
        "fibo-be-le-lp": "https://spec.edmcouncil.org/fibo/ontology/BE/LegalEntities/LegalPersons/",
        "fibo-be-nfp-nfp": "https://spec.edmcouncil.org/fibo/ontology/BE/NotForProfitOrganizations/NotForProfitOrganizations/",
        "fibo-be-oac-cctl": "https://spec.edmcouncil.org/fibo/ontology/BE/OwnershipAndControl/CorporateControl/",
        "fibo-fbc-dae-dbt": "https://spec.edmcouncil.org/fibo/ontology/FBC/DebtAndEquities/Debt/",
        "fibo-fbc-pas-fpas": "https://spec.edmcouncil.org/fibo/ontology/FBC/ProductsAndServices/FinancialProductsAndServices/",
        "fibo-fnd-acc-cur": "https://spec.edmcouncil.org/fibo/ontology/FND/Accounting/CurrencyAmount/",
        "fibo-fnd-agr-ctr": "https://spec.edmcouncil.org/fibo/ontology/FND/Agreements/Contracts/",
        "fibo-fnd-arr-doc": "https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Documents/",
        "fibo-fnd-arr-lif": "https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Lifecycles/",
        "fibo-fnd-dt-oc": "https://spec.edmcouncil.org/fibo/ontology/FND/DatesAndTimes/Occurrences/",
        "fibo-fnd-org-org": "https://spec.edmcouncil.org/fibo/ontology/FND/Organizations/Organizations/",
        "fibo-fnd-pas-pas": "https://spec.edmcouncil.org/fibo/ontology/FND/ProductsAndServices/ProductsAndServices/",
        "fibo-fnd-plc-adr": "https://spec.edmcouncil.org/fibo/ontology/FND/Places/Addresses/",
        "fibo-fnd-plc-fac": "https://spec.edmcouncil.org/fibo/ontology/FND/Places/Facilities/",
        "fibo-fnd-plc-loc": "https://spec.edmcouncil.org/fibo/ontology/FND/Places/Locations/",
        "fibo-fnd-pty-pty": "https://spec.edmcouncil.org/fibo/ontology/FND/Parties/Parties/",
        "fibo-fnd-rel-rel": "https://spec.edmcouncil.org/fibo/ontology/FND/Relations/Relations/",
        "fibo-pay-ps-ps": "https://spec.edmcouncil.org/fibo/ontology/PAY/PaymentServices/PaymentServices/",
        "gleif-L1": "https://www.gleif.org/ontology/L1/",
        "gs1": "https://ref.gs1.org/voc/",
        "lcc-cr": "https://www.omg.org/spec/LCC/Countries/CountryRepresentation/",
        "unece": "http://unece.org/vocab#",
        "vcard": "http://www.w3.org/2006/vcard/ns#",
        "bibo": "http://purl.org/ontology/bibo/",
        "sarif": "http://sarif.info/",
        "lrmoo": "http://iflastandards.info/ns/lrm/lrmoo/",
        "snomed": "http://purl.bioontology.org/ontology/SNOMEDCT/",
        "eli": "http://data.europa.eu/eli/ontology#",
        "prov": "http://www.w3.org/ns/prov#",
        "hydra": "http://www.w3.org/ns/hydra/core#",
        "mo": "http://purl.org/ontology/mo/",
        "og": "http://ogp.me/ns#",
    }
    prefix: str
    uri: str
    for prefix, uri in namespaces.items():
        graph.bind(prefix, uri)


class _TermAccumulator:
    """Temporary holder to accumulate term information."""

    def __init__(self, term_id: str) -> None:
        self.id: str = term_id
        self.types: List[rdflib.URIRef] = []
        self.sups: List[rdflib.URIRef] = []
        self.label: Optional[str] = None
        self.layer: Optional[str] = None
        self.type: Optional[rdflib.URIRef] = None

    def appendRow(self, row: rdflib.query.ResultRow) -> None:
        self.types.append(row.type)
        self.sups.append(row.sup)
        self.type = row.type
        self.label = str(row.label)
        self.layer = layerFromUri(str(row.layer))


def _loadOneSourceGraph(file_path: Union[str, Path]) -> rdflib.Graph:
    """Load the content of one source file."""
    path: Path = Path(file_path)
    formats: Dict[str, str] = {".nt": "nt", ".ttl": "turtle"}
    file_format: Optional[str] = formats.get(path.suffix)
    if not file_format:
        raise NotImplementedError(f"Unsupported file format: {path.suffix}")
    try:
        graph: rdflib.Graph = rdflib.Graph()
        graph.parse(source=str(path), format=file_format)
        return graph
    except Exception as e:
        message: str = f"Error parsing source file '{file_path}': {e}"
        log.warning(message)
        raise IOError(message) from e


class SdoTermSource:
    """This class acts as the source of information for terms."""

    TYPE: str = "Class"
    TERMCOUNTS: Optional[Dict[Union[sdoterm.SdoTermType, str], int]] = None

    SOURCEGRAPH: Optional[rdflib.Graph] = None
    MARKDOWNPROCESS: bool = True
    EXPANDEDTERMS: Dict[str, Any] = {}
    TERMS: Dict[str, Any] = {}

    TERMSLOCK: threading.Lock = threading.Lock()
    RDFLIBLOCK: threading.Lock = threading.Lock()
    LOADEDDEFAULT: bool = False

    def __init__(self, uri: str, ttype: Optional[Union[rdflib.URIRef, str]] = None, label: str = "", layer: Optional[str] = None) -> None:
        term_id: str = uri2id(uri)
        self.layer: str = layer or CORE
        self.termdesc: Any = None

        self.parent: Optional[sdoterm.SdoTerm] = None
        self.checkedDataTypeParents: bool = False
        self.supersededBy: Optional[str] = None
        self.supersedes: Optional[List[str]] = None
        self.supers: Optional[List[str]] = None
        self.termStack: Optional[List[sdoterm.SdoTerm]] = None
        self.subs: Optional[List[str]] = None
        self.members: Optional[List[str]] = None
        self.props: Optional[List[str]] = None
        self.propUsedOn: Optional[List[str]] = None
        self.ranges: Optional[List[str]] = None
        self.domains: Optional[List[str]] = None
        self.targetOf: Optional[List[str]] = None
        self.equivalents: Optional[List[str]] = None
        self.gotinverseOf: bool = False
        self.inverseOf: Optional[str] = None
        self.comments: Optional[Sequence[str]] = None
        self.comment: Optional[str] = None
        self.srcacks: Optional[List[Any]] = None
        self.sources: Optional[List[str]] = None
        self.acks: Optional[Sequence[sdocollaborators.collaborator]] = None
        self.examples: Optional[List[Any]] = None
        global DATATYPEURI, ENUMERATIONURI
        cls: Type[SdoTermSource] = self.__class__
        self.ttype: sdoterm.SdoTermType
        if ttype == rdflib.RDFS.Class:
            self.ttype = sdoterm.SdoTermType.TYPE
            if uri == str(DATATYPEURI):
                self.ttype = sdoterm.SdoTermType.DATATYPE
            elif uri == str(ENUMERATIONURI):
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

            if self.parent:
                if self.parent.termType == sdoterm.SdoTermType.ENUMERATION:
                    self.ttype = sdoterm.SdoTermType.ENUMERATIONVALUE
                elif self.parent.termType == sdoterm.SdoTermType.DATATYPE:
                    self.ttype = sdoterm.SdoTermType.DATATYPE
                else:
                    self.ttype = sdoterm.SdoTermType.REFERENCE
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
        self.termdesc.superPaths = self.getParentPaths()

        if self.ttype in sdoterm.SdoTerm.TYPE_LIKE_TYPES:
            self.termdesc.properties.setIds(self.getProperties(getall=False))
            self.termdesc.allproperties.setIds(self.getProperties(getall=True))
            self.termdesc.expectedTypeFor.setIds(self.getTargetOf())
            if self.ttype == sdoterm.SdoTermType.ENUMERATION:
                if not self.termdesc.properties:
                    self.termdesc.termStack.clear()
                self.termdesc._enumerationMembers.setIds(self.getEnumerationMembers())
        elif self.ttype == sdoterm.SdoTermType.PROPERTY:
            self.termdesc.domainIncludes.setIds(self.getDomains())
            self.termdesc.rangeIncludes.setIds(self.getRanges())
            self.termdesc.inverse.setId(self.getInverseOf())
        elif self.ttype == sdoterm.SdoTermType.REFERENCE:
            self.termdesc.label = prefixedIdFromUri(uri)
            self.termdesc.comment = self.getComment()

        cls.TERMS[uri] = self.termdesc

    def __str__(self) -> str:
        return f"<SdoTermSource: {self.ttype} '{self.id}'>"

    @property
    def id(self) -> str:
        assert self.termdesc is not None
        return self.termdesc.id

    @property
    def uri(self) -> str:
        assert self.termdesc is not None
        return self.termdesc.uri

    def getTermdesc(self) -> sdoterm.SdoTerm:
        assert self.termdesc is not None
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
            sup_id: str
            for sup_id in self.getSupers():
                sup: Optional[sdoterm.SdoTerm] = self.__class__.getTerm(sup_id)
                if sup and sup.termType == sdoterm.SdoTermType.DATATYPE:
                    self.ttype = sdoterm.SdoTermType.DATATYPE
                    return True
        return False

    @classmethod
    def _isEnumeration(cls, term_id: str) -> bool:
        global ENUMERATIONURI
        query: str = """
          ASK  {
                    %s rdfs:subClassOf* %s.
            }""" % (uriWrap(toFullId(term_id)), uriWrap(str(ENUMERATIONURI)))

        result: Sequence[rdflib.query.ResultRow] = cls.query(query)
        return bool(result[-1])

    def _isEnumerationValue(self) -> bool:
        return self.ttype == sdoterm.SdoTermType.ENUMERATIONVALUE

    def isReference(self) -> bool:
        return self.ttype == sdoterm.SdoTermType.REFERENCE

    def getParent(self) -> Optional[sdoterm.SdoTerm]:
        return self.parent

    def getPrefixedId(self) -> str:
        return prefixedIdFromUri(self.uri)

    def getComments(self) -> Sequence[str]:
        if not self.comments:
            self.comments = tuple(map(str, self.loadObjects(rdflib.RDFS.comment)))
        return self.comments

    def getComment(self) -> str:
        if not self.comment:
            self.loadComment()
        assert self.comment is not None
        return self.comment

    def getSupersededBy(self) -> str:
        if not self.supersededBy:
            ss: List[rdflib.term.Node] = self.loadObjects("schema:supersededBy")
            tmp: List[str] = [t for s in ss if (t := uri2id(str(s)))]

            if len(tmp) > 1:
                log.debug(
                    f"Warning '{self.id}' supersededBy more than 1 term ({len(tmp)})"
                )
            self.supersededBy = tmp[0] if tmp else ""
        return self.supersededBy

    def superseded(self) -> bool:
        return bool(self.getSupersededBy())

    def getSupersedes(self) -> List[str]:
        if not self.supersedes:
            subs: List[rdflib.term.Node] = self.loadSubjects("schema:supersededBy")
            self.supersedes = sorted(uri2id(str(sub)) for sub in subs)
        return self.supersedes

    def getSources(self) -> List[str]:
        if not self.sources:
            objs: List[rdflib.term.Node] = self.loadObjects("schema:source")
            self.sources = sorted(str(o) for o in objs)
        return self.sources

    def getAcknowledgements(self) -> Sequence[sdocollaborators.collaborator]:
        if not self.acks:
            acks: List[sdocollaborators.collaborator] = []
            objs: List[rdflib.term.Node] = self.loadObjects("schema:contributor")
            obj: rdflib.term.Node
            for obj in objs:
                if obj:
                    cont: Optional[sdocollaborators.collaborator] = sdocollaborators.collaborator.getContributor(str(obj))
                    if cont:
                        acks.append(cont)
            self.acks = sorted(acks, key=lambda t: t.title or "")
        return self.acks

    def getLayer(self) -> str:
        return self.layer

    def getInverseOf(self) -> Optional[str]:
        if not self.gotinverseOf:
            self.gotinverseOf = True
            inverse: Optional[Any] = self.loadValue("schema:inverseOf")
            if inverse:
                self.inverseOf = uri2id(str(inverse))
        return self.inverseOf

    def getSupers(self) -> List[str]:
        if not self.supers:
            self.loadsupers()
        assert self.supers is not None
        return self.supers

    def getTermStack(self) -> List[sdoterm.SdoTerm]:
        if not self.termStack:
            self.termStack = []
            sup_id: str
            for sup_id in self.getSupers():
                try:
                    s: Optional[sdoterm.SdoTerm] = self.__class__._getTerm(sup_id, createReference=True)
                    if not s or s.termType == sdoterm.SdoTermType.REFERENCE:
                        continue
                    self.termStack.append(s)
                    if s.termStack:
                        self.termStack.extend(s.termStack.terms)
                except RecursionError as e:
                    assert self.termdesc is not None
                    e.add_note(f"Circular references with {self.termdesc}")
                    raise
            stack: List[sdoterm.SdoTerm] = []
            t: sdoterm.SdoTerm
            for t in reversed(self.termStack):
                if t not in stack:
                    stack.append(t)
            self.termStack = list(reversed(stack))
        return self.termStack

    def getSubs(self) -> List[str]:
        if not self.subs:
            self.loadsubs()
        assert self.subs is not None
        return self.subs

    def getProperties(self, getall: bool = False) -> List[str]:
        if not self.props:
            subs: List[rdflib.term.Node] = self.loadSubjects("schema:domainIncludes")
            self.props = sorted(uri2id(str(sub)) for sub in subs)
        ret: List[str] = self.props

        if getall:
            allprop_ids: Set[str] = set(self.props)
            t: sdoterm.SdoTerm
            for t in self.getTermStack():
                term: sdoterm.SdoTerm = t if isinstance(t, sdoterm.SdoTerm) else self.__class__._getTerm(t, createReference=True)
                if term.id != self.id:
                    if term.id == "ENUMERATION":
                        break
                    if term.termType in sdoterm.SdoTerm.TYPE_LIKE_TYPES:
                        allprop_ids.update(term.properties.ids)
            ret = sorted(allprop_ids)
        return ret

    def getPropUsedOn(self) -> List[str]:
        raise NotImplementedError("Not implemented yet")

    def getRanges(self) -> List[str]:
        if not self.ranges:
            objs: List[rdflib.term.Node] = self.loadObjects("schema:rangeIncludes")
            self.ranges = sorted(uri2id(str(obj)) for obj in objs)
        return self.ranges

    def getDomains(self) -> List[str]:
        if not self.domains:
            objs: List[rdflib.term.Node] = self.loadObjects("schema:domainIncludes")
            self.domains = sorted(uri2id(str(obj)) for obj in objs)
        return self.domains

    def getTargetOf(self, plusparents: bool = False, stopontarget: bool = False) -> List[str]:
        global ENUMERATIONURI, THINGURI
        if not self.targetOf:
            subs: List[rdflib.term.Node] = self.loadSubjects("schema:rangeIncludes")
            self.targetOf = sorted(uri2id(str(sub)) for sub in subs)
        ret: List[str] = self.targetOf
        if not (self.targetOf and stopontarget):
            if plusparents:
                targets: Set[str] = set(self.targetOf)
                s: str
                for s in self.getSupers():
                    sup: Optional[sdoterm.SdoTerm] = self.__class__._getTerm(s, createReference=True)
                    if not sup or sup.uri in (str(ENUMERATIONURI), str(THINGURI)):
                        break
                    targets.update(sup.expectedTypeFor.ids)
                    if targets and stopontarget:
                        break
                ret = sorted(targets)
        return ret

    def getEquivalents(self) -> List[str]:
        if not self.equivalents:
            equivalents: List[rdflib.term.Node] = self.loadObjects("owl:equivalentClass")
            equivalents.extend(self.loadObjects("owl:equivalentProperty"))
            self.equivalents = sorted((str(e) for e in equivalents), key=prefixedIdFromUri)
        return self.equivalents

    def inLayers(self, layers: Union[str, Iterable[str]]) -> bool:
        if isinstance(layers, str):
            return self.layer == layers
        return self.layer in layers

    def getExtLayer(self) -> str:
        return self.layer if self.layer and self.layer != CORE else ""

    @classmethod
    def subClassOf(cls, child: Union[str, sdoterm.SdoTerm], parent: Union[str, sdoterm.SdoTerm]) -> bool:
        child_obj: Optional[sdoterm.SdoTerm] = cls.getTerm(child) if isinstance(child, str) else child
        parent_obj: Optional[sdoterm.SdoTerm] = cls.getTerm(parent) if isinstance(parent, str) else parent

        if child_obj == parent_obj:
            return True
        if not child_obj:
            return False

        parents: Tuple[str, ...] = child_obj.supers.ids
        if parent_obj and parent_obj.id in parents:
            return True

        return any(cls.subClassOf(p, parent_obj) for p in parents) if parent_obj else False

    def loadComment(self) -> None:
        comments: Sequence[str] = self.getComments()
        wpre: Optional[str] = None
        assert self.termdesc is not None
        name: str = self.termdesc.id
        if name.startswith("http:"):
            val: str = Path(name).name
            wpre = name[: -len(val)]

        comment_buffer: List[str]
        if self.__class__.MARKDOWNPROCESS:
            comment_buffer = [
                localmarkdown.Markdown.parse(comment, wpre=wpre) for comment in comments
            ]
        else:
            comment_buffer = list(comments)
        self.comment = " ".join(comment_buffer).strip()

    def loadValue(self, valType: str) -> Optional[Any]:
        ret: List[rdflib.term.Node] = self.loadObjects(valType)
        return ret[0] if ret else None

    def loadObjects(self, pred: Union[rdflib.URIRef, str]) -> List[rdflib.term.Node]:
        query: str = """
        SELECT ?val WHERE {
                %s %s ?val.
         }""" % (uriWrap(toFullId(self.id)), uriWrap(str(pred)))
        res: Sequence[rdflib.query.ResultRow] = self.__class__.query(query)
        return [row.val for row in res]

    def loadSubjects(self, pred: Union[rdflib.URIRef, str]) -> List[rdflib.term.Node]:
        query: str = """
        SELECT ?sub WHERE {
                ?sub %s %s.
         }""" % (uriWrap(str(pred)), uriWrap(toFullId(self.id)))
        res: Sequence[rdflib.query.ResultRow] = self.__class__.query(query)
        return [row.sub for row in res]

    def loadsupers(self) -> None:
        fullId: str = toFullId(self.id)
        query: str = """
        SELECT ?sup WHERE {
             {
                 %s rdfs:subClassOf ?sup .
             }UNION{
                 %s rdfs:subPropertyOf ?sup .
             }
         }
         ORDER BY ?sup""" % (uriWrap(fullId), uriWrap(fullId))

        res: Sequence[rdflib.query.ResultRow] = self.__class__.query(query)
        self.supers = sorted(uri2id(str(row.sup)) for row in res)

    def loadsubs(self) -> None:
        fullId: str = toFullId(self.id)
        sel: str = "rdfs:subClassOf" if self.ttype in sdoterm.SdoTerm.TYPE_LIKE_TYPES else "rdfs:subPropertyOf"
        query: str = """
        SELECT ?sub WHERE {
                ?sub %s %s.
         }ORDER BY ?sub""" % (uriWrap(sel), uriWrap(fullId))
        res: Sequence[rdflib.query.ResultRow] = self.__class__.query(query)
        self.subs = [uri2id(str(row.sub)) for row in res]

        if self.ttype == sdoterm.SdoTermType.DATATYPE:
            subjects: List[rdflib.term.Node] = self.loadSubjects("a")
            self.subs.extend(uri2id(str(child)) for child in subjects)
        self.subs.sort()

    def getEnumerationMembers(self) -> Optional[List[str]]:
        if not self.members and self.ttype == sdoterm.SdoTermType.ENUMERATION:
            subjects: List[rdflib.term.Node] = self.loadSubjects("a")
            self.members = sorted(uri2id(str(child)) for child in subjects)
        return self.members

    def getParentPaths(self, cstack: Optional[List[str]] = None) -> List[List[str]]:
        self._pstacks: List[List[str]] = []
        cstack_list: List[str] = cstack or []
        self._pstacks.append(cstack_list)
        assert self.termdesc is not None
        self._getParentPaths(self.termdesc, cstack_list)

        inserts: List[str] = []
        if self.ttype == sdoterm.SdoTermType.PROPERTY:
            inserts = ["Property", "Thing"]
        elif self.ttype == sdoterm.SdoTermType.DATATYPE and self.id != "DataType":
            inserts = ["DataType"]
        elif self.ttype == sdoterm.SdoTermType.TYPE:
            base: str = self._pstacks[0][0]
            basetype: Optional[sdoterm.SdoTerm] = self.termdesc if base == self.id else self.__class__._getTerm(base)
            if basetype and basetype.termType == sdoterm.SdoTermType.DATATYPE:
                inserts = ["DataType"]

        ins: str
        s: List[str]
        for ins in inserts:
            for s in self._pstacks:
                s.insert(0, ins)

        return self._pstacks

    def _getParentPaths(self, term: sdoterm.SdoTerm, cstack: List[str]) -> None:
        cstack.insert(0, term.id)
        tmpStacks: List[List[str]] = [cstack]
        super_ids: List[str] = list(term.supers.ids)

        if (
            term.termType == sdoterm.SdoTermType.ENUMERATIONVALUE
            and term.enumerationParent
            and term.enumerationParent.id not in super_ids
        ):
            assert term.enumerationParent.id is not None
            super_ids.append(term.enumerationParent.id)

        if super_ids:
            i: int
            for i in range(1, len(super_ids)):
                t: List[str] = cstack[:]
                tmpStacks.append(t)
                self._pstacks.append(t)

            x: int
            parent_id: str
            for x, parent_id in enumerate(super_ids):
                if not (parent_id.startswith("http:") or parent_id.startswith("https:")):
                    sup: Optional[sdoterm.SdoTerm] = self.__class__._getTerm(parent_id)
                    if sup:
                        self._getParentPaths(sup, tmpStacks[x])

    @classmethod
    def getParentPathTo(cls, start_term_id: str, end_term_id: Optional[str] = None) -> List[List[str]]:
        end_term_id = end_term_id or "Thing"
        start_term: Optional[sdoterm.SdoTerm] = cls.getTerm(start_term_id, expanded=True)
        if not start_term:
            return []
        return [list(path) for path in start_term.superPaths if end_term_id in path]

    def checkForEnumVal(self) -> bool:
        if self.ttype == sdoterm.SdoTermType.ENUMERATION:
            return True

        sup_id: str
        return any(
            (sup_term := self.__class__.getTerm(sup_id)) and sup_term.checkForEnumVal()
            for sup_id in self.getSupers()
        )

    @classmethod
    def expandTerms(cls, terms: Iterable[sdoterm.SdoTerm], depth: int = 2) -> List[sdoterm.SdoTerm]:
        return [cls.expandTerm(t, depth=depth) for t in terms]

    @classmethod
    def expandTerm(cls, termdesc: sdoterm.SdoTerm, depth: int = 2) -> sdoterm.SdoTerm:
        """Expand a term, e.g. expand the properties that only contain term-ids to contain actual SdoTerm instances."""
        assert isinstance(termdesc, sdoterm.SdoTerm), termdesc
        if termdesc.expanded() or depth < 1:
            return termdesc

        termdesc.markExpanded(depth)

        termdesc.superPaths = [
            sdoterm.SdoTermSequence.forElements(paths) for paths in termdesc.superPaths
        ]
        termdesc.termStack.setTerms(cls.termsFromIds(termdesc.termStack.ids))
        termdesc.supers.setTerms(cls.termsFromIds(termdesc.supers.ids))
        termdesc.subs.setTerms(cls.termsFromIds(termdesc.subs.ids))
        termdesc.equivalents.setTerms(cls.termsFromIds(termdesc.equivalents.ids))

        if termdesc.termType in sdoterm.SdoTerm.TYPE_LIKE_TYPES:
            if depth > 1:
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
            if termdesc.inverse.id:
                termdesc.inverse.setTerm(cls.termFromId(termdesc.inverse.id))
        elif termdesc.termType == sdoterm.SdoTermType.ENUMERATIONVALUE:
            if termdesc.enumerationParent.id:
                termdesc.enumerationParent.setTerm(
                    cls.termFromId(termdesc.enumerationParent.id)
                )

        if depth > 0:
            termdesc.termStack.setTerms(
                cls.expandTerms(
                    cls.termsFromIds(termdesc.termStack.ids), depth=depth - 1
                )
            )

        return termdesc

    @classmethod
    def termFromId(cls, id: str = "") -> Optional[sdoterm.SdoTerm]:
        if not id:
            return None
        ids: Sequence[sdoterm.SdoTerm] = cls.termsFromIds([id])
        return ids[0] if ids else None

    @classmethod
    def termsFromIds(
        cls, ids: Optional[Sequence[Union[str, sdoterm.SdoTerm]]] = None
    ) -> Sequence[sdoterm.SdoTerm]:
        """Convert a sequence of term-identities into a sequence of SdoTerms."""
        id_list: Sequence[Union[str, sdoterm.SdoTerm]] = ids or []
        ret: List[sdoterm.SdoTerm] = []
        tid: Union[str, sdoterm.SdoTerm]
        for tid in id_list:
            if tid:
                if isinstance(tid, str):
                    term: Optional[sdoterm.SdoTerm] = cls._getTerm(tid, createReference=True)
                    if term:
                        ret.append(term)
                else:
                    ret.append(tid)
        return ret

    @classmethod
    def _singleTermFromResult(
        cls, res: Sequence[rdflib.query.ResultRow], termId: str
    ) -> Optional[sdoterm.SdoTerm]:
        """Return a single term matching `termId` from res."""
        tmp: _TermAccumulator = _TermAccumulator(termId)
        row: rdflib.query.ResultRow
        for row in res:
            tmp.appendRow(row)

        return cls._createTerm(tmp)

    @classmethod
    def termsFromResults(
        cls, res: Sequence[rdflib.query.ResultRow]
    ) -> Sequence[sdoterm.SdoTerm]:
        rows_by_term_id: Dict[str, _TermAccumulator] = {}
        row: rdflib.query.ResultRow
        for row in res:
            key: str = str(row.term)
            if key not in rows_by_term_id:
                rows_by_term_id[key] = _TermAccumulator(key)
            rows_by_term_id[key].appendRow(row)

        acc: _TermAccumulator
        return [t for acc in rows_by_term_id.values() if (t := cls._createTerm(acc))]

    @classmethod
    def _createTerm(cls, tmp: _TermAccumulator) -> Optional[sdoterm.SdoTerm]:
        global DATATYPEURI, ENUMERATIONURI
        if not tmp or not tmp.id:
            return None

        if DATATYPEURI in tmp.types:
            tmp.type = DATATYPEURI
        elif ENUMERATIONURI in tmp.sups:
            tmp.type = ENUMERATIONURI
        elif tmp.types and len(tmp.types) > 1:
            tmp.type = sorted(tmp.types)[0]

        term: Optional[sdoterm.SdoTerm] = cls.TERMS.get(tmp.id)
        if not term:
            t: SdoTermSource = cls(tmp.id, ttype=tmp.type, label=tmp.label or "", layer=tmp.layer)
            term = t.termdesc
        return term

    @classmethod
    def triples4Term(cls, termId: str) -> Iterable[Tuple[rdflib.term.Node, rdflib.term.Node, rdflib.term.Node]]:
        term: Optional[sdoterm.SdoTerm] = cls.getTerm(termId)
        g: Optional[rdflib.Graph] = cls.SOURCEGRAPH
        if not term or not g:
            return []
        return g.triples((rdflib.URIRef(term.uri), None, None))

    @classmethod
    def getTermAsRdfString(cls, termId: str, output_format: str, full: bool = False) -> str:
        global VOCABURI
        term: Optional[sdoterm.SdoTerm] = cls.getTerm(termId)
        if not term or term.termType == sdoterm.SdoTermType.REFERENCE:
            return ""
        g: rdflib.Graph = rdflib.Graph()
        assert VOCABURI is not None
        g.bind("schema", VOCABURI)

        trip: Tuple[rdflib.term.Node, rdflib.term.Node, rdflib.term.Node]
        if not full:
            for trip in cls.triples4Term(term.id):
                g.add(trip)
        else:
            types: List[sdoterm.SdoTerm] = []
            props: List[sdoterm.SdoTerm] = []
            stack: List[sdoterm.SdoTerm] = [term]

            stack.extend(cls.termsFromIds(term.termStack.ids))
            t: sdoterm.SdoTerm
            for t in stack:
                if t.termType == sdoterm.SdoTermType.PROPERTY:
                    props.append(t)
                else:
                    types.append(t)
                    if t.termType == sdoterm.SdoTermType.ENUMERATIONVALUE:
                        e_parent: Optional[sdoterm.SdoTerm] = cls.termFromId(t.enumerationParent.id or "")
                        if e_parent:
                            types.append(e_parent)
                    elif t == stack[0]:
                        props.extend(cls.termsFromIds(t.allproperties.ids))

            for t in sorted(types):
                if t:
                    for trip in cls.triples4Term(t.id):
                        g.add(trip)

            p: sdoterm.SdoTerm
            for p in sorted(props):
                if p:
                    for trip in cls.triples4Term(p.id):
                        g.add(trip)

        if output_format == "rdf":
            output_format = "pretty-xml"

        ret: Union[str, bytes] = g.serialize(format=output_format, auto_compact=True, sort_keys=True, max_depth=1)

        if output_format == "json-ld":
            try:
                data: Any = json.loads(ret)
                return json.dumps(sort_dict(data), indent=2)
            except Exception:
                pass
        return str(ret)

    @classmethod
    def getAllTypes(cls, layer: Optional[str] = None, expanded: bool = False) -> Sequence[Union[str, sdoterm.SdoTerm]]:
        return cls.getAllTerms(
            ttype=sdoterm.SdoTermType.TYPE, layer=layer, expanded=expanded
        )

    @classmethod
    def getAllProperties(cls, layer: Optional[str] = None, expanded: bool = False) -> Sequence[Union[str, sdoterm.SdoTerm]]:
        return cls.getAllTerms(
            ttype=sdoterm.SdoTermType.PROPERTY, layer=layer, expanded=expanded
        )

    @classmethod
    def getAllEnumerations(cls, layer: Optional[str] = None, expanded: bool = False) -> Sequence[Union[str, sdoterm.SdoTerm]]:
        return cls.getAllTerms(
            ttype=sdoterm.SdoTermType.ENUMERATION, layer=layer, expanded=expanded
        )

    @classmethod
    def getAllEnumerationvalues(cls, layer: Optional[str] = None, expanded: bool = False) -> Sequence[Union[str, sdoterm.SdoTerm]]:
        return cls.getAllTerms(
            ttype=sdoterm.SdoTermType.ENUMERATIONVALUE, layer=layer, expanded=expanded
        )

    @classmethod
    def getAllTerms(
        cls, ttype: Optional[sdoterm.SdoTermType] = None, layer: Optional[str] = None, suppressSourceLinks: bool = False, expanded: bool = False
    ) -> Sequence[Union[str, sdoterm.SdoTerm]]:
        with pretty_logger.BlockLog(
            logger=log, message="GetAllTerms", timing=True
        ) as block:
            global DATATYPEURI, ENUMERATIONURI
            typsel: str = ""
            extra: str = ""
            if ttype == sdoterm.SdoTermType.TYPE:
                typsel = f"a <{rdflib.RDFS.Class}>;"
            elif ttype == sdoterm.SdoTermType.PROPERTY:
                typsel = f"a <{rdflib.RDF.Property}>;"
            elif ttype == sdoterm.SdoTermType.DATATYPE:
                typsel = f"a <{DATATYPEURI}>;"
            elif ttype == sdoterm.SdoTermType.ENUMERATION:
                typsel = f"rdfs:subClassOf* <{ENUMERATIONURI}>;"
            elif ttype == sdoterm.SdoTermType.ENUMERATIONVALUE:
                extra = f"?type rdfs:subClassOf*  <{ENUMERATIONURI}>."
            elif not ttype:
                typsel = ""
            else:
                log.debug(f"Invalid type value '{ttype}'")

            laysel: str = ""
            fil: str = ""
            suppress: str = ""
            if layer:
                if layer == "core":
                    fil = "FILTER NOT EXISTS { ?term schema:isPartOf ?x. }"
                else:
                    laysel = f"schema:isPartOf <{uriFromLayer(layer)}>; "

            if suppressSourceLinks:
                suppress = "FILTER NOT EXISTS { ?s dc:source ?term. }"

            query: str = f"""SELECT DISTINCT ?term ?type ?label ?layer ?sup WHERE {{
                 ?term a ?type;
                    {typsel}
                    {laysel}
                    rdfs:label ?label.
                {extra}
                OPTIONAL {{
                    ?term schema:isPartOf ?layer.
                }}
                OPTIONAL {{
                    ?term rdfs:subClassOf ?sup.
                }}
                OPTIONAL {{
                    ?term rdfs:subPropertyOf ?sup.
                }}
                {fil}
                {suppress}
            }}
            ORDER BY ?term
            """

            log.debug(f"query {query}")
            res: Sequence[rdflib.query.ResultRow] = cls.query(query)
            log.debug(f"res {len(res)}")

            terms: List[Union[str, sdoterm.SdoTerm]] = []
            if expanded:
                with pretty_logger.BlockLog(
                    logger=log, message=f"Expanding {len(res)} terms", timing=True
                ):
                    terms = list(cls.termsFromResults(res))
            else:
                seen: Set[str] = set()
                row: rdflib.query.ResultRow
                for row in res:
                    term_id: str = uri2id(str(row.term))
                    if term_id not in seen:
                        terms.append(term_id)
                        seen.add(term_id)
            block.message = f"GetAllTerms: {len(terms)} terms, total: {len(cls.TERMS)}"
            return terms

    @classmethod
    def getAcknowledgedTerms(cls, ack: str) -> Sequence[sdoterm.SdoTerm]:
        query: str = f"""SELECT DISTINCT ?term ?type ?label ?layer ?sup WHERE {{
             ?term a ?type;
                schema:contributor <{ack}>;
                rdfs:label ?label.
                OPTIONAL {{
                    ?term schema:isPartOf ?layer.
                }}
                OPTIONAL {{
                    ?term rdfs:subClassOf ?sup.
                }}
                OPTIONAL {{
                    ?term rdfs:subPropertyOf ?sup.
                }}
            }}
            ORDER BY ?term
            """
        res: Sequence[rdflib.query.ResultRow] = cls.query(query)
        return cls.termsFromResults(res)

    @classmethod
    def setSourceGraph(cls, g: rdflib.graph.Graph) -> None:
        global VOCABURI
        cls.SOURCEGRAPH = g
        if VOCABURI:
            g.bind("schema", VOCABURI)
        bindNameSpaces(g)

        cls.TERMS = {}
        cls.EXPANDEDTERMS = {}

    @classmethod
    def loadSourceGraph(
        cls, files: Optional[Union[str, Iterable[str]]] = None, init: bool = False, vocaburi: Optional[str] = None
    ) -> None:
        global VOCABURI, DEFTRIPLESFILESGLOB
        if init:
            cls.SOURCEGRAPH = None
        if not VOCABURI and not vocaburi:
            cls.setVocabUri(DEFVOCABURI)
        elif vocaburi:
            cls.setVocabUri(vocaburi)

        load_files: List[str] = []
        if not files or files == "default":
            if cls.SOURCEGRAPH:
                if not cls.LOADEDDEFAULT:
                    raise Exception("Sourcegraph already loaded - cannot overwrite with defaults")
                log.info("Default files already loaded")
                return

            cls.LOADEDDEFAULT = True
            log.info(
                f"SdoTermSource.loadSourceGraph() loading from default files found in globs: {','.join(DEFTRIPLESFILESGLOB)}",
            )
            g: str
            for g in DEFTRIPLESFILESGLOB:
                load_files.extend(sorted(glob.glob(g)))
        elif isinstance(files, str):
            cls.LOADEDDEFAULT = False
            log.info(f"SdoTermSource.loadSourceGraph() loading from file: {files}")
            load_files = [files]
        else:
            cls.LOADEDDEFAULT = False
            log.info(f"SdoTermSource.loadSourceGraph() loading from {len(files)} files")
            load_files = list(files)

        if not load_files:
            raise Exception("No triples file(s) to load")

        cls.setSourceGraph(rdflib.Graph())
        file_path: str
        for file_path in load_files:
            assert cls.SOURCEGRAPH is not None
            cls.SOURCEGRAPH += _loadOneSourceGraph(file_path)
        log.info(
            f"Done: Loaded {len(cls.sourceGraph())} triples - {len(cls.getAllTerms())} terms",
        )

    @classmethod
    def sourceGraph(cls) -> rdflib.Graph:
        if cls.SOURCEGRAPH is None:
            cls.loadSourceGraph()
        assert cls.SOURCEGRAPH is not None
        return cls.SOURCEGRAPH

    @staticmethod
    def setVocabUri(uri: Optional[str] = None) -> None:
        global VOCABURI, DATATYPEURI, ENUMERATIONURI, THINGURI
        VOCABURI = uri or DEFVOCABURI
        DATATYPEURI = rdflib.URIRef(f"{VOCABURI}DataType")
        ENUMERATIONURI = rdflib.URIRef(f"{VOCABURI}Enumeration")
        THINGURI = rdflib.URIRef(f"{VOCABURI}Thing")

    @classmethod
    def vocabUri(cls) -> str:
        global VOCABURI
        if not VOCABURI:
            cls.setVocabUri()
        assert VOCABURI is not None
        return VOCABURI

    @classmethod
    def query(cls, query_string: str) -> Sequence[rdflib.query.ResultRow]:
        graph: rdflib.Graph = cls.sourceGraph()
        with cls.RDFLIBLOCK:
            result: Sequence[rdflib.query.ResultRow] = tuple(graph.query(query_string))
        return result

    @classmethod
    def termCounts(cls) -> Dict[Union[sdoterm.SdoTermType, str], int]:
        global VOCABURI
        if not cls.TERMCOUNTS:
            def run_count_query(q: str) -> int:
                res: Sequence[rdflib.query.ResultRow] = cls.query(q)
                return int(res[0][0])

            allterms: int = run_count_query(f'SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {{ ?s a ?type . FILTER (strStarts(str(?s),"{VOCABURI}")) }}')
            classes: int = run_count_query(f'SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {{ ?s a rdfs:Class . FILTER (strStarts(str(?s),"{VOCABURI}")) }}')
            properties: int = run_count_query(f'SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {{ ?s a rdf:Property . FILTER (strStarts(str(?s),"{VOCABURI}")) }}')
            enums: int = run_count_query(f'SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {{ ?s rdfs:subClassOf* schema:Enumeration . FILTER (strStarts(str(?s),"{VOCABURI}")) }}')
            enumvals: int = run_count_query(f'SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {{ ?s a ?type . ?type rdfs:subClassOf* schema:Enumeration . FILTER (strStarts(str(?s),"{VOCABURI}")) }}')
            datatypes: int = run_count_query(f'SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {{ {{ ?s a schema:DataType . }}UNION{{ ?s rdf:type* schema:DataType . }}UNION{{ ?s rdfs:subClassOf* ?x . ?x a schema:DataType . }} FILTER (strStarts(str(?s),"{VOCABURI}")) }}')
            datatypeclasses: int = run_count_query(f'SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {{ ?s rdfs:subClassOf* ?x . ?x a schema:DataType . FILTER (strStarts(str(?s),"{VOCABURI}")) }}')

            types: int = classes - 1 - enums - datatypeclasses
            datatypes -= 1

            cls.TERMCOUNTS = {
                sdoterm.SdoTermType.TYPE: types,
                sdoterm.SdoTermType.PROPERTY: properties,
                sdoterm.SdoTermType.DATATYPE: datatypes,
                sdoterm.SdoTermType.ENUMERATION: enums,
                sdoterm.SdoTermType.ENUMERATIONVALUE: enumvals,
                "All": types + properties + datatypes + enums + enumvals
            }
        return cls.TERMCOUNTS

    @classmethod
    def setMarkdownProcess(cls, process: bool) -> None:
        cls.MARKDOWNPROCESS = process

    @classmethod
    def termCache(cls) -> Dict[str, sdoterm.SdoTerm]:
        return cls.TERMS

    @classmethod
    def getTerm(
        cls,
        termId: str,
        expanded: bool = False,
        refresh: bool = False,
        createReference: bool = False,
    ) -> Optional[sdoterm.SdoTerm]:
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
    ) -> Optional[sdoterm.SdoTerm]:
        if not termId:
            return None
        assert isinstance(termId, str), termId
        termId = termId.strip()
        fullId: str = toFullId(termId)
        term: Optional[sdoterm.SdoTerm] = cls.TERMS.get(fullId)

        if term and refresh:
            del cls.TERMS[fullId]
            log.info(f"Term '{termId}' found and removed")
            term = None

        if not term:
            query: str = f"""
            SELECT ?term ?type ?label ?layer ?sup WHERE {{
                 {uriWrap(fullId)} a ?type;
                    rdfs:label ?label.
                OPTIONAL {{ {uriWrap(fullId)} schema:isPartOf ?layer. }}
                OPTIONAL {{ {uriWrap(fullId)} rdfs:subClassOf ?sup. }}
                OPTIONAL {{ {uriWrap(fullId)} rdfs:subPropertyOf ?sup. }}
            }}"""
            res: Sequence[rdflib.query.ResultRow] = cls.query(query)
            if res:
                term = cls._singleTermFromResult(res, termId=fullId)
            elif createReference:
                term = cls(fullId).getTermdesc()
            else:
                log.warning(f"No definition of term {fullId}")

        if term and expanded and not term.expanded():
            if fullId not in cls.EXPANDEDTERMS:
                cls.EXPANDEDTERMS[fullId] = cls.expandTerm(term)
            term = cls.EXPANDEDTERMS[fullId]

        return term


def toFullId(termId: str) -> str:
    global VOCABURI
    assert VOCABURI
    if ":" not in termId:
        return f"{VOCABURI}{termId}"

    if termId.startswith("http"):
        return termId
    prefix: str
    id_component: str
    prefix, id_component = termId.split(":", 1)
    return f"{uriForPrefix(prefix)}{id_component}"


def uriWrap(identity_str: str) -> str:
    if identity_str.startswith(("http://", "https://")):
        return f"<{identity_str}>"
    return identity_str


LAYERPATTERN: Optional[str] = None


def layerFromUri(uri: str) -> Optional[str]:
    global VOCABURI, LAYERPATTERN
    assert VOCABURI
    if not uri:
        return None
    if not LAYERPATTERN:
        voc: str = VOCABURI.rstrip("/#")
        prto: Optional[str]
        root: Optional[str]
        prto, root = getProtoAndRoot(voc)
        LAYERPATTERN = rf"^{prto}([\w]*)\.{root}"

    if m := re.search(LAYERPATTERN, str(uri)):
        return m.group(1)
    return None


def uriFromLayer(layer: Optional[str] = None) -> str:
    global VOCABURI
    assert VOCABURI is not None
    voc: str = VOCABURI.rstrip("/#")
    if not layer:
        return voc
    prto: Optional[str]
    root: Optional[str]
    prto, root = getProtoAndRoot(voc)
    return f"{prto}{layer}.{root}"


ProtoAndRoot = collections.namedtuple("ProtoAndRoot", ["proto", "root"])


def getProtoAndRoot(uri: str) -> ProtoAndRoot:
    m: Optional[re.Match] = re.search(r"^(http[s]?:\/\/)(.*)", uri)
    if m:
        return ProtoAndRoot(m.group(1), m.group(2))
    return ProtoAndRoot(None, None)


def uri2id(uri: str) -> str:
    global VOCABURI
    assert VOCABURI is not None
    if uri.startswith(VOCABURI):
        return uri[len(VOCABURI) :]
    return uri


def prefixFromUri(uri: str) -> Optional[str]:
    if SdoTermSource.SOURCEGRAPH is None:
        return None
    pref: rdflib.term.Node
    pth: rdflib.term.Node
    for pref, pth in SdoTermSource.SOURCEGRAPH.namespaces():
        if uri.startswith(str(pth)):
            return str(pref)
    return None


def uriForPrefix(pre: str) -> Optional[rdflib.term.URIRef]:
    if SdoTermSource.SOURCEGRAPH is None:
        return None
    pref: rdflib.term.Node
    pth: rdflib.term.URIRef
    for pref, pth in SdoTermSource.SOURCEGRAPH.namespaces():
        if pre == str(pref):
            return pth
    return None


def prefixedIdFromUri(uri: str) -> str:
    """Converts a URI into a string of the form namespace:term."""
    prefix: Optional[str] = prefixFromUri(uri)
    if prefix:
        base: str = Path(uri).name
        if "#" in base:
            base = base.split("#", 1)[1]
        return f"{prefix}:{base}"
    return uri
