"""JSON-LD class-hierarchy tree renderer for website documentation."""

from __future__ import annotations

import json
from typing import Any

from rdflib.term import URIRef

from schemaorg import markdown
from schemaorg.model import Vocabulary
from schemaorg.sdo_uri import SDO, SdoUri
from util.sort_dict import sort_dict
import util.textutils as textutils


def _tree_node(
    vocab: Vocabulary,
    uri: URIRef,
    visitset: set[URIRef],
    term_dict: dict[str, Any] | None = None,
) -> dict[str, Any]:
    termdesc = vocab.term(uri)
    if termdesc is None:
        raise ValueError(f"No description for term {uri}")

    node: dict[str, Any] = term_dict if term_dict is not None else {}
    rendered_comment = (
        markdown.Markdown.parse(termdesc.comment, wpre="/").strip()
        if termdesc.comment
        else ""
    )
    node.update({
        "@type": "rdfs:Class",
        "@id": f"schema:{termdesc.id}",
        "name": termdesc.label or termdesc.id,
        "description": textutils.ShortenOnSentence(
            textutils.StripHtmlTags(rendered_comment)
        ),
    })

    supers = getattr(termdesc, "supers", ())
    if supers:
        sups = [f"schema:{SdoUri(sup).term_name()}" for sup in supers]
        node["rdfs:subClassOf"] = sups[0] if len(sups) == 1 else sups

    layer = vocab.layer(uri)
    if layer in ("pending", "attic"):
        node[layer] = True

    if uri not in visitset:
        visitset.add(uri)
        children = [
            _tree_node(vocab, sub, visitset)
            for sub in vocab.subs.get(uri, ())
            if vocab.term(sub) is not None
        ]
        if children:
            node["children"] = children
    return node


def render_jsonld_tree(vocab: Vocabulary) -> str:
    """JSON-LD class hierarchy rooted at schema:Thing for docs/tree.jsonld."""
    context: dict[str, Any] = {
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        # Legacy output: no trailing slash.
        "schema": str(SdoUri.for_layer()),
        "rdfs:subClassOf": {"@type": "@id"},
        "description": "rdfs:comment",
        "children": {"@reverse": "rdfs:subClassOf"},
    }
    data = _tree_node(
        vocab, SDO.Thing, visitset=set(), term_dict={"@context": context}
    )
    return json.dumps(sort_dict(data), indent=3)
