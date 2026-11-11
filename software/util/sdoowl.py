#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from typing import Dict, FrozenSet, List, Optional, Set
from xml.dom import minidom
from xml.etree import ElementTree

import rdflib
from rdflib.namespace import RDF, RDFS
from rdflib.term import URIRef

from schemaorg import constants
from schemaorg.sdo_uri import SDO, SdoUri
from SchemaTerms.localmarkdown import Markdown, MarkdownTool
from SchemaTerms.sdotermsource import SdoTermSource, layerFromUri, uriFromLayer
import util.schema as schema


NAMESPACES: Dict[str, str] = {
    "xml:base": constants.SCHEMA_URI,
    "xmlns": constants.SCHEMA_URI,
    "xmlns:schema": constants.SCHEMA_URI,
    "xmlns:rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "xmlns:rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xmlns:owl": "http://www.w3.org/2002/07/owl#",
    "xmlns:dcterms": "http://purl.org/dc/terms/",
    "xmlns:xsd": "http://www.w3.org/2001/XMLSchema#",
}


DEFAULTRANGES: FrozenSet[str] = frozenset(str(t) for t in (SDO.Text, SDO.URL, SDO.Role))
DATATYPES: FrozenSet[str] = frozenset(
    str(t)
    for t in (
        SDO.Boolean,
        SDO.Date,
        SDO.DateTime,
        SDO.Number,
        SDO.Float,
        SDO.Integer,
        SDO.Time,
    )
)


def _MakePrettyComment(text: str) -> ElementTree.Comment:
    """Make a pretty comment with a box of slashes before and after."""
    inner_text: str = f"/ {text}"
    bar: str = "/" * len(inner_text)
    comment: str = f"\n\t{bar}\n\t{inner_text}\n\t{bar}\n\n\t"
    return ElementTree.Comment(comment)


