#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import enum
import logging
import collections

log = logging.getLogger(__name__)

class SdoTermType(str, enum.Enum):
    """Enumeration describing the type of an SdoTerm."""

    TYPE = "Type"
    PROPERTY = "Property"
    DATATYPE = "Datatype"
    ENUMERATION = "Enumeration"
    ENUMERATIONVALUE = "Enumerationvalue"
    REFERENCE = "Reference"

    def __str__(self):
        return self.value

class UnexpandedTermError(LookupError):
    """Term is not expanded."""


class SdoTermOrId(object):

    def __init__(self, term_id : str = None, term = None):
        self._term = term
        if term:
            self._term_id = term.id
            assert not term_id or term_id == term.id
        else:
            self._term_id = term_id

    @property
    def expanded(self) -> bool:
        return not self._term_id or bool(self._term)

    @property
    def id(self) -> str:
        return self._term_id

    @property
    def term(self):
        if not self._term:
             raise UnexpandedTermError()
        return self._term

    def setId(self, term_id):
        self._term_id = term_id

    def setTerm(self, term):
        self._term = term
        if self._term:
            self._term_id = term.id

    def __str__(self):
        if not self._term:
            return '<%s>' % self._term_id
        return str(self._term)

    def __bool__(self):
        return bool(self._term_id)


class SdoTermSequence(object):
    """Sequence that holds either a sequence of term-ids, or a sequence of terms.

    If it holds a sequence of terms, the sequence is said to expanded.

    """
    def __init__(self):
        self._term_dict = collections.OrderedDict()

    @classmethod
    def forElements(cls, elements):
        if isinstance(elements, cls):
            return elements

        sequence = cls()
        if all(map(lambda e : isinstance(e, SdoTerm), elements)):
            sequence.setTerms(elements)
            return sequence
        term_ids = []
        for element in elements:
            try:
                term_id = element.id
            except AttributeError:
                term_id = element
            term_ids.append(term_id)
        sequence.setIds(term_ids)
        return sequence

    @property
    def expanded(self):
        return not self._term_dict or all(self._term_dict.values())

    @property
    def ids(self):
        return tuple(self._term_dict.keys())

    @property
    def terms(self):
        if not self.expanded:
          raise UnexpandedTermError()
        return tuple(self._term_dict.values())

    def setIds(self, term_ids):
        self._term_dict.clear()
        for term_id in term_ids:
            self._term_dict[term_id] = None

    def setTerms(self, terms):
        self._term_dict.clear()
        for term in terms:
            self._term_dict[term.id] = term

    def clear(self):
        self._term_dict.clear()

    def __bool__(self):
        return bool(self._term_dict)

    def __len__(self):
        return len(self._term_dict)

    def __contains__(self, value):
        return value in self._term_dict.keys()

    def __str__(self):
        return '[' + ','.join(map(str, self.ids)) + ']'


class SdoTerm(object):
    """Abstract superclass for various schema.org types.

    Note that the semantics of the relational fields depends on the expansion_depth.

    0: Nothing is expanded
    1: Non recursive fields are expanded
    2: All recursive fields are expanded (at are at least at level 1)

    """


    TYPE_LIKE_TYPES = frozenset(
        [SdoTermType.TYPE, SdoTermType.DATATYPE, SdoTermType.ENUMERATION]
    )

    def __init__(self, termType: SdoTermType, term_id: str, uri: str, label: str):
        if type(self) == SdoTerm:
            raise Exception("<SdoTerm> must be subclassed.")

        assert isinstance(term_id, str)
        self._expansion_depth = 0
        self.termType = termType
        self.uri = uri
        self._term_id = term_id
        self.label = label

        self.acknowledgements = []

        self.comment = ""
        self.comments = []

        self.examples = []
        self.pending = False
        self.retired = False
        self.extLayer = ""
        self.sources = []


        self.supersededBy = ""
        self.supersedes = ""
        self.superseded = False
        self.superPaths = []

        self._termStack = SdoTermSequence()
        self._supers = SdoTermSequence()
        self._subs = SdoTermSequence()
        self._equivalents = SdoTermSequence()


    def __str__(self):
        return ("<%s: '%s' expansion depth: %s >") % (
            self.__class__.__name__.upper(),
            self.id,
            self._expansion_depth,
        )

    def __eq__(self, other):
        return self.id == other.id

    def __lt__(self, other):
        return self.id < other.id

    def markExpanded(self, depth : int):
        self._expansion_depth = depth

    def expanded(self):
        return self._expansion_depth > 1

    @property
    def supers(self):
        return self._supers;

    @property
    def subs(self):
        return self._subs;

    @property
    def equivalents(self):
        return self._equivalents

    @property
    def termStack(self):
        return self._termStack

    @property
    def id(self) -> str:
        return self._term_id


