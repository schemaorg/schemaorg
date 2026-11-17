"""OWL/XML ontology renderer."""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any
from xml.etree import ElementTree

import rdflib
from rdflib.namespace import RDF, RDFS
from rdflib.term import URIRef

from schemaorg import constants
from schemaorg.markdown import Markdown
from schemaorg.sdo_uri import SDO, SdoUri
from schemaorg.version import VersionItem

NAMESPACES: dict[str, str] = {
    "xml:base": constants.SCHEMA_URI,
    "xmlns": constants.SCHEMA_URI,
    "xmlns:schema": constants.SCHEMA_URI,
    "xmlns:rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "xmlns:rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xmlns:owl": "http://www.w3.org/2002/07/owl#",
    "xmlns:dcterms": "http://purl.org/dc/terms/",
    "xmlns:xsd": "http://www.w3.org/2001/XMLSchema#",
}

DEFAULTRANGES: frozenset[str] = frozenset(
    map(str, (SDO.Text, SDO.URL, SDO.Role))
)
DATATYPES: frozenset[str] = frozenset(
    map(
        str,
        (
            SDO.Boolean,
            SDO.Date,
            SDO.DateTime,
            SDO.Number,
            SDO.Float,
            SDO.Integer,
            SDO.Time,
        ),
    )
)


def _pretty_comment(text: str) -> ElementTree.Element[Any]:
    """XML comment framed with slash banners."""
    inner_text = f"/ {text}"
    bar = "/" * len(inner_text)
    return ElementTree.Comment(f"\n\t{bar}\n\t{inner_text}\n\t{bar}\n\n\t")


def _defined_by(uri: str, ext: str | None = None) -> ElementTree.Element:
    root = SdoUri.for_layer(SdoUri(ext).layer() if ext else None)
    return ElementTree.Element(
        "rdfs:isDefinedBy", {"rdf:resource": f"{root}/{SdoUri(uri).term_name()}"}
    )


def _text_element(
    tag: str, text: str, attrib: dict[str, str] | None = None
) -> ElementTree.Element:
    elem = ElementTree.Element(tag, attrib or {})
    elem.text = text
    return elem


def _union_element(tag: str, uris: Iterable[str]) -> ElementTree.Element:
    elem = ElementTree.Element(tag)
    cls_elem = ElementTree.SubElement(elem, "owl:Class")
    union = ElementTree.SubElement(
        cls_elem, "owl:unionOf", {"rdf:parseType": "Collection"}
    )
    for target in sorted(uris):
        ElementTree.SubElement(union, "owl:Class", {"rdf:about": target})
    return elem


