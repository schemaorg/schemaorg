#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import standard python libraries
import enum
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Type, Union, Iterable, Set, Sequence, FrozenSet

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


class SdoTermOrId:
    """Wrapper that holds a term-id or a term, or nothing."""

    def __init__(self, term_id: Optional[str] = None, term: Optional["SdoTerm"] = None) -> None:
        assert not (term_id and term), f"{term_id} {term}"
        self._term_id = term.id if term else term_id
        self._term = term

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
        if term:
            self._term_id = term.id

    def __str__(self) -> str:
        return str(self._term or self._term_id)

    def __bool__(self) -> bool:
        return bool(self._term_id)


class SdoTermSequence:
    """Sequence that holds either a sequence of term-ids, or a sequence of terms."""

    def __init__(self) -> None:
        self._term_dict: Dict[str, Optional["SdoTerm"]] = {}

    @classmethod
    def forElements(cls, elements: Iterable[Any]) -> "SdoTermSequence":
        """Convert an arbitrary sequence into a SdoTermSequence."""
        if isinstance(elements, cls):
            return elements

        sequence = cls()
        elements_list = list(elements)
        if all(isinstance(e, SdoTerm) for e in elements_list):
            sequence.setTerms(elements_list)
            return sequence

        term_ids = []
        for element in elements_list:
            if hasattr(element, "id"):
                term_ids.append(element.id)
            else:
                term_ids.append(str(element))
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
        return tuple(self._term_dict.values())  # type: ignore

    def setIds(self, term_ids: Iterable[str]) -> None:
        self._term_dict = {tid: None for tid in term_ids}

    def setTerms(self, terms: Iterable["SdoTerm"]) -> None:
        self._term_dict = {t.id: t for t in terms}

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
        return f'[{", ".join(self.ids)}]'


class SdoTerm(ABC):
    """Abstract superclass for various schema.org types."""

    TYPE_LIKE_TYPES: FrozenSet[SdoTermType] = frozenset(
        {SdoTermType.TYPE, SdoTermType.DATATYPE, SdoTermType.ENUMERATION}
    )

    def __init__(self, termType: SdoTermType, term_id: str, uri: str, label: str) -> None:
        assert isinstance(term_id, str)
        self._expansion_depth = 0
        self.termType = termType
        self.uri = uri
        self._term_id = term_id
        self.label = label

        self.acknowledgements: List[Any] = []
        self.comment = ""
        self.comments: List[str] = []
        self.examples: List[Any] = []
        self.pending = False
        self.retired = False
        self.extLayer = ""
        self.sources: List[str] = []
        self.supersededBy = ""
        self.supersedes: List[str] = []
        self.superseded = False
        self.superPaths: List[Any] = []

        self._termStack = SdoTermSequence()
        self._supers = SdoTermSequence()
        self._subs = SdoTermSequence()
        self._equivalents = SdoTermSequence()

    def __str__(self) -> str:
        return f"<{self.__class__.__name__.upper()}: '{self.id}' expansion depth: {self._expansion_depth}>"

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


class _SdoTypeLike(SdoTerm):
    def __init__(self, termType: SdoTermType, term_id: str, uri: str, label: str) -> None:
        super().__init__(termType, term_id, uri, label)
        self._properties = SdoTermSequence()
        self._allproperties = SdoTermSequence()
        self._expectedTypeFor = SdoTermSequence()

    @property
    def properties(self) -> SdoTermSequence:
        return self._properties

    @property
    def allproperties(self) -> SdoTermSequence:
        return self._allproperties

    @property
    def expectedTypeFor(self) -> SdoTermSequence:
        return self._expectedTypeFor


class SdoType(_SdoTypeLike):
    """Term that defines a schema.org type"""
    def __init__(self, term_id: str, uri: str, label: str) -> None:
        super().__init__(SdoTermType.TYPE, term_id, uri, label)


class SdoProperty(SdoTerm):
    """Term that defines a property of another type."""
    def __init__(self, term_id: str, uri: str, label: str) -> None:
        super().__init__(SdoTermType.PROPERTY, term_id, uri, label)
        self._domainIncludes = SdoTermSequence()
        self._rangeIncludes = SdoTermSequence()
        self._inverse = SdoTermOrId()

    @property
    def domainIncludes(self) -> SdoTermSequence:
        return self._domainIncludes

    @property
    def rangeIncludes(self) -> SdoTermSequence:
        return self._rangeIncludes

    @property
    def inverse(self) -> SdoTermOrId:
        return self._inverse


class SdoDataType(_SdoTypeLike):
    """Term that defines one of the basic data-types: Boolean, Date, Text, Number etc."""
    def __init__(self, term_id: str, uri: str, label: str) -> None:
        super().__init__(SdoTermType.DATATYPE, term_id, uri, label)


class SdoEnumeration(_SdoTypeLike):
    """Term that defines a schema.org enumeration."""
    def __init__(self, term_id: str, uri: str, label: str) -> None:
        super().__init__(SdoTermType.ENUMERATION, term_id, uri, label)
        self._enumerationMembers = SdoTermSequence()

    @property
    def enumerationMembers(self) -> SdoTermSequence:
        return self._enumerationMembers


class SdoEnumerationvalue(SdoTerm):
    """Term that defines a value within a schema.org enumeration."""
    def __init__(self, term_id: str, uri: str, label: str) -> None:
        super().__init__(SdoTermType.ENUMERATIONVALUE, term_id, uri, label)
        self._enumerationParent = SdoTermOrId()

    @property
    def enumerationParent(self) -> SdoTermOrId:
        return self._enumerationParent


class SdoReference(SdoTerm):
    def __init__(self, term_id: str, uri: str, label: str) -> None:
        super().__init__(SdoTermType.REFERENCE, term_id, uri, label)


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
