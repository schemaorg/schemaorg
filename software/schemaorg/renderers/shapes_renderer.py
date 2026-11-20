"""ShEx and SHACL shape renderer."""

from __future__ import annotations

from collections import defaultdict
import functools
import json
import logging
from typing import Any

from rdflib import BNode, Graph, Namespace, RDF, RDFS, URIRef
from rdflib.collection import Collection
from rdflib.compare import to_canonical_graph
from rdflib.term import Node

from schemaorg import constants
from schemaorg.renderers.postprocess import protocol_swap
from schemaorg.sdo_uri import SCHEMA_URL
from util.sort_dict import sort_dict

# Shapes target the http://schema.org/ namespace to match @vocab in JSON-LD context.
SCHEMA: Namespace = Namespace(SCHEMA_URL._replace(scheme="http").geturl())
BASE: Namespace = Namespace(f"{SCHEMA}validation#")
SHACL: Namespace = Namespace("http://www.w3.org/ns/shacl#")
PREFIX: str = "ValidSchema"

log: logging.Logger = logging.getLogger(__name__)


def _shape_uri(term_uri: URIRef) -> URIRef:
    return BASE[f"{PREFIX}{str(term_uri).removeprefix(str(SCHEMA))}"]


def _bnode(
    prefix: str,
    shape: URIRef | None,
    prop: URIRef,
    range_shape: URIRef | None = None,
) -> BNode:
    def sid(term: Node | None) -> str:
        return (
            str(term).rsplit("#", 1)[-1].rsplit("/", 1)[-1]
            if term
            else "shape"
        )

    return BNode("_".join([prefix, sid(shape), sid(prop), sid(range_shape)]))


