#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import enum
import logging
import collections
from typing import Any, Dict, List, Optional, Tuple, Type, TypeVar, Union, Iterable, Set

log: logging.Logger = logging.getLogger(__name__)

class SdoTermType(str, enum.Enum):
    """Enumeration describing the type of an SdoTerm."""

    TYPE = "Type"
    PROPERTY = "Property"
    DATATYPE = "Datatype"
    ENUMERATION = "Enumeration"
    ENUMERATIONVALUE = "Enumerationvalue"
    REFERENCE = "Reference"

    def __str__(self) -> str:
        return self.value

class UnexpandedTermError(LookupError):
    """Term is not expanded."""


class SdoTermOrId(object):
    """Wrapper that holds a term-id or a term, or nothing."""

    def __init__(self, term_id: Optional[str] = None, term: Optional["SdoTerm"] = None) -> None:
        # Empty instance is fine.
        assert not (term_id and term), f"{term_id} {term}"
        self._term_id: Optional[str] = None
        if term:
            self._term_id = term.id
        else:
            self._term_id = term_id
        self._term: Optional["SdoTerm"] = term

    @property
    def expanded(self) -> bool:
        return not self._term_id or bool(self._term)

    @property
    def id(self) -> Optional[str]:
        return self._term_id

    @property
    def term(self) -> "SdoTerm":
        if not self._term:
             raise UnexpandedTermError()
        return self._term

    def setId(self, term_id: Optional[str]) -> None:
        self._term_id = term_id

    def setTerm(self, term: Optional["SdoTerm"]) -> None:
        self._term = term
        if self._term:
            self._term_id = term.id

    def __str__(self) -> str:
        if not self._term:
            return f'{self._term_id}'
        return str(self._term)

    def __bool__(self) -> bool:
        return bool(self._term_id)


class SdoTermSequence(object):
    """Sequence that holds either a sequence of term-ids, or a sequence of terms.

    If it holds a sequence of terms, the sequence is said to be expanded.
    It can only be changed by replacing all the values, either with ids, or term instances.

    """
    def __init__(self) -> None:
        self._term_dict: collections.OrderedDict[str, Optional["SdoTerm"]] = collections.OrderedDict()

    @classmethod
    def forElements(cls, elements: Iterable[Any]) -> "SdoTermSequence":
        """Convert an arbitrary sequence into a SdoTermSequence."""
        if isinstance(elements, cls):
            return elements

        sequence: SdoTermSequence = cls()
        elements_list = list(elements)
        if all(map(lambda e : isinstance(e, SdoTerm), elements_list)):
            sequence.setTerms(elements_list)
            return sequence
        term_ids: List[str] = []
        for element in elements_list:
            try:
                # This will work for both SdoTerm instances, and SdoTermOrId
                term_id: str = element.id
            except AttributeError:
                term_id = str(element)
            term_ids.append(term_id)
        sequence.setIds(term_ids)
        return sequence

    @property
    def expanded(self) -> bool:
        return all(self._term_dict.values())

    @property
    def ids(self) -> Tuple[str, ...]:
        return tuple(self._term_dict.keys())

    @property
    def terms(self) -> Tuple["SdoTerm", ...]:
        if not self.expanded:
          raise UnexpandedTermError()
        return tuple(self._term_dict.values()) # type: ignore

    def setIds(self, term_ids: Iterable[str]) -> None:
        self._term_dict.clear()
        for term_id in term_ids:
            self._term_dict[term_id] = None

    def setTerms(self, terms: Iterable["SdoTerm"]) -> None:
        self._term_dict.clear()
        for term in terms:
            self._term_dict[term.id] = term

    def clear(self) -> None:
        self._term_dict.clear()

    def __bool__(self) -> bool:
        return bool(self._term_dict)

    def __len__(self) -> int:
        return len(self._term_dict)

    def __contains__(self, value: str) -> bool:
        return value in self._term_dict

    def __iter__(self) -> Iterable[str]:
        return iter(self.ids)

    def __str__(self) -> str:
        return '[' + ','.join(map(str, self.ids)) + ']'


class SdoTerm(object):
    """Abstract superclass for various schema.org types.

    Note that the semantics of the relational fields depends on the expansion_depth.

    0: Nothing is expanded
    1: Non recursive fields are expanded
    2: All recursive fields are expanded (and are at least at level 1)

    """


    TYPE_LIKE_TYPES: Set[SdoTermType] = frozenset(
        [SdoTermType.TYPE, SdoTermType.DATATYPE, SdoTermType.ENUMERATION]
    )

    def __init__(self, termType: SdoTermType, term_id: str, uri: str, label: str) -> None:
        if type(self) == SdoTerm:
            raise Exception("<SdoTerm> must be subclassed.")

        assert isinstance(term_id, str)
        self._expansion_depth: int = 0
        self.termType: SdoTermType = termType
        self.uri: str = uri
        self._term_id: str = term_id
        self.label: str = label

        self.acknowledgements: List[Any] = []

        self.comment: str = ""
        self.comments: List[str] = []

        self.examples: List[Any] = []
        self.pending: bool = False
        self.retired: bool = False
        self.extLayer: str = ""
        self.sources: List[str] = []


        self.supersededBy: str = ""
        self.supersedes: List[str] = []
        self.superseded: bool = False
        self.superPaths: List[Any] = []

        self._termStack: SdoTermSequence = SdoTermSequence()
        self._supers: SdoTermSequence = SdoTermSequence()
        self._subs: SdoTermSequence = SdoTermSequence()
        self._equivalents: SdoTermSequence = SdoTermSequence()


    def __str__(self) -> str:
        return ("<%s: '%s' expansion depth: %s >") % (
            self.__class__.__name__.upper(),
            self.id,
            self._expansion_depth,
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, SdoTerm):
             return False
        return self.id == other.id

    def __lt__(self, other: "SdoTerm") -> bool:
        return self.id < other.id

    def markExpanded(self, depth: int) -> None:
        self._expansion_depth = depth

    def expanded(self) -> bool:
        return self._expansion_depth > 1

    @property
    def supers(self) -> SdoTermSequence:
        return self._supers

    @property
    def subs(self) -> SdoTermSequence:
        return self._subs

    @property
    def equivalents(self) -> SdoTermSequence:
        return self._equivalents

    @property
    def termStack(self) -> SdoTermSequence:
        return self._termStack

    @property
    def id(self) -> str:
        return self._term_id

