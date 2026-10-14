#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Loader that populates flat pydantic-rdf models and builds a Vocabulary."""

from typing import Dict, Optional, Set, Tuple

import rdflib
from rdflib import RDFS, URIRef

from schemaorg.model.terms import (
    DataType,
    EnumerationValue,
    SchemaProperty,
    SchemaType,
)
from schemaorg.model.vocabulary import Vocabulary
from schemaorg.sdo_uri import SDO, SdoUri
from schemaorg.version import VersionItem


class VocabularyLoader:
    """Extracts SchemaType, DataType, SchemaProperty, and EnumerationValue from a graph."""

    def __init__(
        self, graph: rdflib.Graph, version: Optional[VersionItem] = None
    ) -> None:
        self.graph = graph
        self.version = version

    def load_terms(
        self,
    ) -> Tuple[
        Dict[URIRef, SchemaType],
        Dict[URIRef, SchemaProperty],
        Dict[URIRef, EnumerationValue],
        Dict[URIRef, DataType],
    ]:
        # Extract all schema.org classes (rdf:type rdfs:Class), excluding external URIs.
        types: Dict[URIRef, SchemaType] = {
            t.uri: t
            for t in SchemaType.all_entities(self.graph)
            if SdoUri(t.uri).is_sdo()
        }

        # Extract primitive datatypes (rdf:type schema:DataType, e.g. Text, Number, Boolean).
        datatypes: Dict[URIRef, DataType] = {
            dt.uri: dt
            for dt in DataType.all_entities(self.graph)
            if SdoUri(dt.uri).is_sdo()
        }
        # Root schema:DataType has rdf:type rdfs:Class (not schema:DataType); promote it.
        if SDO.DataType in types and SDO.DataType not in datatypes:
            datatypes[SDO.DataType] = DataType(**types[SDO.DataType].model_dump())

        # Primitive datatypes carry both rdfs:Class and schema:DataType; store the
        # narrower DataType instance in `types` as well.
        for dt_uri, dt in datatypes.items():
            if dt_uri in types:
                types[dt_uri] = dt

        # Boolean literals (True, False) have rdf:type schema:Boolean rather than
        # rdfs:Class; probe each datatype class for direct value instances.
        for dt_uri in list(datatypes.keys()):
            if dt_uri == SDO.DataType:
                continue
            dt_name = SdoUri(dt_uri).term_name()
            dt_value_cls = type(
                f"DT_{dt_name}", (DataType,), {"rdf_type": dt_uri}
            )
            for inst in dt_value_cls.all_entities(self.graph):
                if SdoUri(inst.uri).is_sdo() and inst.uri not in datatypes:
                    datatypes[inst.uri] = DataType(**inst.model_dump())

        # Extract all schema.org properties (rdf:type rdf:Property).
        properties: Dict[URIRef, SchemaProperty] = {
            p.uri: p
            for p in SchemaProperty.all_entities(self.graph)
            if SdoUri(p.uri).is_sdo()
        }

        # Walk rdfs:subClassOf downward from schema:Enumeration to find all
        # enumeration classes (including multi-level ones like MedicalSpecialty).
        sup_to_sub: Dict[URIRef, Set[URIRef]] = {}
        for s, o in self.graph.subject_objects(RDFS.subClassOf):
            if isinstance(s, URIRef) and isinstance(o, URIRef):
                sup_to_sub.setdefault(o, set()).add(s)

        enum_classes: Set[URIRef] = set()
        if SDO.Enumeration in types:
            stack = [SDO.Enumeration]
            while stack:
                cur = stack.pop()
                if cur not in enum_classes and cur in types:
                    enum_classes.add(cur)
                    stack.extend(sup_to_sub.get(cur, ()))

        # Enumeration members have rdf:type <SubEnumeration> (e.g. schema:DayOfWeek),
        # not rdf:type schema:Enumeration. Synthesize a temporary model per enum
        # class so pydantic-rdf can query its instances, then re-wrap as top-level
        # EnumerationValue so instances remain picklable.
        enum_values: Dict[URIRef, EnumerationValue] = {}
        for ec in sorted(enum_classes, key=str):
            ec_name = SdoUri(ec).term_name()
            ev_cls = type(
                f"EV_{ec_name}", (EnumerationValue,), {"rdf_type": ec}
            )
            for ev in ev_cls.all_entities(self.graph):
                if (
                    SdoUri(ev.uri).is_sdo()
                    and ev.uri not in types
                    and ev.uri not in properties
                    and ev.uri not in enum_values
                ):
                    enum_values[ev.uri] = EnumerationValue(**ev.model_dump())

        return types, properties, enum_values, datatypes

    def load(self, version: Optional[VersionItem] = None) -> Vocabulary:
        types, properties, enum_values, datatypes = self.load_terms()
        return Vocabulary(
            version=version or self.version,
            types=types,
            properties=properties,
            enum_values=enum_values,
            datatypes=datatypes,
        )