class OwlRenderer:
    """OWL/XML ontology of the graph."""

    def __init__(self, graph: rdflib.Graph, version: VersionItem) -> None:
        self.graph = graph
        self.version = version

    def render(self) -> str:
        dom = self._create_dom()
        self._populate(dom)
        ElementTree.indent(dom, space="\t")
        return f"{ElementTree.tostring(dom, encoding='unicode', xml_declaration=True)}\n"

    def _sorted_predicate_objects(
        self, uri: str
    ) -> list[tuple[rdflib.term.Node, rdflib.term.Node]]:
        return sorted(
            self.graph.predicate_objects(URIRef(uri)),
            key=lambda pair: (str(pair[0]), str(pair[1])),
        )

    def _create_dom(self) -> ElementTree.Element:
        dom = ElementTree.Element("rdf:RDF", dict(sorted(NAMESPACES.items())))

        version = self.version.number()
        version_date = self.version.date()
        banner = (
            f"Generated from Schema.org version: {version} released: {version_date}"
            if version_date
            else f"Generated from Schema.org version: {version}"
        )
        dom.append(_pretty_comment(banner))
        ont = ElementTree.SubElement(
            dom, "owl:Ontology", {"rdf:about": constants.SCHEMA_URI}
        )
        ont.append(
            _text_element(
                "owl:versionInfo",
                version,
                {"rdf:datatype": "http://www.w3.org/2001/XMLSchema#string"},
            )
        )
        ont.append(_text_element("rdfs:label", "Schema.org Vocabulary"))
        if version_date is not None:
            ont.append(
                _text_element(
                    "dcterms:modified",
                    version_date,
                    {"rdf:datatype": "http://www.w3.org/2001/XMLSchema#date"},
                )
            )
        dom.append(_pretty_comment("Definitions"))
        return dom

    def _populate(self, dom: ElementTree.Element) -> None:
        graph = self.graph

        dom.append(_pretty_comment("Class Definitions"))
        types = sorted(
            {
                str(s)
                for s, _, _ in graph.triples((None, RDF.type, RDFS.Class))
                if SdoUri(s).is_sdo()
            }
        )
        for uri in types:
            self._add_type(dom, uri)

        dom.append(_pretty_comment("Property Definitions"))
        props = sorted(
            {
                str(s)
                for s, _, _ in graph.triples((None, RDF.type, RDF.Property))
                if SdoUri(s).is_sdo()
            }
        )
        for uri in props:
            self._add_prop(dom, uri)

        dom.append(_pretty_comment("Named Individuals Definitions"))
        self._add_enums(dom)
        self._add_named_individual(dom, str(SDO["True"]))
        self._add_named_individual(dom, str(SDO["False"]))

    def _add_type(self, dom: ElementTree.Element, uri: str) -> None:
        typ = ElementTree.SubElement(dom, "owl:Class", {"rdf:about": uri})
        ext: str | None = None
        for p, o in self._sorted_predicate_objects(uri):
            if p == RDFS.label:
                typ.append(_text_element("rdfs:label", str(o), {"xml:lang": "en"}))
            elif p == RDFS.comment:
                typ.append(
                    _text_element(
                        "rdfs:comment",
                        Markdown.parse(str(o), wpre="/"),
                        {"xml:lang": "en"},
                    )
                )
            elif p == RDFS.subClassOf:
                ElementTree.SubElement(
                    typ, "rdfs:subClassOf", {"rdf:resource": str(o)}
                )
            elif p == SDO.isPartOf:
                ext = str(o)
            elif p == RDF.type and o == SDO.DataType:
                ElementTree.SubElement(
                    typ, "rdfs:subClassOf", {"rdf:resource": str(SDO.DataType)}
                )

        typ.append(_defined_by(uri, ext))

    def _add_prop(self, dom: ElementTree.Element, uri: str) -> None:
        children: list[ElementTree.Element] = []
        domains: set[str] = set()
        ranges: list[str] = []
        datatype_only = True
        ext: str | None = None

        for p, o in self._sorted_predicate_objects(uri):
            if p == RDFS.label:
                children.append(
                    _text_element("rdfs:label", str(o), {"xml:lang": "en"})
                )
            elif p == RDFS.comment:
                children.append(
                    _text_element(
                        "rdfs:comment",
                        Markdown.parse(str(o), wpre="/"),
                        {"xml:lang": "en"},
                    )
                )
            elif p == RDFS.subPropertyOf:
                # Fixes a special case with schema:additionalType.
                subval = (
                    "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
                    if str(o) == "rdf:type"
                    else str(o)
                )
                children.append(
                    ElementTree.Element(
                        "rdfs:subPropertyOf", {"rdf:resource": subval}
                    )
                )
            elif p == SDO.inverseOf:
                children.append(
                    ElementTree.Element("owl:inverseOf", {"rdf:resource": str(o)})
                )
            elif p == SDO.supersededBy:
                children.append(
                    ElementTree.Element(
                        "schema:supersededBy", {"rdf:resource": str(o)}
                    )
                )
            elif p == SDO.domainIncludes:
                domains.add(str(o))
            elif p == SDO.rangeIncludes:
                ranges.append(str(o))
                if str(o) not in DATATYPES:
                    datatype_only = False
            elif p == SDO.isPartOf:
                ext = str(o)

        children.append(_defined_by(uri, ext))

        if not datatype_only:
            ranges.extend(r for r in sorted(DEFAULTRANGES) if r not in ranges)
        if domains:
            children.append(_union_element("rdfs:domain", domains))
        if ranges:
            children.append(_union_element("rdfs:range", ranges))

        tag = "owl:DatatypeProperty" if datatype_only else "owl:ObjectProperty"
        prop = ElementTree.SubElement(dom, tag, {"rdf:about": uri})
        prop.extend(children)

    def _add_enums(self, dom: ElementTree.Element) -> None:
        pairs = sorted({
            (str(enum), str(parent))
            for parent in self.graph.subjects(RDFS.subClassOf, SDO.Enumeration)
            for enum in self.graph.subjects(RDFS.subClassOf, parent)
        })
        for enum_uri, parent_uri in pairs:
            self._add_named_individual(dom, enum_uri, parent=parent_uri)

    def _add_named_individual(
        self,
        dom: ElementTree.Element,
        individual: str,
        parent: str | None = None,
    ) -> None:
        typ = ElementTree.SubElement(
            dom, "owl:NamedIndividual", {"rdf:about": individual}
        )
        ext: str | None = None
        for p, o in self._sorted_predicate_objects(individual):
            if p == RDFS.label:
                typ.append(_text_element("rdfs:label", str(o), {"xml:lang": "en"}))
            elif p == RDFS.comment:
                typ.append(
                    _text_element(
                        "rdfs:comment",
                        Markdown.parse(str(o), wpre="/"),
                        {"xml:lang": "en"},
                    )
                )
            elif p == SDO.isPartOf:
                ext = str(o)

        typ.append(_defined_by(individual, ext))
        if parent:
            ElementTree.SubElement(
                typ, "rdfs:subClassOf", {"rdf:resource": parent}
            )
