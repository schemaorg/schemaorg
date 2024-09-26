#!/usr/bin/env python3
# -*- coding: UTF-8 -*-


class SdoTerm:
    """Abstract superclass for various schema.org types."""

    TYPE = "Type"
    PROPERTY = "Property"
    DATATYPE = "Datatype"
    ENUMERATION = "Enumeration"
    ENUMERATIONVALUE = "Enumerationvalue"
    REFERENCE = "Reference"

    def __init__(self, termType, Id, uri, label):
        self.expanded = False
        self.termType = termType
        self.uri = uri
        self.id = Id
        self.label = label

        self.acknowledgements = []
        self.superPaths = []
        self.comment = ""
        self.comments = []
        self.equivalents = []
        self.examples = []
        self.pending = False
        self.retired = False
        self.extLayer = ""
        self.sources = []
        self.subs = []
        self.supers = []
        self.supersededBy = ""
        self.supersedes = ""
        self.superseded = False
        self.termStack = []

    def __str__(self):
        return ("<%s: '%s' expanded: %s>") % (
            self.__class__.__name__.upper(),
            self.id,
            self.expanded,
        )


class SdoType(SdoTerm):
    """Term that defines a schema.org type"""

    def __init__(self, Id, uri, label):
        SdoTerm.__init__(self, SdoTerm.TYPE, Id, uri, label)

        self.properties = []
        self.allproperties = []
        self.expectedTypeFor = []


class SdoProperty(SdoTerm):
    """Term that defines a propery of another type."""

    def __init__(self, Id, uri, label):
        SdoTerm.__init__(self, SdoTerm.PROPERTY, Id, uri, label)
        self.domainIncludes = []
        self.rangeIncludes = []
        self.inverse = ""


class SdoDataType(SdoTerm):
    """Term that defines one of the basic data-types: Boolean, Date, Text, Number etc."""

    def __init__(self, Id, uri, label):
        SdoTerm.__init__(self, SdoTerm.DATATYPE, Id, uri, label)

        self.properties = []
        self.allproperties = []
        self.expectedTypeFor = []


class SdoEnumeration(SdoTerm):
    """Term that defines a schema.org enumeration."""

    def __init__(self, Id, uri, label):
        SdoTerm.__init__(self, SdoTerm.ENUMERATION, Id, uri, label)
        self.properties = []
        self.allproperties = []
        self.expectedTypeFor = []
        self.enumerationMembers = []


class SdoEnumerationvalue(SdoTerm):
    """Term that defines a value within a schema.org enumeration."""

    def __init__(self, Id, uri, label):
        SdoTerm.__init__(self, SdoTerm.ENUMERATIONVALUE, Id, uri, label)
        self.enumerationParent = ""


class SdoReference(SdoTerm):
    def __init__(self, Id, uri, label):
        SdoTerm.__init__(self, SdoTerm.REFERENCE, Id, uri, label)
