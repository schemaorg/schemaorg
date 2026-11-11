from __future__ import annotations

from collections.abc import Iterable, Sequence
import json
import logging
from pathlib import Path
import threading
from typing import Any

import rdflib

from schemaorg import constants
from schemaorg.layout import Issues
from schemaorg.sdo_uri import SDO, SdoUri
import SchemaTerms.localmarkdown as localmarkdown
import SchemaTerms.sdocollaborators as sdocollaborators
import SchemaTerms.sdoterm as sdoterm
import util.paths as paths
import util.pretty_logger as pretty_logger
from util.sort_dict import sort_dict

log: logging.Logger = logging.getLogger(__name__)

CORE: str = "core"
_RDF_FILE_FORMATS: dict[str, str] = {".nt": "nt", ".ttl": "turtle"}


def bindNameSpaces(graph: rdflib.Graph) -> None:
    namespaces: dict[str, str] = {
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
        "fibo-fnd-arr-reg": "https://spec.edmcouncil.org/fibo/ontology/FND/Arrangements/Registration/",
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
    for prefix, uri in namespaces.items():
        graph.bind(prefix, uri)


class _TermAccumulator:
    """Temporary holder to accumulate term information."""

    def __init__(self, term_id: str) -> None:
        self.id: str = term_id
        self.types: list[rdflib.URIRef] = []
        self.sups: list[rdflib.URIRef] = []
        self.label: str | None = None
        self.layer: str | None = None
        self.type: rdflib.URIRef | None = None

    def appendRow(self, row: rdflib.query.ResultRow) -> None:
        self.types.append(row.type)
        self.sups.append(row.sup)
        self.type = row.type
        self.label = str(row.label)
        self.layer = layerFromUri(row.layer)


def _parse_into_graph(graph: rdflib.Graph, file_path: str | Path) -> None:
    """Parse one RDF source file directly into graph."""
    path = Path(file_path)
    file_format = _RDF_FILE_FORMATS.get(path.suffix)
    if not file_format:
        raise NotImplementedError(f"Unsupported file format: {path.suffix}")
    try:
        graph.parse(source=path, format=file_format)
    except Exception as e:
        message = f"Error parsing source file '{file_path}': {e}"
        log.warning(message)
        raise OSError(message) from e


class SdoTermSource:
    """This class acts as the source of information for terms."""

    TERMCOUNTS: dict[sdoterm.SdoTermType | str, int] | None = None

    SOURCEGRAPH: rdflib.Graph | None = None
    EXPANDEDTERMS: dict[str, Any] = {}
    TERMS: dict[str, Any] = {}

    TERMSLOCK: threading.Lock = threading.Lock()
    RDFLIBLOCK: threading.Lock = threading.Lock()
    LOADEDDEFAULT: bool = False

    def __init__(
        self,
        uri: str,
        ttype: rdflib.URIRef | str | None = None,
        label: str = "",
        layer: str | None = None,
    ) -> None:
        term_id: str = uri2id(uri)
        self.layer: str = layer or CORE
        self.termdesc: Any = None

        self.parent: sdoterm.SdoTerm | None = None
        self.supersededBy: str | None = None
        self.supersedes: list[str] | None = None
        self.supers: list[str] | None = None
        self.termStack: list[sdoterm.SdoTerm] | None = None
        self.subs: list[str] | None = None
        self.members: list[str] | None = None
        self.props: list[str] | None = None
        self.ranges: list[str] | None = None
        self.domains: list[str] | None = None
        self.targetOf: list[str] | None = None
        self.equivalents: list[str] | None = None
        self.gotinverseOf: bool = False
        self.inverseOf: str | None = None
        self.comments: Sequence[str] | None = None
        self.comment: str | None = None
        self.sources: list[str] | None = None
        self.acks: Sequence[sdocollaborators.collaborator] | None = None
        cls: type[SdoTermSource] = self.__class__
        self.ttype: sdoterm.SdoTermType
        if ttype == rdflib.RDFS.Class:
            self.ttype = sdoterm.SdoTermType.TYPE
            if uri == str(SDO.DataType):
                self.ttype = sdoterm.SdoTermType.DATATYPE
            elif uri == str(SDO.Enumeration):
                self.ttype = sdoterm.SdoTermType.ENUMERATION
            elif self._isEnumeration(term_id=term_id):
                self.ttype = sdoterm.SdoTermType.ENUMERATION
        elif ttype == rdflib.RDF.Property:
            self.ttype = sdoterm.SdoTermType.PROPERTY
        elif ttype == SDO.Enumeration:
            self.ttype = sdoterm.SdoTermType.ENUMERATION
        elif ttype == SDO.DataType:
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
                self.termdesc._enumerationMembers.setIds(
                    self.getEnumerationMembers() or ()
                )
        elif self.ttype == sdoterm.SdoTermType.PROPERTY:
            self.termdesc.domainIncludes.setIds(self.getDomains())
            self.termdesc.rangeIncludes.setIds(self.getRanges())
            self.termdesc.inverse.setId(self.getInverseOf())
        elif self.ttype == sdoterm.SdoTermType.REFERENCE:
            self.termdesc.label = prefixedIdFromUri(uri)

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

    @classmethod
    def _isEnumeration(cls, term_id: str) -> bool:
        query: str = f"""
          ASK {{
                    {uriWrap(toFullId(term_id))} rdfs:subClassOf* {uriWrap(str(SDO.Enumeration))}.
            }}"""

        result: Sequence[rdflib.query.ResultRow] = cls.query(query)
        return bool(result[-1])

    def getComments(self) -> Sequence[str]:
        if self.comments is None:
            self.comments = tuple(map(str, self.loadObjects(rdflib.RDFS.comment)))
        return self.comments

    def getComment(self) -> str:
        if self.comment is None:
            self.loadComment()
        assert self.comment is not None
        return self.comment

    def getSupersededBy(self) -> str:
        if self.supersededBy is None:
            ss = self.loadObjects("schema:supersededBy")
            tmp = [t for s in ss if (t := uri2id(str(s)))]

            if len(tmp) > 1:
                log.debug(
                    "Warning '%s' supersededBy more than 1 term (%d)",
                    self.id,
                    len(tmp),
                )
            self.supersededBy = tmp[0] if tmp else ""
        return self.supersededBy

    def superseded(self) -> bool:
        return bool(self.getSupersededBy())

    def getSupersedes(self) -> list[str]:
        if self.supersedes is None:
            subs = self.loadSubjects("schema:supersededBy")
            self.supersedes = sorted(uri2id(str(sub)) for sub in subs)
        return self.supersedes

    def getSources(self) -> list[str]:
        if self.sources is None:
            objs = self.loadObjects("schema:source")
            self.sources = sorted(str(o) for o in objs)
        return self.sources

    def getAcknowledgements(self) -> Sequence[sdocollaborators.collaborator]:
        if self.acks is None:
            acks = [
                cont
                for obj in self.loadObjects("schema:contributor")
                if obj and (cont := sdocollaborators.collaborator.getContributor(str(obj)))
            ]
            self.acks = sorted(acks, key=lambda t: t.title or "")
        return self.acks

    def getInverseOf(self) -> str | None:
        if not self.gotinverseOf:
            self.gotinverseOf = True
            if inverse := self.loadValue("schema:inverseOf"):
                self.inverseOf = uri2id(str(inverse))
        return self.inverseOf

    def getSupers(self) -> list[str]:
        if self.supers is None:
            self.loadsupers()
        assert self.supers is not None
        return self.supers

    def getTermStack(self) -> list[sdoterm.SdoTerm]:
        if self.termStack is None:
            self.termStack = []
            for sup_id in self.getSupers():
                try:
                    s = self.__class__._getTerm(sup_id, createReference=True)
                    if not s or s.termType == sdoterm.SdoTermType.REFERENCE:
                        continue
                    self.termStack.append(s)
                    if s.termStack:
                        self.termStack.extend(s.termStack.terms)
                except RecursionError as e:
                    assert self.termdesc is not None
                    e.add_note(f"Circular references with {self.termdesc}")
                    raise
            stack: list[sdoterm.SdoTerm] = []
            for t in reversed(self.termStack):
                if t not in stack:
                    stack.append(t)
            self.termStack = list(reversed(stack))
        return self.termStack

    def getSubs(self) -> list[str]:
        if self.subs is None:
            self.loadsubs()
        assert self.subs is not None
        return self.subs

    def getProperties(self, getall: bool = False) -> list[str]:
        if self.props is None:
            subs = self.loadSubjects("schema:domainIncludes")
            self.props = sorted(uri2id(str(sub)) for sub in subs)
        ret = self.props

        if getall:
            allprop_ids: set[str] = set(self.props)
            for t in self.getTermStack():
                term = (
                    t
                    if isinstance(t, sdoterm.SdoTerm)
                    else self.__class__._getTerm(t, createReference=True)
                )
                if term and term.id != self.id and term.termType in sdoterm.SdoTerm.TYPE_LIKE_TYPES:
                    allprop_ids.update(term.allproperties.ids)
            ret = sorted(allprop_ids)
        return ret

    def getRanges(self) -> list[str]:
        if self.ranges is None:
            objs = self.loadObjects("schema:rangeIncludes")
            self.ranges = sorted(uri2id(str(obj)) for obj in objs)
        return self.ranges

    def getDomains(self) -> list[str]:
        if self.domains is None:
            objs = self.loadObjects("schema:domainIncludes")
            self.domains = sorted(uri2id(str(obj)) for obj in objs)
        return self.domains

    def getTargetOf(self) -> list[str]:
        if self.targetOf is None:
            subs = self.loadSubjects("schema:rangeIncludes")
            self.targetOf = sorted(uri2id(str(sub)) for sub in subs)
        return self.targetOf

    def getEquivalents(self) -> list[str]:
        if self.equivalents is None:
            equivalents = self.loadObjects("owl:equivalentClass")
            equivalents.extend(self.loadObjects("owl:equivalentProperty"))
            self.equivalents = sorted((str(e) for e in equivalents), key=prefixedIdFromUri)
        return self.equivalents

    def inLayers(self, layers: str | Iterable[str]) -> bool:
        if isinstance(layers, str):
            return self.layer == layers
        return self.layer in layers

    def getExtLayer(self) -> str:
        return self.layer if self.layer and self.layer != CORE else ""

    @classmethod
    def subClassOf(
        cls, child: str | sdoterm.SdoTerm, parent: str | sdoterm.SdoTerm
    ) -> bool:
        child_obj = cls.getTerm(child) if isinstance(child, str) else child
        parent_obj = cls.getTerm(parent) if isinstance(parent, str) else parent

        if child_obj == parent_obj:
            return True
        if not child_obj or not parent_obj:
            return False

        parents = child_obj.supers.ids
        if parent_obj.id in parents:
            return True

        return any(cls.subClassOf(p, parent_obj) for p in parents)

    def loadComment(self) -> None:
        comments = self.getComments()
        wpre: str | None = None
        assert self.termdesc is not None
        name: str = self.termdesc.id
        if name.startswith("https:"):
            val = Path(name).name
            wpre = name[: -len(val)]

        comment_buffer = [
            localmarkdown.Markdown.parse(comment, wpre=wpre) for comment in comments
        ]
        self.comment = " ".join(comment_buffer).strip()

    def loadValue(self, valType: str) -> Any | None:
        ret = self.loadObjects(valType)
        return ret[0] if ret else None

    def loadObjects(self, pred: rdflib.URIRef | str) -> list[rdflib.term.Node]:
        query = f"""
        SELECT ?val WHERE {{
                {uriWrap(toFullId(self.id))} {uriWrap(str(pred))} ?val.
         }}"""
        return [row.val for row in self.__class__.query(query)]

    def loadSubjects(self, pred: rdflib.URIRef | str) -> list[rdflib.term.Node]:
        query = f"""
        SELECT ?sub WHERE {{
                ?sub {uriWrap(str(pred))} {uriWrap(toFullId(self.id))}.
         }}"""
        return [row.sub for row in self.__class__.query(query)]

    def loadsupers(self) -> None:
        wrapped_id = uriWrap(toFullId(self.id))
        query = f"""
        SELECT ?sup WHERE {{
             {{
                 {wrapped_id} rdfs:subClassOf ?sup .
             }} UNION {{
                 {wrapped_id} rdfs:subPropertyOf ?sup .
             }}
         }}
         ORDER BY ?sup"""

        res = self.__class__.query(query)
        self.supers = sorted(uri2id(str(row.sup)) for row in res)

    def loadsubs(self) -> None:
        fullId = toFullId(self.id)
        sel = (
            "rdfs:subClassOf"
            if self.ttype in sdoterm.SdoTerm.TYPE_LIKE_TYPES
            else "rdfs:subPropertyOf"
        )
        query = f"""
        SELECT ?sub WHERE {{
                ?sub {uriWrap(sel)} {uriWrap(fullId)}.
         }} ORDER BY ?sub"""
        res = self.__class__.query(query)
        self.subs = [uri2id(str(row.sub)) for row in res]

        if self.ttype == sdoterm.SdoTermType.DATATYPE:
            subjects = self.loadSubjects("a")
            self.subs.extend(uri2id(str(child)) for child in subjects)
        self.subs.sort()

    def getEnumerationMembers(self) -> list[str] | None:
        if self.members is None and self.ttype == sdoterm.SdoTermType.ENUMERATION:
            subjects = self.loadSubjects("a")
            self.members = sorted(uri2id(str(child)) for child in subjects)
        return self.members

    def getParentPaths(self) -> list[list[str]]:
        cstack_list: list[str] = []
        self._pstacks: list[list[str]] = [cstack_list]
        assert self.termdesc is not None
        self._getParentPaths(self.termdesc, cstack_list)

        inserts: list[str] = []
        if self.ttype == sdoterm.SdoTermType.PROPERTY:
            inserts = ["Property", "Thing"]
        elif self.ttype == sdoterm.SdoTermType.DATATYPE and self.id != "DataType":
            inserts = ["DataType"]
        elif self.ttype == sdoterm.SdoTermType.TYPE:
            base = self._pstacks[0][0]
            basetype = (
                self.termdesc
                if base == self.id
                else self.__class__._getTerm(base)
            )
            if basetype and basetype.termType == sdoterm.SdoTermType.DATATYPE:
                inserts = ["DataType"]

        for ins in inserts:
            for s in self._pstacks:
                s.insert(0, ins)

        return self._pstacks

    def _getParentPaths(self, term: sdoterm.SdoTerm, cstack: list[str]) -> None:
        cstack.insert(0, term.id)
        super_ids: list[str] = list(term.supers.ids)

        if (
            term.termType == sdoterm.SdoTermType.ENUMERATIONVALUE
            and term.enumerationParent
            and term.enumerationParent.id not in super_ids
        ):
            assert term.enumerationParent.id is not None
            super_ids.append(term.enumerationParent.id)

        super_ids = [sid for sid in super_ids if SdoUri(sid).is_sdo()]

        tmpStacks: list[list[str]] = [cstack]
        if super_ids:
            for _ in range(1, len(super_ids)):
                t = cstack[:]
                tmpStacks.append(t)
                self._pstacks.append(t)

            for x, parent_id in enumerate(super_ids):
                sup = self.__class__._getTerm(parent_id)
                if sup:
                    self._getParentPaths(sup, tmpStacks[x])

    @classmethod
    def getParentPathTo(
        cls, start_term_id: str, end_term_id: str | None = None
    ) -> list[list[str]]:
        end_term_id = end_term_id or "Thing"
        start_term = cls.getTerm(start_term_id, expanded=True)
        if not start_term:
            return []
        return [list(path) for path in start_term.superPaths if end_term_id in path]

    @classmethod
    def expandTerms(
        cls, terms: Iterable[sdoterm.SdoTerm], depth: int = 2
    ) -> list[sdoterm.SdoTerm]:
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
                assert isinstance(termdesc, sdoterm.SdoEnumeration)
                termdesc.enumerationMembers.setTerms(
                    cls.termsFromIds(termdesc.enumerationMembers.ids)
                )
        elif termdesc.termType == sdoterm.SdoTermType.PROPERTY:
            assert isinstance(termdesc, sdoterm.SdoProperty)
            termdesc.domainIncludes.setTerms(
                cls.termsFromIds(termdesc.domainIncludes.ids)
            )
            termdesc.rangeIncludes.setTerms(
                cls.termsFromIds(termdesc.rangeIncludes.ids)
            )
            if termdesc.inverse.id:
                termdesc.inverse.setTerm(cls.termFromId(termdesc.inverse.id))
        elif termdesc.termType == sdoterm.SdoTermType.ENUMERATIONVALUE:
            assert isinstance(termdesc, sdoterm.SdoEnumerationvalue)
            if termdesc.enumerationParent.id:
                termdesc.enumerationParent.setTerm(
                    cls.termFromId(termdesc.enumerationParent.id)
                )

        termdesc.termStack.setTerms(
            cls.expandTerms(
                cls.termsFromIds(termdesc.termStack.ids), depth=depth - 1
            )
        )

        return termdesc

    @classmethod
    def termFromId(cls, id: str = "") -> sdoterm.SdoTerm | None:
        if not id:
            return None
        ids = cls.termsFromIds([id])
        return ids[0] if ids else None

    @classmethod
    def termsFromIds(
        cls, ids: Sequence[str | sdoterm.SdoTerm] | None = None
    ) -> Sequence[sdoterm.SdoTerm]:
        """Convert a sequence of term-identities into a sequence of SdoTerms."""
        ret: list[sdoterm.SdoTerm] = []
        for tid in ids or ():
            if tid:
                if isinstance(tid, str):
                    if term := cls._getTerm(tid, createReference=True):
                        ret.append(term)
                else:
                    ret.append(tid)
        return ret

    @classmethod
    def _singleTermFromResult(
        cls, res: Sequence[rdflib.query.ResultRow], termId: str
    ) -> sdoterm.SdoTerm | None:
        """Return a single term matching `termId` from res."""
        tmp = _TermAccumulator(termId)
        for row in res:
            tmp.appendRow(row)

        return cls._createTerm(tmp)

    @classmethod
    def termsFromResults(
        cls, res: Sequence[rdflib.query.ResultRow]
    ) -> Sequence[sdoterm.SdoTerm]:
        rows_by_term_id: dict[str, _TermAccumulator] = {}
        for row in res:
            key = str(row.term)
            acc = rows_by_term_id.get(key)
            if acc is None:
                acc = _TermAccumulator(key)
                rows_by_term_id[key] = acc
            acc.appendRow(row)

        return [t for acc in rows_by_term_id.values() if (t := cls._createTerm(acc))]

    @classmethod
    def _createTerm(cls, tmp: _TermAccumulator) -> sdoterm.SdoTerm | None:
        if not tmp or not tmp.id:
            return None

        if SDO.DataType in tmp.types:
            tmp.type = SDO.DataType
        elif SDO.Enumeration in tmp.sups:
            tmp.type = SDO.Enumeration
        elif len(tmp.types) > 1:
            tmp.type = sorted(tmp.types)[0]

        term: sdoterm.SdoTerm | None = cls.TERMS.get(tmp.id)
        if not term:
            term = cls(
                tmp.id, ttype=tmp.type, label=tmp.label or "", layer=tmp.layer
            ).termdesc
        return term

    @classmethod
    def triples4Term(
        cls, termId: str
    ) -> Iterable[tuple[rdflib.term.Node, rdflib.term.Node, rdflib.term.Node]]:
        term = cls.getTerm(termId)
        g = cls.SOURCEGRAPH
        if not term or g is None:
            return ()
        return g.triples((rdflib.URIRef(term.uri), None, None))

    @classmethod
    def getTermAsRdfString(
        cls, termId: str, output_format: str, full: bool = False
    ) -> str:
        term = cls.getTerm(termId)
        if not term or term.termType == sdoterm.SdoTermType.REFERENCE:
            return ""
        g = rdflib.Graph()
        g.bind("schema", constants.SCHEMA_URI)

        if not full:
            for trip in cls.triples4Term(term.id):
                g.add(trip)
        else:
            types: list[sdoterm.SdoTerm] = []
            props: list[sdoterm.SdoTerm] = []
            stack: list[sdoterm.SdoTerm] = [term, *cls.termsFromIds(term.termStack.ids)]

            for t in stack:
                if t.termType == sdoterm.SdoTermType.PROPERTY:
                    props.append(t)
                else:
                    types.append(t)
                    if t.termType == sdoterm.SdoTermType.ENUMERATIONVALUE:
                        assert isinstance(t, sdoterm.SdoEnumerationvalue)
                        if e_parent := cls.termFromId(t.enumerationParent.id or ""):
                            types.append(e_parent)
                    elif t == stack[0]:
                        assert isinstance(t, sdoterm._SdoTypeLike)
                        props.extend(cls.termsFromIds(t.allproperties.ids))

            for item in (*sorted(types), *sorted(props)):
                for trip in cls.triples4Term(item.id):
                    g.add(trip)

        if output_format == "rdf":
            output_format = "pretty-xml"

        ret = g.serialize(
            format=output_format, auto_compact=True, sort_keys=True, max_depth=1
        )

        if output_format == "json-ld":
            try:
                return json.dumps(sort_dict(json.loads(ret)), indent=2)
            except (TypeError, ValueError):
                pass
        return str(ret)

    @classmethod
    def getAllTypes(
        cls, layer: str | None = None, expanded: bool = False
    ) -> Sequence[str | sdoterm.SdoTerm]:
        return cls.getAllTerms(
            ttype=sdoterm.SdoTermType.TYPE, layer=layer, expanded=expanded
        )

    @classmethod
    def getAllProperties(
        cls, layer: str | None = None, expanded: bool = False
    ) -> Sequence[str | sdoterm.SdoTerm]:
        return cls.getAllTerms(
            ttype=sdoterm.SdoTermType.PROPERTY, layer=layer, expanded=expanded
        )

    @classmethod
    def getAllEnumerationvalues(
        cls, layer: str | None = None, expanded: bool = False
    ) -> Sequence[str | sdoterm.SdoTerm]:
        return cls.getAllTerms(
            ttype=sdoterm.SdoTermType.ENUMERATIONVALUE, layer=layer, expanded=expanded
        )

    @classmethod
    def getAllTerms(
        cls,
        ttype: sdoterm.SdoTermType | None = None,
        layer: str | None = None,
        suppressSourceLinks: bool = False,
        expanded: bool = False,
    ) -> Sequence[str | sdoterm.SdoTerm]:
        with pretty_logger.BlockLog(
            logger=log, message="GetAllTerms", timing=True
        ) as block:
            typsel: str = ""
            extra: str = ""
            if ttype == sdoterm.SdoTermType.TYPE:
                typsel = f"a <{rdflib.RDFS.Class}>;"
            elif ttype == sdoterm.SdoTermType.PROPERTY:
                typsel = f"a <{rdflib.RDF.Property}>;"
            elif ttype == sdoterm.SdoTermType.DATATYPE:
                typsel = f"a <{SDO.DataType}>;"
            elif ttype == sdoterm.SdoTermType.ENUMERATION:
                typsel = f"rdfs:subClassOf* <{SDO.Enumeration}>;"
            elif ttype == sdoterm.SdoTermType.ENUMERATIONVALUE:
                extra = f"?type rdfs:subClassOf*  <{SDO.Enumeration}>."
            elif ttype:
                log.debug("Invalid type value '%s'", ttype)

            laysel: str = ""
            fil: str = ""
            if layer:
                if layer == CORE:
                    fil = "FILTER NOT EXISTS { ?term schema:isPartOf ?x. }"
                else:
                    laysel = f"schema:isPartOf <{uriFromLayer(layer)}>; "

            suppress = (
                "FILTER NOT EXISTS { ?s dc:source ?term. }"
                if suppressSourceLinks
                else ""
            )

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

            log.debug("query %s", query)
            res = cls.query(query)
            log.debug("res %d", len(res))

            terms: list[str | sdoterm.SdoTerm]
            if expanded:
                with pretty_logger.BlockLog(
                    logger=log, message=f"Expanding {len(res)} terms", timing=True
                ):
                    terms = list(cls.termsFromResults(res))
            else:
                terms = list(dict.fromkeys(uri2id(str(row.term)) for row in res))
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
        return cls.termsFromResults(cls.query(query))

    @classmethod
    def setSourceGraph(cls, g: rdflib.Graph) -> None:
        cls.SOURCEGRAPH = g
        g.bind("schema", constants.SCHEMA_URI)
        bindNameSpaces(g)

        cls.TERMS = {}
        cls.EXPANDEDTERMS = {}
        cls.TERMCOUNTS = None

    @classmethod
    def loadSourceGraph(
        cls, files: str | Iterable[str | Path] | None = None, init: bool = False
    ) -> None:
        if init:
            cls.SOURCEGRAPH = None

        load_files: Sequence[str | Path]
        if not files or files == "default":
            if cls.SOURCEGRAPH is not None:
                if not cls.LOADEDDEFAULT:
                    raise RuntimeError(
                        "Sourcegraph already loaded - cannot overwrite with defaults"
                    )
                log.info("Default files already loaded")
                return

            cls.LOADEDDEFAULT = True
            log.info("SdoTermSource.loadSourceGraph() loading from default files")
            load_files = Issues(paths.DefaultInputLayout()).get_ttl_files()
        elif isinstance(files, str):
            cls.LOADEDDEFAULT = False
            log.info("SdoTermSource.loadSourceGraph() loading from file: %s", files)
            load_files = [files]
        else:
            cls.LOADEDDEFAULT = False
            load_files = list(files)
            log.info(
                "SdoTermSource.loadSourceGraph() loading from %d files",
                len(load_files),
            )

        if not load_files:
            raise ValueError("No triples file(s) to load")

        parsed = rdflib.Graph(bind_namespaces="none")
        for file_path in load_files:
            _parse_into_graph(parsed, file_path)
        graph = rdflib.Graph()
        graph += parsed
        cls.setSourceGraph(graph)
        log.info(
            "Done: Loaded %d triples - %d terms",
            len(cls.sourceGraph()),
            len(cls.getAllTerms()),
        )

    @classmethod
    def sourceGraph(cls) -> rdflib.Graph:
        if cls.SOURCEGRAPH is None:
            cls.loadSourceGraph()
        assert cls.SOURCEGRAPH is not None
        return cls.SOURCEGRAPH

    @staticmethod
    def vocabUri() -> str:
        return constants.SCHEMA_URI

    @classmethod
    def query(cls, query_string: str) -> Sequence[rdflib.query.ResultRow]:
        graph = cls.sourceGraph()
        with cls.RDFLIBLOCK:
            return tuple(graph.query(query_string))

    @classmethod
    def termCounts(cls) -> dict[sdoterm.SdoTermType | str, int]:
        if cls.TERMCOUNTS is None:
            def run_count_query(q: str) -> int:
                res = cls.query(q)
                return int(res[0][0])

            classes = run_count_query(f'SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {{ ?s a rdfs:Class . FILTER (strStarts(str(?s),"{constants.SCHEMA_URI}")) }}')
            properties = run_count_query(f'SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {{ ?s a rdf:Property . FILTER (strStarts(str(?s),"{constants.SCHEMA_URI}")) }}')
            enums = run_count_query(f'SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {{ ?s rdfs:subClassOf* schema:Enumeration . FILTER (strStarts(str(?s),"{constants.SCHEMA_URI}")) }}')
            enumvals = run_count_query(f'SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {{ ?s a ?type . ?type rdfs:subClassOf* schema:Enumeration . FILTER (strStarts(str(?s),"{constants.SCHEMA_URI}")) }}')
            datatypes = run_count_query(f'SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {{ {{ ?s a schema:DataType . }}UNION{{ ?s rdf:type* schema:DataType . }}UNION{{ ?s rdfs:subClassOf* ?x . ?x a schema:DataType . }} FILTER (strStarts(str(?s),"{constants.SCHEMA_URI}")) }}')
            datatypeclasses = run_count_query(f'SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {{ ?s rdfs:subClassOf* ?x . ?x a schema:DataType . FILTER (strStarts(str(?s),"{constants.SCHEMA_URI}")) }}')

            types = classes - 1 - enums - datatypeclasses
            datatypes -= 1

            cls.TERMCOUNTS = {
                sdoterm.SdoTermType.TYPE: types,
                sdoterm.SdoTermType.PROPERTY: properties,
                sdoterm.SdoTermType.DATATYPE: datatypes,
                sdoterm.SdoTermType.ENUMERATION: enums,
                sdoterm.SdoTermType.ENUMERATIONVALUE: enumvals,
                "All": types + properties + datatypes + enums + enumvals,
            }
        return cls.TERMCOUNTS

    @classmethod
    def getTerm(
        cls,
        termId: str,
        expanded: bool = False,
        createReference: bool = False,
    ) -> sdoterm.SdoTerm | None:
        with cls.TERMSLOCK:
            return cls._getTerm(
                termId,
                expanded=expanded,
                createReference=createReference,
            )

    @classmethod
    def _getTerm(
        cls,
        termId: str,
        expanded: bool = False,
        createReference: bool = False,
    ) -> sdoterm.SdoTerm | None:
        if not termId:
            return None
        assert isinstance(termId, str), termId
        termId = termId.strip()
        fullId = toFullId(termId)
        term: sdoterm.SdoTerm | None = cls.TERMS.get(fullId)

        if not term:
            wrapped = uriWrap(fullId)
            query = f"""
            SELECT ?term ?type ?label ?layer ?sup WHERE {{
                 {wrapped} a ?type;
                    rdfs:label ?label.
                OPTIONAL {{ {wrapped} schema:isPartOf ?layer. }}
                OPTIONAL {{ {wrapped} rdfs:subClassOf ?sup. }}
                OPTIONAL {{ {wrapped} rdfs:subPropertyOf ?sup. }}
            }}"""
            res = cls.query(query)
            if res:
                term = cls._singleTermFromResult(res, termId=fullId)
            elif createReference:
                term = cls(fullId).getTermdesc()
            else:
                log.warning("No definition of term %s", fullId)

        if term and expanded and not term.expanded():
            if fullId not in cls.EXPANDEDTERMS:
                cls.EXPANDEDTERMS[fullId] = cls.expandTerm(term)
            term = cls.EXPANDEDTERMS[fullId]

        return term


def toFullId(termId: str) -> str:
    if ":" not in termId:
        return f"{constants.SCHEMA_URI}{termId}"

    if termId.startswith("http"):
        return termId
    prefix, id_component = termId.split(":", 1)
    return f"{uriForPrefix(prefix)}{id_component}"


def uriWrap(identity_str: str) -> str:
    if identity_str.startswith(("http://", "https://")):
        return f"<{identity_str}>"
    return identity_str


def layerFromUri(uri: str | None) -> str | None:
    """Layer named by a schema.org host (``pending``, ``attic``, ...); None for core or non-URIs."""
    if not uri:
        return None
    layer = SdoUri(uri).layer()
    return None if layer == CORE else layer


def uriFromLayer(layer: str | None = None) -> str:
    return str(SdoUri.for_layer(layer))


def uri2id(uri: str) -> str:
    return SdoUri(uri).term_name()


def prefixFromUri(uri: str) -> str | None:
    if SdoTermSource.SOURCEGRAPH is None:
        return None
    for pref, pth in SdoTermSource.SOURCEGRAPH.namespaces():
        if uri.startswith(str(pth)):
            return str(pref)
    return None


def uriForPrefix(pre: str) -> rdflib.term.URIRef | None:
    if SdoTermSource.SOURCEGRAPH is None:
        return None
    for pref, pth in SdoTermSource.SOURCEGRAPH.namespaces():
        if pre == str(pref):
            return pth
    return None


def prefixedIdFromUri(uri: str) -> str:
    """Converts a URI into a string of the form namespace:term."""
    if prefix := prefixFromUri(uri):
        base = Path(uri).name
        if "#" in base:
            base = base.split("#", 1)[1]
        return f"{prefix}:{base}"
    return uri
