"""Thin Jinja2 view adapter over SchemaTerm and Vocabulary."""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass
import enum
import functools
from pathlib import Path
from typing import Any

import rdflib
from rdflib import URIRef

from schemaorg import markdown
from schemaorg.collaborators import Collaborator, CollaboratorRegistry
from schemaorg.model import (
    EnumerationValue,
    SchemaProperty,
    SchemaTerm,
    Vocabulary,
)
from schemaorg.sdo_uri import SdoUri


class TermKind(enum.StrEnum):
    """Display classification used by Jinja2 term and docs templates."""

    TYPE = "Type"
    PROPERTY = "Property"
    DATATYPE = "Datatype"
    ENUMERATION = "Enumeration"
    ENUMERATIONVALUE = "Enumerationvalue"
    REFERENCE = "Reference"


class TermSeq(tuple[Any, ...]):
    """Tuple exposing .terms and .ids for legacy Jinja2 template loops."""

    def __new__(cls, items: Iterable[Any] = ()) -> TermSeq:
        return super().__new__(cls, items)

    @property
    def terms(self) -> TermSeq:
        return self

    @property
    def ids(self) -> tuple[str, ...]:
        return tuple(x.id if hasattr(x, "id") else str(x) for x in self)


@dataclass(frozen=True)
class ReferenceView:
    """External non-schema.org URI referenced as a supertype or equivalent."""

    id: str
    uri: str
    label: str
    termType: TermKind = TermKind.REFERENCE
    pending: bool = False
    retired: bool = False
    superseded: bool = False
    extLayer: str = ""


class TermView:
    """Read-only template view joining a flat SchemaTerm with its Vocabulary."""

    def __init__(self, term: SchemaTerm, catalog: TermViewCatalog) -> None:
        self._term = term
        self._catalog = catalog

    @property
    def id(self) -> str:
        return self._term.id

    @property
    def uri(self) -> str:
        return str(self._term.uri)

    @property
    def label(self) -> str:
        return self._term.label or self._term.id

    @functools.cached_property
    def termType(self) -> TermKind:
        return self._catalog.kind_of(self._term)

    @functools.cached_property
    def comment(self) -> str:
        if not self._term.comment:
            return ""
        return markdown.Markdown.parse(self._term.comment, wpre="/").strip()

    @functools.cached_property
    def _layer(self) -> str:
        if not self._term.isPartOf:
            return "core"
        return SdoUri(self._term.isPartOf[0]).layer()

    @property
    def pending(self) -> bool:
        return self._layer == "pending"

    @property
    def retired(self) -> bool:
        return self._layer == "attic"

    @property
    def extLayer(self) -> str:
        return "" if self._layer == "core" else self._layer

    @property
    def supersededBy(self) -> str:
        if not self._term.supersededBy:
            return ""
        return SdoUri(self._term.supersededBy[0]).term_name()

    @property
    def superseded(self) -> bool:
        return bool(self._term.supersededBy)

    @functools.cached_property
    def supersedes(self) -> tuple[str, ...]:
        uris = self._catalog.vocab.supersedes.get(self._term.uri, ())
        return tuple(SdoUri(u).term_name() for u in uris)

    @functools.cached_property
    def sources(self) -> tuple[str, ...]:
        return tuple(str(u) for u in self._term.source)

    @functools.cached_property
    def acknowledgements(self) -> tuple[Collaborator, ...]:
        if self._catalog.collaborators is None:
            return ()
        return self._catalog.collaborators.for_term(self._term)

    @functools.cached_property
    def supers(self) -> TermSeq:
        raw = sorted(
            getattr(self._term, "supers", ()),
            key=lambda u: SdoUri(u).term_name(),
        )
        return self._catalog.views_or_refs(raw)

    @functools.cached_property
    def subs(self) -> TermSeq:
        return self._catalog.views(
            self._catalog.vocab.subs.get(self._term.uri, ())
        )

    @functools.cached_property
    def equivalents(self) -> TermSeq:
        raw = sorted(
            getattr(self._term, "equivalents", ()),
            key=lambda u: self._catalog.prefixed_id(str(u)),
        )
        return self._catalog.views_or_refs(raw)

    @functools.cached_property
    def properties(self) -> TermSeq:
        return self._catalog.views(
            self._catalog.vocab.declared_properties.get(self._term.uri, ())
        )

    @functools.cached_property
    def allproperties(self) -> TermSeq:
        return self._catalog.views(
            self._catalog.vocab.all_properties.get(self._term.uri, ())
        )

    @functools.cached_property
    def expectedTypeFor(self) -> TermSeq:
        return self._catalog.views(
            self._catalog.vocab.expected_type_for.get(self._term.uri, ())
        )

    @functools.cached_property
    def enumerationMembers(self) -> TermSeq:
        return self._catalog.views(
            self._catalog.vocab.enumeration_members.get(self._term.uri, ())
        )

    @functools.cached_property
    def domainIncludes(self) -> TermSeq:
        if not isinstance(self._term, SchemaProperty):
            return TermSeq()
        return self._catalog.views(self._term.domainIncludes)

    @functools.cached_property
    def rangeIncludes(self) -> TermSeq:
        if not isinstance(self._term, SchemaProperty):
            return TermSeq()
        return self._catalog.views(self._term.rangeIncludes)

    @functools.cached_property
    def inverse(self) -> TermView | None:
        if not isinstance(self._term, SchemaProperty) or not self._term.inverseOf:
            return None
        return self._catalog.get(self._term.inverseOf[0])

    @functools.cached_property
    def enumerationParent(self) -> TermView | None:
        if not isinstance(self._term, EnumerationValue):
            return None
        enums = self._catalog.vocab.enumerations
        for rt in self._term.rdf_types:
            if rt in enums:
                return self._catalog.get(rt)
        return None

    @functools.cached_property
    def termStack(self) -> TermSeq:
        # Pure enumerations omit inherited Thing properties on term pages.
        if self.termType == TermKind.ENUMERATION and not self.properties:
            return TermSeq()
        return self._catalog.views(
            self._catalog.vocab.ancestors.get(self._term.uri, ())
        )

    @functools.cached_property
    def superPaths(self) -> tuple[TermSeq, ...]:
        return self._catalog.parent_paths(self._term)


