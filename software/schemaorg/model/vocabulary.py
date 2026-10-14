#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Pre-indexed container for the schema.org vocabulary."""

from dataclasses import dataclass, field
from typing import Dict, FrozenSet, List, Mapping, Optional, Set, Tuple, Union

from rdflib import URIRef

from schemaorg.model.terms import (
    DataType,
    EnumerationValue,
    SchemaProperty,
    SchemaTerm,
    SchemaType,
)
from schemaorg.sdo_uri import SDO, SdoUri
from schemaorg.version import VersionItem


@dataclass
class Vocabulary:
    """Vocabulary container with precomputed relationship indexes."""

    version: Optional[VersionItem] = None
    types: Mapping[URIRef, SchemaType] = field(default_factory=dict)
    properties: Mapping[URIRef, SchemaProperty] = field(default_factory=dict)
    enum_values: Mapping[URIRef, EnumerationValue] = field(default_factory=dict)
    datatypes: Mapping[URIRef, DataType] = field(default_factory=dict)

    enumerations: FrozenSet[URIRef] = field(init=False)
    declared_properties: Mapping[URIRef, Tuple[URIRef, ...]] = field(init=False)
    expected_type_for: Mapping[URIRef, Tuple[URIRef, ...]] = field(init=False)
    subs: Mapping[URIRef, Tuple[URIRef, ...]] = field(init=False)
    enumeration_members: Mapping[URIRef, Tuple[URIRef, ...]] = field(init=False)
    ancestors: Mapping[URIRef, Tuple[URIRef, ...]] = field(init=False)
    all_properties: Mapping[URIRef, Tuple[URIRef, ...]] = field(init=False)
    supersedes: Mapping[URIRef, Tuple[URIRef, ...]] = field(init=False)

    def __post_init__(self) -> None:
        self.types = dict(self.types)
        self.properties = dict(self.properties)
        self.enum_values = dict(self.enum_values)
        self.datatypes = (
            dict(self.datatypes)
            if self.datatypes
            else {
                u: t
                for u, t in self.types.items()
                if isinstance(t, DataType)
            }
        )

        all_terms: Dict[URIRef, SchemaTerm] = {
            **self.types,
            **self.datatypes,
            **self.properties,
            **self.enum_values,
        }

        declared_raw: Dict[URIRef, Set[URIRef]] = {}
        expected_raw: Dict[URIRef, Set[URIRef]] = {}
        subs_raw: Dict[URIRef, Set[URIRef]] = {}
        supersedes_raw: Dict[URIRef, Set[URIRef]] = {}

        for p in self.properties.values():
            for d in p.domainIncludes:
                declared_raw.setdefault(d, set()).add(p.uri)
            for r in p.rangeIncludes:
                expected_raw.setdefault(r, set()).add(p.uri)
            for sup in p.supers:
                if SdoUri(sup).is_sdo():
                    subs_raw.setdefault(sup, set()).add(p.uri)

        for t in self.types.values():
            for sup in t.supers:
                if SdoUri(sup).is_sdo():
                    subs_raw.setdefault(sup, set()).add(t.uri)

        for ev in self.enum_values.values():
            for sup in ev.supers:
                if SdoUri(sup).is_sdo():
                    subs_raw.setdefault(sup, set()).add(ev.uri)

        # DataType children (Boolean -> DataType, True -> Boolean) are linked via rdf:type.
        for dt in self.datatypes.values():
            for rt in dt.rdf_types:
                if rt in self.datatypes and rt != dt.uri:
                    subs_raw.setdefault(rt, set()).add(dt.uri)

        for term in all_terms.values():
            for target in term.supersededBy:
                supersedes_raw.setdefault(target, set()).add(term.uri)

        enum_set: Set[URIRef] = set()
        if SDO.Enumeration in self.types:
            stack = [SDO.Enumeration]
            while stack:
                cur = stack.pop()
                if cur not in enum_set and cur in self.types:
                    enum_set.add(cur)
                    stack.extend(subs_raw.get(cur, ()))

        enum_members_raw: Dict[URIRef, Set[URIRef]] = {}
        for ev in self.enum_values.values():
            for rt in ev.rdf_types:
                if rt in enum_set:
                    enum_members_raw.setdefault(rt, set()).add(ev.uri)

        self.enumerations = frozenset(enum_set)
        self.declared_properties = {
            u: tuple(sorted(ps, key=str)) for u, ps in declared_raw.items()
        }
        self.expected_type_for = {
            u: tuple(sorted(ps, key=str)) for u, ps in expected_raw.items()
        }
        self.subs = {
            u: tuple(sorted(cs, key=str)) for u, cs in subs_raw.items()
        }
        self.enumeration_members = {
            u: tuple(sorted(ms, key=str)) for u, ms in enum_members_raw.items()
        }
        self.supersedes = {
            u: tuple(sorted(ss, key=str)) for u, ss in supersedes_raw.items()
        }

        memo: Dict[URIRef, Tuple[URIRef, ...]] = {}

        def _ancestors(u: URIRef, visiting: FrozenSet[URIRef]) -> Tuple[URIRef, ...]:
            if u in memo:
                return memo[u]
            if u in visiting:
                return ()
            term = all_terms.get(u)
            if term is None:
                return ()
            supers = sorted(getattr(term, "supers", ()), key=str)
            raw: List[URIRef] = []
            next_visiting = visiting | {u}
            for sup in supers:
                if sup not in all_terms:
                    continue
                raw.append(sup)
                raw.extend(_ancestors(sup, next_visiting))
            dedup_rev: List[URIRef] = []
            for item in reversed(raw):
                if item not in dedup_rev:
                    dedup_rev.append(item)
            res = tuple(reversed(dedup_rev))
            memo[u] = res
            return res

        self.ancestors = {u: _ancestors(u, frozenset()) for u in all_terms}

        all_properties: Dict[URIRef, Tuple[URIRef, ...]] = {}
        for u in (*self.types, *self.datatypes, *self.enum_values):
            if u in all_properties:
                continue
            props: Set[URIRef] = set(self.declared_properties.get(u, ()))
            for anc in self.ancestors.get(u, ()):
                props.update(self.declared_properties.get(anc, ()))
            all_properties[u] = tuple(sorted(props, key=str))
        self.all_properties = all_properties

    def term(self, uri: Union[URIRef, str]) -> Optional[SchemaTerm]:
        u = SdoUri(uri).uri
        return (
            self.types.get(u)
            or self.properties.get(u)
            or self.enum_values.get(u)
            or self.datatypes.get(u)
        )

    def all_terms(self) -> Dict[URIRef, SchemaTerm]:
        return {
            **self.types,
            **self.datatypes,
            **self.properties,
            **self.enum_values,
        }

    def layer(self, uri: Union[URIRef, str]) -> str:
        t = self.term(uri)
        if not t or not t.isPartOf:
            return "core"
        return SdoUri(t.isPartOf[0]).layer()

    def ga_terms(self) -> FrozenSet[URIRef]:
        return frozenset(
            u
            for u in self.all_terms()
            if self.layer(u) not in {"pending", "attic"}
        )

    def __hash__(self) -> int:
        return hash((
            self.version,
            tuple(sorted(self.types.keys(), key=str)),
            tuple(sorted(self.properties.keys(), key=str)),
            tuple(sorted(self.enum_values.keys(), key=str)),
            tuple(sorted(self.datatypes.keys(), key=str)),
        ))