class SdoType(SdoTerm):
    """Term that defines a schema.org type"""

    def __init__(self, term_id: str, uri: str, label: str) -> None:
        SdoTerm.__init__(self, SdoTermType.TYPE, term_id, uri, label)

        self._properties: SdoTermSequence = SdoTermSequence()
        self._allproperties: SdoTermSequence = SdoTermSequence()
        self._expectedTypeFor: SdoTermSequence = SdoTermSequence()

    @property
    def properties(self) -> SdoTermSequence:
        return self._properties

    @property
    def allproperties(self) -> SdoTermSequence:
        return self._allproperties

    @property
    def expectedTypeFor(self) -> SdoTermSequence:
        return self._expectedTypeFor


class SdoProperty(SdoTerm):
    """Term that defines a propery of another type."""

    def __init__(self, term_id: str, uri: str, label: str) -> None:
        SdoTerm.__init__(self, SdoTermType.PROPERTY, term_id, uri, label)
        self._domainIncludes: SdoTermSequence = SdoTermSequence()
        self._rangeIncludes: SdoTermSequence = SdoTermSequence()
        self._inverse: SdoTermOrId = SdoTermOrId()

    @property
    def domainIncludes(self) -> SdoTermSequence:
        return self._domainIncludes

    @property
    def rangeIncludes(self) -> SdoTermSequence:
        return self._rangeIncludes

    @property
    def inverse(self) -> SdoTermOrId:
        return self._inverse



class SdoDataType(SdoTerm):
    """Term that defines one of the basic data-types: Boolean, Date, Text, Number etc."""

    def __init__(self, term_id: str, uri: str, label: str) -> None:
        SdoTerm.__init__(self, SdoTermType.DATATYPE, term_id, uri, label)

        self._properties: SdoTermSequence = SdoTermSequence()
        self._allproperties: SdoTermSequence = SdoTermSequence()
        self._expectedTypeFor: SdoTermSequence = SdoTermSequence()

    @property
    def properties(self) -> SdoTermSequence:
        return self._properties

    @property
    def allproperties(self) -> SdoTermSequence:
        return self._allproperties

    @property
    def expectedTypeFor(self) -> SdoTermSequence:
        return self._expectedTypeFor


class SdoEnumeration(SdoTerm):
    """Term that defines a schema.org enumeration."""

    def __init__(self, term_id: str, uri: str, label: str) -> None:
        SdoTerm.__init__(self, SdoTermType.ENUMERATION, term_id, uri, label)
        self._properties: SdoTermSequence = SdoTermSequence()
        self._allproperties: SdoTermSequence = SdoTermSequence()
        self._expectedTypeFor: SdoTermSequence = SdoTermSequence()
        self._enumerationMembers: SdoTermSequence = SdoTermSequence()

    @property
    def properties(self) -> SdoTermSequence:
        return self._properties

    @property
    def allproperties(self) -> SdoTermSequence:
        return self._allproperties

    @property
    def expectedTypeFor(self) -> SdoTermSequence:
        return self._expectedTypeFor

    @property
    def enumerationMembers(self) -> SdoTermSequence:
        return self._enumerationMembers


class SdoEnumerationvalue(SdoTerm):
    """Term that defines a value within a schema.org enumeration."""

    def __init__(self, term_id: str, uri: str, label: str) -> None:
        SdoTerm.__init__(self, SdoTermType.ENUMERATIONVALUE, term_id, uri, label)
        self._enumerationParent: SdoTermOrId = SdoTermOrId()

    @property
    def enumerationParent(self) -> SdoTermOrId:
        return self._enumerationParent


class SdoReference(SdoTerm):
    def __init__(self, term_id: str, uri: str, label: str) -> None:
        SdoTerm.__init__(self, SdoTermType.REFERENCE, term_id, uri, label)


_TYPES_FOR_TYPES: Dict[SdoTermType, Type[SdoTerm]] = {
    SdoTermType.TYPE: SdoType,
    SdoTermType.DATATYPE: SdoDataType,
    SdoTermType.PROPERTY: SdoProperty,
    SdoTermType.ENUMERATION: SdoEnumeration,
    SdoTermType.ENUMERATIONVALUE: SdoEnumerationvalue,
    SdoTermType.REFERENCE: SdoReference
}


def SdoTermforType(term_type: SdoTermType, **kwargs: Any) -> SdoTerm:
    t: Type[SdoTerm] = _TYPES_FOR_TYPES[term_type]
    return t(**kwargs)
