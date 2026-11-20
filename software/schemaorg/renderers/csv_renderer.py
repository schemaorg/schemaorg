"""CSV table renderer for the types and properties of a Vocabulary."""

from __future__ import annotations

from collections.abc import Sequence
import csv
import functools
import io
import operator
from typing import Any

import rdflib

from schemaorg import constants, markdown
from schemaorg.model import (
    EnumerationValue,
    SchemaProperty,
    SchemaTerm,
    SchemaType,
    Vocabulary,
)
from schemaorg.sdo_uri import SdoUri

Row = dict[str, str]

TYPE_FIELDS: tuple[str, ...] = (
    "id",
    "label",
    "comment",
    "subTypeOf",
    "enumerationtype",
    "equivalentClass",
    "properties",
    "subTypes",
    "supersedes",
    "supersededBy",
    "isPartOf",
)
PROPERTY_FIELDS: tuple[str, ...] = (
    "id",
    "label",
    "comment",
    "subPropertyOf",
    "equivalentProperty",
    "subproperties",
    "domainIncludes",
    "rangeIncludes",
    "inverseOf",
    "supersedes",
    "supersededBy",
    "isPartOf",
)
_ATTIC_URI: str = str(SdoUri.for_layer("attic"))


def uriwrap(thing: Any) -> str:
    """Format one URI/term name or an iterable of them as sorted full URIs."""
    if not thing:
        return ""
    if isinstance(thing, SdoUri):
        return str(thing)
    if isinstance(thing, (str, rdflib.URIRef)):
        return str(SdoUri(thing))
    return ", ".join(sorted(map(uriwrap, thing)))


def _to_csv(rows: Sequence[Row], fields: Sequence[str]) -> str:
    with io.StringIO() as buffer:
        writer = csv.DictWriter(
            buffer,
            fieldnames=fields,
            quoting=csv.QUOTE_ALL,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(rows)
        return buffer.getvalue()


class CsvRenderer:
    """Type and property tables of one vocabulary; rows are computed once.

    Term links inside comments use full schema.org URLs by default so CSV
    exports resolve outside schema.org.
    """

    def __init__(
        self, vocab: Vocabulary, wikilink_prefix: str = constants.SCHEMA_URI
    ) -> None:
        self.vocab = vocab
        self.wikilink_prefix = wikilink_prefix

    def _base_row(self, term: SchemaTerm) -> Row:
        layer = SdoUri(term.isPartOf[0]).layer() if term.isPartOf else "core"
        comment = (
            markdown.Markdown.parse(
                term.comment, wpre=self.wikilink_prefix
            ).strip()
            if term.comment
            else ""
        )
        return {
            "id": str(term.uri),
            "label": term.label or "",
            "comment": comment,
            "supersedes": uriwrap(self.vocab.supersedes.get(term.uri, ())),
            "supersededBy": uriwrap(
                term.supersededBy[0] if term.supersededBy else ""
            ),
            "isPartOf": "" if layer == "core" else str(SdoUri.for_layer(layer)),
        }

    def _property_row(self, term: SchemaProperty) -> Row:
        return {
            **self._base_row(term),
            "subPropertyOf": uriwrap(term.supers),
            "equivalentProperty": uriwrap(term.equivalents),
            "subproperties": uriwrap(self.vocab.subs.get(term.uri, ())),
            "domainIncludes": uriwrap(term.domainIncludes),
            "rangeIncludes": uriwrap(term.rangeIncludes),
            "inverseOf": uriwrap(term.inverseOf[0] if term.inverseOf else ""),
        }

    def _type_row(self, term: SchemaType | EnumerationValue) -> Row:
        vocab = self.vocab
        row = {
            **self._base_row(term),
            "subTypeOf": uriwrap(term.supers),
            "equivalentClass": uriwrap(term.equivalents),
            "subTypes": uriwrap(vocab.subs.get(term.uri, ())),
        }
        if isinstance(term, EnumerationValue):
            enum_parent = min(
                (rt for rt in term.rdf_types if rt in vocab.enumerations),
                key=str,
                default="",
            )
            row["enumerationtype"] = uriwrap(enum_parent)
        else:
            row["properties"] = uriwrap(vocab.all_properties.get(term.uri, ()))
        return row

    @functools.cached_property
    def _rows(self) -> tuple[tuple[Row, ...], tuple[Row, ...]]:
        typedata: list[Row] = []
        propdata: list[Row] = []

        for term in self.vocab.all_terms().values():
            if isinstance(term, SchemaProperty):
                propdata.append(self._property_row(term))
            elif isinstance(term, (SchemaType, EnumerationValue)):
                typedata.append(self._type_row(term))

        by_id = operator.itemgetter("id")
        return (
            tuple(sorted(typedata, key=by_id)),
            tuple(sorted(propdata, key=by_id)),
        )

    @staticmethod
    def _select(rows: Sequence[Row], include_retired: bool) -> Sequence[Row]:
        if include_retired:
            return rows
        return [r for r in rows if r["isPartOf"] != _ATTIC_URI]

    def types(self, include_retired: bool) -> str:
        return _to_csv(self._select(self._rows[0], include_retired), TYPE_FIELDS)

    def properties(self, include_retired: bool) -> str:
        return _to_csv(
            self._select(self._rows[1], include_retired), PROPERTY_FIELDS
        )