class OwlBuild:
    def __init__(self) -> None:
        self.typesCount: int = 0
        self.propsCount: int = 0
        self.namedCount: int = 0
        self.dom: ElementTree.Element
        self.ont: ElementTree.Element
        old_pre: str = MarkdownTool.WPRE
        MarkdownTool.setWikilinkPrePath("/")
        self._createDom()
        self._loadGraph()
        MarkdownTool.setWikilinkPrePath(old_pre)

    def _createDom(self) -> None:
        self.dom = ElementTree.Element("rdf:RDF")
        for k, v in sorted(NAMESPACES.items()):
            self.dom.set(k, v)

        version: str = schema.VERSION.current().number()
        version_date: Optional[str] = schema.VERSION.current().date()
        comment_text: str = f"Generated from Schema.org version: {version} released: {version_date}"
        self.dom.append(_MakePrettyComment(text=comment_text))
        self.ont = ElementTree.SubElement(self.dom, "owl:Ontology")
        self.ont.set("rdf:about", constants.SCHEMA_URI)
        info: ElementTree.Element = ElementTree.SubElement(self.ont, "owl:versionInfo")
        info.set("rdf:datatype", "http://www.w3.org/2001/XMLSchema#string")
        info.text = version
        x: ElementTree.Element = ElementTree.SubElement(self.ont, "rdfs:label")
        x.text = "Schema.org Vocabulary"
        x = ElementTree.SubElement(self.ont, "dcterms:modified")
        x.set("rdf:datatype", "http://www.w3.org/2001/XMLSchema#date")
        x.text = version_date
        self.dom.append(_MakePrettyComment(text="Definitions"))

    def _loadGraph(self) -> None:
        self.list(SdoTermSource.sourceGraph())

    def getContent(self) -> str:
        return self.prettify(self.dom)

    def prettify(self, elem: ElementTree.Element) -> str:
        doc: minidom.Document = minidom.parseString(ElementTree.tostring(elem))
        return doc.toprettyxml(encoding="UTF-8").decode("utf-8")

    def list(self, graph: rdflib.Graph) -> None:
        self.dom.append(_MakePrettyComment(text="Class Definitions"))
        types: Set[rdflib.term.Node] = {
            s
            for s, _, _ in graph.triples((None, RDF.type, RDFS.Class))
            if SdoUri(s).is_sdo()
        }
        for t in sorted(types, key=str):
            self.outputType(str(t), graph)

        self.dom.append(_MakePrettyComment(text="Property Definitions"))
        props: Set[rdflib.term.Node] = {
            s
            for s, _, _ in graph.triples((None, RDF.type, RDF.Property))
            if SdoUri(s).is_sdo()
        }
        for p in sorted(props, key=str):
            self.outputProp(str(p), graph)

        self.dom.append(_MakePrettyComment(text="Named Individuals Definitions"))

        self.outputEnums(graph)
        self.outputNamedIndividuals(str(SDO["True"]), graph)
        self.outputNamedIndividuals(str(SDO["False"]), graph)

    def outputType(self, uri: str, graph: rdflib.Graph) -> None:
        self.typesCount += 1

        typ: ElementTree.Element = ElementTree.SubElement(self.dom, "owl:Class")
        typ.set("rdf:about", uri)
        ext: Optional[str] = None
        for p, o in sorted(graph.predicate_objects(URIRef(uri)), key=lambda x: (str(x[0]), str(x[1]))):
            if p == RDFS.label:
                l: ElementTree.Element = ElementTree.SubElement(typ, "rdfs:label")
                l.set("xml:lang", "en")
                l.text = str(o)
            elif p == RDFS.comment:
                c: ElementTree.Element = ElementTree.SubElement(typ, "rdfs:comment")
                c.set("xml:lang", "en")
                c.text = Markdown.parse(str(o))
            elif p == RDFS.subClassOf:
                s: ElementTree.Element = ElementTree.SubElement(typ, "rdfs:subClassOf")
                s.set("rdf:resource", str(o))
            elif p == SDO.isPartOf:  # Defined in an extension
                ext = str(o)
            elif p == RDF.type and o == SDO.DataType:  # A datatype
                s = ElementTree.SubElement(typ, "rdfs:subClassOf")
                s.set("rdf:resource", str(SDO.DataType))

        typ.append(self.addDefined(uri, ext))

    def outputProp(self, uri: str, graph: rdflib.Graph) -> None:
        self.propsCount += 1
        children: List[ElementTree.Element] = []
        domains: Set[rdflib.term.Node] = set()
        ranges: List[str] = []
        datatypeonly: bool = True
        ext: Optional[str] = None
        for p, o in sorted(graph.predicate_objects(URIRef(uri)), key=lambda x: (str(x[0]), str(x[1]))):
            if p == RDFS.label:
                l: ElementTree.Element = ElementTree.Element("rdfs:label")
                l.set("xml:lang", "en")
                l.text = str(o)
                children.append(l)
            elif p == RDFS.comment:
                c: ElementTree.Element = ElementTree.Element("rdfs:comment")
                c.set("xml:lang", "en")
                c.text = Markdown.parse(str(o))
                children.append(c)
            elif p == RDFS.subPropertyOf:
                sub: ElementTree.Element = ElementTree.Element("rdfs:subPropertyOf")
                subval: str = str(o)
                if (
                    subval == "rdf:type"
                ):  # Fixes a special case with schema:additionalType
                    subval = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"

                sub.set("rdf:resource", subval)
                children.append(sub)
            elif p == SDO.inverseOf:
                sub = ElementTree.Element("owl:inverseOf")
                sub.set("rdf:resource", str(o))
                children.append(sub)
            elif p == SDO.supersededBy:
                sub = ElementTree.Element("schema:supersededBy")
                sub.set("rdf:resource", str(o))
                children.append(sub)
            elif p == SDO.domainIncludes:
                domains.add(o)
            elif p == SDO.rangeIncludes:
                ranges.append(str(o))
                if str(o) not in DATATYPES:
                    datatypeonly = False
            elif p == SDO.isPartOf:
                ext = str(o)

        children.append(self.addDefined(uri, ext))

        if not datatypeonly:
            ranges.extend(r for r in sorted(DEFAULTRANGES) if r not in ranges)

        if domains:
            d: ElementTree.Element = ElementTree.Element("rdfs:domain")
            children.append(d)
            cl: ElementTree.Element = ElementTree.SubElement(d, "owl:Class")
            u: ElementTree.Element = ElementTree.SubElement(cl, "owl:unionOf")
            u.set("rdf:parseType", "Collection")
            for target in sorted(domains, key=str):
                targ: ElementTree.Element = ElementTree.SubElement(u, "owl:Class")
                targ.set("rdf:about", str(target))

        if ranges:
            r_elem: ElementTree.Element = ElementTree.Element("rdfs:range")
            children.append(r_elem)
            cl_elem: ElementTree.Element = ElementTree.SubElement(r_elem, "owl:Class")
            u_elem: ElementTree.Element = ElementTree.SubElement(cl_elem, "owl:unionOf")
            u_elem.set("rdf:parseType", "Collection")
            for target_range in sorted(ranges):
                targ_elem: ElementTree.Element = ElementTree.SubElement(u_elem, "owl:Class")
                targ_elem.set("rdf:about", target_range)

        prop: ElementTree.Element
        if datatypeonly:
            prop = ElementTree.SubElement(self.dom, "owl:DatatypeProperty")
        else:
            prop = ElementTree.SubElement(self.dom, "owl:ObjectProperty")
        prop.set("rdf:about", uri)
        prop.extend(children)

    def addDefined(self, uri: str, ext: Optional[str] = None) -> ElementTree.Element:
        root: str = uriFromLayer(layerFromUri(ext))
        defn: ElementTree.Element = ElementTree.Element("rdfs:isDefinedBy")
        defn.set("rdf:resource", f"{root}/{SdoUri(uri).term_name()}")
        return defn

    def outputEnums(self, graph: rdflib.Graph) -> None:
        q: str = f""" prefix schema: <{constants.SCHEMA_URI}>
        select Distinct ?enum ?parent where{{
        ?parent rdfs:subClassOf schema:Enumeration.
            ?enum rdfs:subClassOf ?parent.
        }}
        """
        enums: List[rdflib.query.ResultRow] = list(graph.query(q))
        for row in sorted(enums, key=lambda r: (str(r.enum), str(r.parent))):
            self.outputNamedIndividuals(str(row.enum), graph, parent=str(row.parent))

    def outputNamedIndividuals(self, individual: str, graph: rdflib.Graph, parent: Optional[str] = None) -> None:
        self.namedCount += 1

        typ: ElementTree.Element = ElementTree.SubElement(self.dom, "owl:NamedIndividual")
        typ.set("rdf:about", individual)
        ext: Optional[str] = None
        for p, o in sorted(graph.predicate_objects(URIRef(individual)), key=lambda x: (str(x[0]), str(x[1]))):
            if p == RDFS.label:
                l: ElementTree.Element = ElementTree.SubElement(typ, "rdfs:label")
                l.set("xml:lang", "en")
                l.text = str(o)
            elif p == RDFS.comment:
                c: ElementTree.Element = ElementTree.SubElement(typ, "rdfs:comment")
                c.set("xml:lang", "en")
                c.text = Markdown.parse(str(o))
            elif p == SDO.isPartOf:
                ext = str(o)

        typ.append(self.addDefined(individual, ext))

        if parent:
            s: ElementTree.Element = ElementTree.SubElement(typ, "rdfs:subClassOf")
            s.set("rdf:resource", parent)
