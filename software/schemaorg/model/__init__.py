#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Pydantic-RDF models and Vocabulary container for schema.org."""

from schemaorg.model.loader import VocabularyLoader
from schemaorg.model.terms import (
    DataType,
    EnumerationValue,
    SchemaProperty,
    SchemaTerm,
    SchemaType,
)
from schemaorg.model.vocabulary import Vocabulary
from schemaorg.sdo_uri import SDO, SdoUri

__all__ = [
    "DataType",
    "EnumerationValue",
    "SDO",
    "SchemaProperty",
    "SchemaTerm",
    "SchemaType",
    "SdoUri",
    "Vocabulary",
    "VocabularyLoader",
]
