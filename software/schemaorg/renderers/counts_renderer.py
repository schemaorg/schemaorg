"""Vocabulary term-count renderer (JSON and JSONP)."""

from __future__ import annotations

import functools
import json
from typing import Any

from schemaorg.model import Vocabulary
from schemaorg.sdo_uri import SDO
from schemaorg.version import VersionItem
from util.sort_dict import sort_dict


class CountsRenderer:
    """Term counts per kind, as JSON and as the JSONP snippet used by the docs."""

    def __init__(self, vocab: Vocabulary, version: VersionItem) -> None:
        self.vocab = vocab
        self.version = version

    @functools.cached_property
    def counts(self) -> dict[str, Any]:
        vocab = self.vocab
        dt_roots = (vocab.datatypes.keys() & vocab.types.keys()) - {SDO.DataType}
        dt_classes = {
            u
            for u in vocab.types
            if u in dt_roots or not dt_roots.isdisjoint(vocab.ancestors.get(u, ()))
        }
        properties = len(vocab.properties)
        enums = len(vocab.enumerations)
        enumvals = len(vocab.enum_values)
        datatypes = len(dt_classes) + len(vocab.datatypes.keys() - vocab.types.keys())
        types = len(vocab.types) - 1 - enums - len(dt_classes)

        return {
            "Type": types,
            "Property": properties,
            "Datatype": datatypes,
            "Enumeration": enums,
            "Enumerationvalue": enumvals,
            "All": types + properties + datatypes + enums + enumvals,
            "schemaorgversion": self.version.number(),
        }

    def json(self) -> str:
        return json.dumps(sort_dict(self.counts))

    def jsonp(self) -> str:
        return f"\n    COUNTS = '{self.json()}';\n\n    insertschemacounts ( COUNTS );\n    "
