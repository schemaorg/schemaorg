"""Single-pass JSON-LD slicer for per-term HTML <script> payloads."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import rdflib

from schemaorg import constants
from schemaorg.sdo_uri import SdoUri
from schemaorg.term_view import TermKind, TermView
from util.sort_dict import sort_dict


def _add_prefix(token: str, out: set[str]) -> None:
    if ":" in token and not token.startswith(("http://", "https://")):
        out.add(token.split(":", 1)[0])


def _used_prefixes(obj: Any, out: set[str]) -> None:
    if isinstance(obj, dict):
        for k, v in obj.items():
            _add_prefix(k, out)
            if k in ("@id", "@type"):
                if isinstance(v, str):
                    _add_prefix(v, out)
                elif isinstance(v, list):
                    for item in v:
                        if isinstance(item, str):
                            _add_prefix(item, out)
            elif isinstance(v, (dict, list)):
                _used_prefixes(v, out)
    elif isinstance(obj, list):
        for item in obj:
            _used_prefixes(item, out)


class TermJsonLdIndex:
    """Indexes one full-graph JSON-LD document by term ID for O(1) slicing."""

    def __init__(
        self,
        context: dict[str, Any],
        nodes_by_id: dict[str, dict[str, Any]],
    ) -> None:
        self._context = context
        self._nodes_by_id = nodes_by_id

    @classmethod
    def from_jsonld_text(cls, raw_jsonld: str) -> TermJsonLdIndex:
        parsed = json.loads(raw_jsonld)
        raw_ctx = parsed.get("@context", {})
        context = dict(raw_ctx) if isinstance(raw_ctx, dict) else {}
        nodes = (
            parsed["@graph"]
            if "@graph" in parsed
            else [
                {k: v for k, v in parsed.items() if k != "@context"}
            ]
        )
        nodes_by_id: dict[str, dict[str, Any]] = {}
        for node in nodes:
            node_id = node.get("@id", "")
            if not isinstance(node_id, str) or not node_id:
                continue
            if node_id.startswith("schema:"):
                tid = node_id.removeprefix("schema:")
            elif SdoUri(node_id).is_sdo():
                tid = SdoUri(node_id).term_name()
            else:
                continue
            nodes_by_id[tid] = node
        return cls(context, nodes_by_id)

    @classmethod
    def from_graph(
        cls, graph: rdflib.Graph, jsonld_file: Path | None = None
    ) -> TermJsonLdIndex:
        if jsonld_file is not None and jsonld_file.is_file():
            return cls.from_jsonld_text(jsonld_file.read_text(encoding="utf-8"))
        copy = rdflib.Graph(bind_namespaces="none")
        for prefix, ns_uri in graph.namespaces():
            if str(prefix):
                copy.bind(str(prefix), ns_uri, override=True)
        copy.bind("schema", constants.SCHEMA_URI, override=True)
        for triple in graph:
            copy.add(triple)
        raw = copy.serialize(
            format="json-ld", auto_compact=True, sort_keys=True, max_depth=1
        )
        return cls.from_jsonld_text(str(raw))

    def render_for(self, view: TermView) -> str:
        if view.termType == TermKind.PROPERTY:
            ids = {view.id, *view.termStack.ids}
        elif view.termType == TermKind.ENUMERATIONVALUE:
            ids = {view.id, *view.termStack.ids}
            if view.enumerationParent is not None:
                ids.add(view.enumerationParent.id)
        elif view.termType in {
            TermKind.TYPE,
            TermKind.DATATYPE,
            TermKind.ENUMERATION,
        }:
            ids = {view.id, *view.termStack.ids, *view.allproperties.ids}
        else:
            return ""

        selected = sorted(
            (self._nodes_by_id[tid] for tid in ids if tid in self._nodes_by_id),
            key=lambda n: n["@id"],
        )
        if not selected:
            return ""

        used: set[str] = set()
        _used_prefixes(selected, used)
        ctx = {k: v for k, v in self._context.items() if k in used}

        doc: dict[str, Any] = (
            {"@context": ctx, **selected[0]}
            if len(selected) == 1
            else {"@context": ctx, "@graph": selected}
        )
        return json.dumps(sort_dict(doc), indent=2)
