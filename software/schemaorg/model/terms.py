#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Flat RDF models for schema.org vocabulary terms."""

from typing import Annotated, List, Optional

from pydantic import model_validator
from pydantic_rdf import BaseRdfModel, WithPredicate
from rdflib import OWL, RDF, RDFS, URIRef

from schemaorg.sdo_uri import SDO, SdoUri


class SchemaTerm(BaseRdfModel):
    """Flat base shape for schema.org terms; references are always URIRefs."""

    _rdf_namespace = SDO

    label: Annotated[Optional[str], WithPredicate(RDFS.label)] = None
    comment: Annotated[Optional[str], WithPredicate(RDFS.comment)] = None
    isPartOf: Annotated[List[URIRef], WithPredicate(SDO.isPartOf)] = []
    source: Annotated[List[URIRef], WithPredicate(SDO.source)] = []
    contributor: Annotated[List[URIRef], WithPredicate(SDO.contributor)] = []
    supersededBy: Annotated[List[URIRef], WithPredicate(SDO.supersededBy)] = []
    rdf_types: Annotated[List[URIRef], WithPredicate(RDF.type)] = []

    @model_validator(mode="after")
    def _sort_uri_lists(self) -> "SchemaTerm":
        for name in type(self).model_fields:
            val = getattr(self, name, None)
            if isinstance(val, list) and len(val) > 1:
                val.sort(key=str)
        return self

    @property
    def id(self) -> str:
        return SdoUri(self.uri).term_name()

    def __hash__(self) -> int:
        return hash(self.uri)


class SchemaType(SchemaTerm):
    """Schema.org class (rdfs:Class)."""

    rdf_type = RDFS.Class

    supers: Annotated[List[URIRef], WithPredicate(RDFS.subClassOf)] = []
    equivalents: Annotated[List[URIRef], WithPredicate(OWL.equivalentClass)] = []


class DataType(SchemaType):
    """Schema.org primitive data type (schema:DataType) or boolean literal."""

    rdf_type = SDO.DataType


class SchemaProperty(SchemaTerm):
    """Schema.org property (rdf:Property)."""

    rdf_type = RDF.Property

    supers: Annotated[List[URIRef], WithPredicate(RDFS.subPropertyOf)] = []
    domainIncludes: Annotated[List[URIRef], WithPredicate(SDO.domainIncludes)] = []
    rangeIncludes: Annotated[List[URIRef], WithPredicate(SDO.rangeIncludes)] = []
    inverseOf: Annotated[List[URIRef], WithPredicate(SDO.inverseOf)] = []
    equivalents: Annotated[List[URIRef], WithPredicate(OWL.equivalentProperty)] = []


class EnumerationValue(SchemaTerm):
    """Member instance of a schema:Enumeration subclass."""

    rdf_type = SDO.Enumeration

    supers: Annotated[List[URIRef], WithPredicate(RDFS.subClassOf)] = []
    equivalents: Annotated[List[URIRef], WithPredicate(OWL.equivalentClass)] = []
