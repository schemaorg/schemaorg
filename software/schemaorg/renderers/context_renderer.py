"""JSON-LD @context renderer."""

from __future__ import annotations

import json
import logging
from typing import Any

import rdflib

from schemaorg import constants
from schemaorg.model import Vocabulary
from schemaorg.sdo_uri import SCHEMA_URL
import util.pretty_logger as pretty_logger
from util.sort_dict import sort_dict

log: logging.Logger = logging.getLogger(__name__)

# Published JSON-LD context keeps the legacy http scheme.
SDO_HTTP: rdflib.Namespace = rdflib.Namespace(
    SCHEMA_URL._replace(scheme="http").geturl()
)


def render_jsonld_context(graph: rdflib.Graph, vocab: Vocabulary) -> str:
    """Published JSON-LD @context mapping graph prefixes and vocabulary terms."""
    schema_http_uri = str(SDO_HTTP)
    with pretty_logger.BlockLog(message="Creating JSON-LD context", logger=log):
        json_context: dict[str, Any] = {
            "type": "@type",
            "id": "@id",
            "HTML": {"@id": "rdf:HTML"},
            "@vocab": schema_http_uri,
        }

        for pref, path in sorted(
            graph.namespaces(),
            key=lambda kv: (str(kv[0]) == "", str(kv[0])),
        ):
            ns = str(path)
            pref_str = str(pref) or (
                "schema" if ns == constants.SCHEMA_URI else ""
            )
            if pref_str:
                json_context.setdefault(
                    pref_str, schema_http_uri if pref_str == "schema" else ns
                )

        for term in vocab.all_terms().values():
            json_context[term.id] = {"@id": f"schema:{term.id}"}

        return json.dumps(sort_dict({"@context": json_context}), indent=2)