class ShapesRenderer:
    """ShEx and SHACL shapes of one graph, indexed once per instance."""

    def __init__(self, graph: Graph) -> None:
        self.graph = graph
        self._ancestor_cache: dict[URIRef, list[URIRef]] = {}

    @functools.cached_property
    def http_graph(self) -> Graph:
        swap = protocol_swap()

        def http(node: Node) -> Node:
            return URIRef(swap(str(node))) if isinstance(node, URIRef) else node

        out = Graph(bind_namespaces="none")
        out.bind("schema", swap(constants.SCHEMA_URI))
        for s, p, o in self.graph:
            out.add((http(s), http(p), http(o)))
        return out

    @functools.cached_property
    def _index(
        self,
    ) -> tuple[
        list[URIRef],
        set[URIRef],
        dict[URIRef, list[URIRef]],
        dict[URIRef, list[URIRef]],
        dict[URIRef, list[URIRef]],
    ]:
        source = self.http_graph
        domain_includes: dict[URIRef, list[URIRef]] = defaultdict(list)
        range_includes: dict[URIRef, list[URIRef]] = defaultdict(list)
        subclass_of: dict[URIRef, list[URIRef]] = defaultdict(list)

        for s, o in source.subject_objects(SCHEMA.domainIncludes):
            if isinstance(s, URIRef) and isinstance(o, URIRef):
                domain_includes[o].append(s)
        for s, o in source.subject_objects(SCHEMA.rangeIncludes):
            if isinstance(s, URIRef) and isinstance(o, URIRef):
                range_includes[s].append(o)
        for s, o in source.subject_objects(RDFS.subClassOf):
            if isinstance(s, URIRef) and isinstance(o, URIRef):
                subclass_of[s].append(o)

        for mapping in (domain_includes, range_includes, subclass_of):
            for values in mapping.values():
                values.sort(key=str)

        shapes = sorted(
            (
                s
                for s in source.subjects(RDF.type, RDFS.Class)
                if isinstance(s, URIRef)
            ),
            key=str,
        )

        # Literal-bearing shapes: schema:DataType, its subclasses, its instances,
        # and subclasses of its instances.
        datatypes: set[URIRef] = {URIRef(SCHEMA.DataType)}
        for dt_sub in source.transitive_subjects(RDFS.subClassOf, SCHEMA.DataType):
            if isinstance(dt_sub, URIRef):
                datatypes.add(dt_sub)
        for dt_inst in source.subjects(RDF.type, SCHEMA.DataType):
            if isinstance(dt_inst, URIRef):
                datatypes.add(dt_inst)
                datatypes.update(
                    dt_sub
                    for dt_sub in source.transitive_subjects(RDFS.subClassOf, dt_inst)
                    if isinstance(dt_sub, URIRef)
                )

        return shapes, datatypes, domain_includes, range_includes, subclass_of

    def _ancestors(self, shape: URIRef) -> list[URIRef]:
        if shape not in self._ancestor_cache:
            _, _, _, _, subclass_of = self._index
            seen: set[URIRef] = set()
            stack = list(subclass_of.get(shape, ()))
            while stack:
                cur = stack.pop()
                if cur != shape and cur not in seen:
                    seen.add(cur)
                    stack.extend(subclass_of.get(cur, ()))
            self._ancestor_cache[shape] = sorted(seen, key=str)
        return self._ancestor_cache[shape]

    def shex(self) -> str:
        shapes, datatypes, domain_includes, range_includes, subclass_of = self._index

        def shex_prop(prop: URIRef) -> dict[str, Any]:
            node: dict[str, Any] = {
                "type": "TripleConstraint",
                "predicate": prop,
                "min": 0,
                "max": -1,
            }
            prop_range = sorted(
                (_shape_uri(x) for x in range_includes.get(prop, ())),
                key=str,
            )
            if len(prop_range) == 1:
                node["valueExpr"] = prop_range[0]
            elif prop_range:
                node["valueExpr"] = {"type": "ShapeOr", "shapeExprs": prop_range}
            return node

        def shex_shape(shape: URIRef) -> dict[str, Any]:
            if shape in datatypes:
                expr: dict[str, Any] = {
                    "type": "NodeConstraint",
                    "nodeKind": "literal",
                }
            else:
                props = domain_includes.get(shape, ())
                allowed_types = sorted([*self._ancestors(shape), shape], key=str)
                type_expr: dict[str, Any] = {
                    "type": "TripleConstraint",
                    "predicate": RDF.type,
                    "valueExpr": {"type": "NodeConstraint", "values": allowed_types},
                }
                expr = {
                    "type": "Shape",
                    "expression": (
                        {
                            "type": "EachOf",
                            "expressions": [
                                type_expr,
                                *(shex_prop(p) for p in props),
                            ],
                        }
                        if props
                        else type_expr
                    ),
                    "extra": [RDF.type],
                }
                if parents := sorted(
                    (_shape_uri(x) for x in subclass_of.get(shape, ())),
                    key=str,
                ):
                    expr["extends"] = parents

            return {"type": "ShapeDecl", "id": _shape_uri(shape), "shapeExpr": expr}

        return json.dumps(
            sort_dict({"type": "Schema", "shapes": [shex_shape(s) for s in shapes]})
        )

    def shacl(self) -> str:
        shapes, datatypes, domain_includes, range_includes, _ = self._index
        valid_text = _shape_uri(URIRef(SCHEMA.Text))

        dest = Graph(bind_namespaces="none")
        dest.bind("sh", SHACL)
        dest.bind("schema", SCHEMA)
        dest.bind("", BASE)

        for shape in shapes:
            node = _shape_uri(shape)
            dest.add((node, RDF.type, SHACL.NodeShape))
            dest.add((node, SHACL.targetClass, shape))
            if shape in datatypes:
                dest.add((node, SHACL.nodeKind, SHACL.IRIOrLiteral))
                continue

            dest.add((node, SHACL.nodeKind, SHACL.BlankNodeOrIRI))
            for prop in domain_includes.get(shape, ()):
                prop_node = _bnode("prop", shape, prop)
                dest.add((node, SHACL.property, prop_node))
                dest.add((prop_node, SHACL.path, prop))
                # Schema.org allows Text on every property ("Role or Text" pattern).
                prop_range = sorted(
                    {
                        *(_shape_uri(x) for x in range_includes.get(prop, ())),
                        valid_text,
                    },
                    key=str,
                )

                if len(prop_range) > 1:
                    or_node = _bnode("or", shape, prop)
                    or_collection = Collection(dest, or_node)
                    dest.add((prop_node, SHACL["or"], or_node))
                    for range_shape in prop_range:
                        t = _bnode("t", shape, prop, range_shape=range_shape)
                        dest.add((t, SHACL.node, range_shape))
                        or_collection.append(t)
                else:
                    dest.add((prop_node, SHACL.node, prop_range[0]))

        for prefix, ns in self.graph.namespaces():
            if prefix and str(prefix) != "schema":
                dest.bind(prefix, ns)

        return str(dest.serialize(format="turtle", sort_keys=True))

    def subclasses(self) -> str:
        subclasses = Graph(bind_namespaces="none")
        subclasses.bind("schema", SCHEMA)
        subclasses.bind("rdfs", RDFS)
        for s, p, o in sorted(
            self.http_graph.triples((None, RDFS.subClassOf, None)),
            key=lambda t: (str(t[0]), str(t[1]), str(t[2])),
        ):
            subclasses.add((s, p, o))

        log.info("Canonicalizing subclasses graph (%d)", len(subclasses))
        ns_mgr = subclasses.namespace_manager
        subclasses = to_canonical_graph(subclasses)
        subclasses.namespace_manager = ns_mgr
        return str(subclasses.serialize(format="turtle", sort_keys=True))