class TermViewCatalog:
    """Memoized TermView lookup, prefix formatting, and breadcrumb paths."""

    def __init__(
        self,
        vocab: Vocabulary | None = None,
        namespaces: Mapping[str, str] | None = None,
        collaborators: CollaboratorRegistry | None = None,
    ) -> None:
        self.vocab: Vocabulary = vocab if vocab is not None else Vocabulary()
        self.namespaces: tuple[tuple[str, str], ...] = tuple(
            sorted((k, v) for k, v in (namespaces or {}).items() if k)
        )
        self.collaborators = collaborators
        self._views: dict[URIRef, TermView] = {
            u: TermView(t, self) for u, t in self.vocab.all_terms().items()
        }

    @classmethod
    def from_graph(
        cls,
        graph: rdflib.Graph,
        vocab: Vocabulary,
        collaborators: CollaboratorRegistry | None = None,
    ) -> TermViewCatalog:
        ns = {str(p): str(u) for p, u in graph.namespaces() if str(p)}
        return cls(vocab=vocab, namespaces=ns, collaborators=collaborators)

    def kind_of(self, term: SchemaTerm) -> TermKind:
        if isinstance(term, SchemaProperty):
            return TermKind.PROPERTY
        if isinstance(term, EnumerationValue):
            return TermKind.ENUMERATIONVALUE
        if term.uri in self.vocab.enumerations:
            return TermKind.ENUMERATION
        if term.uri in self.vocab.datatypes:
            return TermKind.DATATYPE
        return TermKind.TYPE

    def get(self, uri_or_id: URIRef | str) -> TermView | None:
        if not uri_or_id:
            return None
        return self._views.get(SdoUri(uri_or_id).uri)

    def all_views(self, layer: str | None = None) -> list[TermView]:
        views = sorted(self._views.values(), key=lambda v: str(v._term.uri))
        if not layer:
            return views
        return [v for v in views if self.vocab.layer(v._term.uri) == layer]

    def views(self, uris: Iterable[URIRef]) -> TermSeq:
        return TermSeq(
            v for u in uris if (v := self._views.get(u)) is not None
        )

    def views_or_refs(self, uris: Iterable[URIRef]) -> TermSeq:
        items: list[TermView | ReferenceView] = []
        for u in uris:
            if (view := self._views.get(u)) is not None:
                items.append(view)
            else:
                s = str(u)
                items.append(ReferenceView(id=s, uri=s, label=self.prefixed_id(s)))
        return TermSeq(items)

    def prefixed_id(self, uri: str) -> str:
        for prefix, ns_uri in self.namespaces:
            if uri.startswith(ns_uri):
                base = Path(uri).name
                if "#" in base:
                    base = base.split("#", 1)[1]
                return f"{prefix}:{base}"
        return uri

    def parent_paths(self, term: SchemaTerm) -> tuple[TermSeq, ...]:
        pstacks: list[list[str]] = [[]]

        def walk(cur: SchemaTerm, cstack: list[str]) -> None:
            cstack.insert(0, cur.id)
            sup_ids = sorted(
                SdoUri(u).term_name() for u in getattr(cur, "supers", ())
            )
            if isinstance(cur, EnumerationValue):
                for rt in cur.rdf_types:
                    if rt in self.vocab.enumerations:
                        ep_id = SdoUri(rt).term_name()
                        if ep_id not in sup_ids:
                            sup_ids.append(ep_id)
                        break
            sup_ids = [sid for sid in sup_ids if SdoUri(sid).is_sdo()]
            tmp = [cstack]
            if sup_ids:
                for _ in range(1, len(sup_ids)):
                    branch = cstack[:]
                    tmp.append(branch)
                    pstacks.append(branch)
                for idx, pid in enumerate(sup_ids):
                    parent = self.vocab.term(pid)
                    if parent is not None:
                        walk(parent, tmp[idx])

        walk(term, pstacks[0])

        tt = self.kind_of(term)
        inserts: list[str] = []
        if tt == TermKind.PROPERTY:
            inserts = ["Property", "Thing"]
        elif tt == TermKind.DATATYPE and term.id != "DataType":
            inserts = ["DataType"]
        elif tt == TermKind.TYPE:
            base = self.vocab.term(pstacks[0][0])
            if base is not None and self.kind_of(base) == TermKind.DATATYPE:
                inserts = ["DataType"]

        for ins in inserts:
            for s in pstacks:
                s.insert(0, ins)

        return tuple(TermSeq(s) for s in pstacks)

    def parent_paths_to(
        self, start_term_id: str, end_term_id: str = "Thing"
    ) -> list[list[str]]:
        view = self.get(start_term_id)
        if view is None:
            return []
        return [list(p) for p in view.superPaths if end_term_id in p]

    def is_subclass_of(self, child_id: str, parent_id: str) -> bool:
        child = self.vocab.term(child_id)
        parent = self.vocab.term(parent_id)
        if child is None or parent is None:
            return False
        if child.uri == parent.uri:
            return True
        return parent.uri in self.vocab.ancestors.get(child.uri, ())
