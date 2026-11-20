"""HTTP/HTTPS equivalence Turtle renderer."""

from __future__ import annotations

import rdflib
from rdflib.namespace import OWL

from schemaorg.model import SchemaProperty, Vocabulary
from schemaorg.sdo_uri import SCHEMA_URL, SDO

SDO_HTTP: rdflib.Namespace = rdflib.Namespace(
    SCHEMA_URL._replace(scheme="http").geturl()
)


def render_http_equivs(vocab: Vocabulary) -> str:
    """Turtle declaring the http and https versions of every live term equivalent."""
    out_graph = rdflib.Graph(bind_namespaces="none")
    out_graph.bind("schema_p", SDO_HTTP)
    out_graph.bind("schema_s", SDO)
    out_graph.bind("owl", OWL)

    for uri, term in vocab.all_terms().items():
        if vocab.layer(uri) == "attic":
            continue
        equiv = (
            OWL.equivalentProperty
            if isinstance(term, SchemaProperty)
            else OWL.equivalentClass
        )
        p_uri, s_uri = SDO_HTTP[term.id], SDO[term.id]
        out_graph.add((p_uri, equiv, s_uri))
        out_graph.add((s_uri, equiv, p_uri))

    return str(
        out_graph.serialize(format="turtle", auto_compact=True, sort_keys=True)
    )