class SdoType(SdoTerm):
    """Term that defines a schema.org type"""

    def __init__(self, Id: str, uri: str, label: str):
        SdoTerm.__init__(self, SdoTermType.TYPE, Id, uri, label)

        self._properties = SdoTermSequence()
        self._allproperties = SdoTermSequence()
        self._expectedTypeFor = SdoTermSequence()

    @property
    def properties(self):
        return self._properties

    @property
    def allproperties(self):
        return self._allproperties

    @property
    def expectedTypeFor(self):
        return self._expectedTypeFor


class SdoProperty(SdoTerm):
    """Term that defines a propery of another type."""

    def __init__(self, Id: str, uri: str, label: str):
        SdoTerm.__init__(self, SdoTermType.PROPERTY, Id, uri, label)
        self._domainIncludes = SdoTermSequence()
        self._rangeIncludes = SdoTermSequence()
        self._inverse = SdoTermOrId()

    @property
    def domainIncludes(self):
        return self._domainIncludes

    @property
    def rangeIncludes(self):
        return self._rangeIncludes

    @property
    def inverse(self):
        return self._inverse



class SdoDataType(SdoTerm):
    """Term that defines one of the basic data-types: Boolean, Date, Text, Number etc."""

    def __init__(self, Id: str, uri: str, label: str):
        SdoTerm.__init__(self, SdoTermType.DATATYPE, Id, uri, label)

        self._properties = SdoTermSequence()
        self._allproperties = SdoTermSequence()
        self._expectedTypeFor = SdoTermSequence()

    @property
    def properties(self):
        return self._properties

    @property
    def allproperties(self):
        return self._allproperties

    @property
    def expectedTypeFor(self):
        return self._expectedTypeFor


class SdoEnumeration(SdoTerm):
    """Term that defines a schema.org enumeration."""

    def __init__(self, Id: str, uri: str, label: str):
        SdoTerm.__init__(self, SdoTermType.ENUMERATION, Id, uri, label)
        self._properties = SdoTermSequence()
        self._allproperties = SdoTermSequence()
        self._expectedTypeFor = SdoTermSequence()
        self._enumerationMembers = SdoTermSequence()

    @property
    def properties(self):
        return self._properties

    @property
    def allproperties(self):
        return self._allproperties

    @property
    def expectedTypeFor(self):
        return self._expectedTypeFor

    @property
    def enumerationMembers(self):
        return self._enumerationMembers


class SdoEnumerationvalue(SdoTerm):
    """Term that defines a value within a schema.org enumeration."""

    def __init__(self, Id: str, uri: str, label: str):
        SdoTerm.__init__(self, SdoTermType.ENUMERATIONVALUE, Id, uri, label)
        self._enumerationParent = SdoTermOrId()

    @property
    def enumerationParent(self):
        return self._enumerationParent


class SdoReference(SdoTerm):
    def __init__(self, Id: str, uri: str, label: str):
        SdoTerm.__init__(self, SdoTermType.REFERENCE, Id, uri, label)
