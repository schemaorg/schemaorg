#!/usr/bin/env python3
"""Generate the `shexj` and `shacl` files."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
import json
import logging
from pathlib import Path
from typing import Any

from rdflib import BNode, Graph, Namespace, RDF, RDFS, URIRef
from rdflib.collection import Collection
from rdflib.compare import to_canonical_graph
from rdflib.term import Node

from schemaorg.layout import Releases
from schemaorg.sdo_uri import SCHEMA_URL, SDO
import util.paths as paths
import util.schema as schema
from util.sort_dict import sort_dict

# Shapes are generated from the http:// dump and keep that namespace.
SCHEMA: Namespace = Namespace(SCHEMA_URL._replace(scheme="http").geturl())
BASE: Namespace = Namespace(f"{SCHEMA}validation#")
SHACL: Namespace = Namespace("http://www.w3.org/ns/shacl#")

PREFIX: str = "ValidSchema"

log: logging.Logger = logging.getLogger(__name__)


def _detect_schema_ns(source: Graph) -> Namespace:
    if (
        (None, SCHEMA.domainIncludes, None) in source
        or (SCHEMA.DataType, None, None) in source
    ):
        return SCHEMA
    if (
        (None, SDO.domainIncludes, None) in source
        or (SDO.DataType, None, None) in source
    ):
        return SDO
    return SCHEMA


def replace_prefix(data: URIRef, schema_ns: Namespace = SCHEMA) -> URIRef:
    """Replace schema.org prefix with schema.org validation prefix."""
    base = BASE if schema_ns == SCHEMA else Namespace(f"{schema_ns}validation#")
    return base[f"{PREFIX}{str(data).removeprefix(str(schema_ns))}"]


def collect_datatypes(source: Graph, schema_ns: Namespace = SCHEMA) -> set[URIRef]:
    """Collect every term that must be serialised as a literal-bearing shape.

    That is schema:DataType itself, everything declared a subclass of it, and
    every instance of it (schema:Text, schema:Date, ...) together with their
    subclasses.

    Both exporters need exactly this set. Keeping a single copy matters: when
    the ShEx and SHACL exporters computed it separately they were free to
    drift, and a shape that is wrongly classed as a non-datatype gets
    `sh:nodeKind sh:BlankNodeOrIRI`, which forbids it from ever being a
    literal and fails every example that uses it.
    """
    datatypes: set[URIRef] = {URIRef(schema_ns.DataType)}

    for dt_sub in source.transitive_subjects(RDFS.subClassOf, schema_ns.DataType):
        if isinstance(dt_sub, URIRef):
            datatypes.add(dt_sub)

    for dt_inst in source.subjects(RDF.type, schema_ns.DataType):
        if isinstance(dt_inst, URIRef):
            datatypes.add(dt_inst)
            for dt_sub in source.transitive_subjects(RDFS.subClassOf, dt_inst):
                if isinstance(dt_sub, URIRef):
                    datatypes.add(dt_sub)

    return datatypes


class ShExJParser:
    _ancestor_cache: dict[URIRef, list[URIRef]] = {}
    _domain_includes: dict[URIRef, list[URIRef]] = {}
    _range_includes: dict[URIRef, list[URIRef]] = {}
    _subclass_of: dict[URIRef, list[URIRef]] = {}
    _schema_ns: Namespace = SCHEMA

    @classmethod
    def clear_caches(cls) -> None:
        cls._ancestor_cache = {}
        cls._domain_includes = {}
        cls._range_includes = {}
        cls._subclass_of = {}
        cls._schema_ns = SCHEMA

    @classmethod
    def index_graph(cls, source: Graph) -> None:
        cls.clear_caches()
        cls._schema_ns = _detect_schema_ns(source)
        for s, o in source.subject_objects(cls._schema_ns.domainIncludes):
            if isinstance(s, URIRef) and isinstance(o, URIRef):
                cls._domain_includes.setdefault(o, []).append(s)
        for s, o in source.subject_objects(cls._schema_ns.rangeIncludes):
            if isinstance(s, URIRef) and isinstance(o, URIRef):
                cls._range_includes.setdefault(s, []).append(o)
        for s, o in source.subject_objects(RDFS.subClassOf):
            if isinstance(s, URIRef) and isinstance(o, URIRef):
                cls._subclass_of.setdefault(s, []).append(o)

        for values in cls._domain_includes.values():
            values.sort(key=str)
        for values in cls._range_includes.values():
            values.sort(key=str)
        for values in cls._subclass_of.values():
            values.sort(key=str)

    @classmethod
    def parse_shape(
        cls, source: Graph, shape: URIRef, is_datatype: bool
    ) -> dict[str, Any]:
        """Create ShExJ shape for a schema.org entity."""
        shape_id = replace_prefix(shape, cls._schema_ns)
        node: dict[str, Any]
        if is_datatype:
            node = {
                "type": "NodeConstraint",
                "nodeKind": "literal",
            }
        else:
            node = {"type": "Shape"}
            properties = cls._domain_includes.get(shape, [])
            ancestors = sorted(
                set(cls.find_parent_classes(source, shape)), key=str
            )
            type_expr = cls.type_constraint(sorted(ancestors + [shape], key=str))
            if properties:
                node["expression"] = {
                    "type": "EachOf",
                    "expressions": [
                        type_expr,
                        *(
                            cls.parse_property(prop)
                            for prop in sorted(properties, key=str)
                        ),
                    ],
                }
            else:
                node["expression"] = type_expr
            node["extra"] = [RDF.type]

            parents = sorted(
                (
                    replace_prefix(URIRef(x), cls._schema_ns)
                    for x in cls._subclass_of.get(shape, [])
                ),
                key=str,
            )
            if parents:
                node["extends"] = parents

        return {"type": "ShapeDecl", "id": shape_id, "shapeExpr": node}

    @staticmethod
    def type_constraint(types: list[URIRef]) -> dict[str, Any]:
        """Create rdf:type constraints."""
        return {
            "type": "TripleConstraint",
            "predicate": RDF.type,
            "valueExpr": {"type": "NodeConstraint", "values": types},
        }

    @classmethod
    def parse_property(cls, prop: URIRef) -> dict[str, Any]:
        """Create property constraints."""
        node: dict[str, Any] = {
            "type": "TripleConstraint",
            "predicate": prop,
            "min": 0,
            "max": -1,
        }
        prop_range = sorted(
            (
                replace_prefix(URIRef(x), cls._schema_ns)
                for x in cls._range_includes.get(prop, [])
            ),
            key=str,
        )
        if len(prop_range) == 1:
            node["valueExpr"] = prop_range[0]
        elif prop_range:
            node["valueExpr"] = {"type": "ShapeOr", "shapeExprs": prop_range}
        return node

    @classmethod
    def find_parent_classes(cls, source: Graph, shape: URIRef) -> list[URIRef]:
        """Find all ancestors of `shape` in the subclass hierarchy."""
        if shape in cls._ancestor_cache:
            return cls._ancestor_cache[shape]

        # transitive_objects includes `shape` itself; drop it to keep strict ancestors.
        ancestors = list(source.transitive_objects(shape, RDFS.subClassOf))
        if shape in ancestors:
            ancestors.remove(shape)
        res = [URIRef(c) for c in ancestors if isinstance(c, URIRef)]
        cls._ancestor_cache[shape] = res
        return res

    @classmethod
    def to_shex(cls, source: Graph) -> str:
        """Create ShExJ constraints for schema.org term definitions."""
        cls.index_graph(source)
        shapes = sorted(source.subjects(RDF.type, RDFS.Class), key=str)
        all_datatypes = collect_datatypes(source, cls._schema_ns)

        shex: dict[str, Any] = {
            "type": "Schema",
            "shapes": [
                cls.parse_shape(
                    source, shape, is_datatype=shape in all_datatypes
                )
                for shape in shapes
                if isinstance(shape, URIRef)
            ],
        }

        return json.dumps(sort_dict(shex))


class ShaclParser:
    @staticmethod
    def parse_shape(
        shape: URIRef,
        dest: Graph,
        is_datatype: bool = False,
        schema_ns: Namespace = SCHEMA,
    ) -> None:
        """Create SHACL shape for a schema.org entity."""
        node = replace_prefix(shape, schema_ns)
        dest.add((node, RDF.type, SHACL.NodeShape))
        dest.add((node, SHACL.targetClass, shape))
        if is_datatype:
            dest.add((node, SHACL.nodeKind, SHACL.IRIOrLiteral))
        else:
            dest.add((node, SHACL.nodeKind, SHACL.BlankNodeOrIRI))
            properties = sorted(
                ShExJParser._domain_includes.get(shape, []), key=str
            )
            for prop in properties:
                if isinstance(prop, URIRef):
                    dest.add(
                        (
                            node,
                            SHACL.property,
                            ShaclParser.parse_property(
                                prop, dest, shape=shape, schema_ns=schema_ns
                            ),
                        )
                    )

    @staticmethod
    def create_bnode(
        prefix: str,
        shape: URIRef | None,
        prop: URIRef,
        range_shape: URIRef | None = None,
    ) -> BNode:
        """Create a deterministic BNode for `(prefix, shape, prop, range_shape)`."""
        def sid(term: Node | None) -> str:
            return (
                str(term).rsplit("#", 1)[-1].rsplit("/", 1)[-1]
                if term
                else "shape"
            )

        return BNode("_".join([prefix, sid(shape), sid(prop), sid(range_shape)]))

    @staticmethod
    def parse_property(
        prop: URIRef,
        dest: Graph,
        shape: URIRef | None = None,
        schema_ns: Namespace = SCHEMA,
    ) -> BNode:
        """Create SHACL property constraints."""
        node = ShaclParser.create_bnode("prop", shape, prop)
        dest.add((node, SHACL.path, prop))
        property_range = sorted(
            (
                replace_prefix(URIRef(x), schema_ns)
                for x in ShExJParser._range_includes.get(prop, [])
            ),
            key=str,
        )

        # Schema.org allows Text for any property ("Role or Text" pattern)
        valid_text = replace_prefix(URIRef(schema_ns.Text), schema_ns)
        if valid_text not in property_range:
            property_range.append(valid_text)
            property_range.sort(key=str)

        if len(property_range) > 1:
            or_node = ShaclParser.create_bnode("or", shape, prop)
            or_collection = Collection(dest, or_node)
            dest.add((node, SHACL["or"], or_node))
            for range_shape in property_range:
                t = ShaclParser.create_bnode(
                    "t", shape, prop, range_shape=range_shape
                )
                dest.add((t, SHACL.node, range_shape))
                or_collection.append(t)
        elif property_range:
            dest.add((node, SHACL.node, property_range[0]))
        return node

    @staticmethod
    def get_subclasses(source: Graph) -> str:
        """Serialize the canonicalized rdfs:subClassOf graph as Turtle."""
        schema_ns = _detect_schema_ns(source)
        subclasses = Graph()
        subclasses.bind("schema", schema_ns)
        subclasses.bind("rdfs", RDFS)
        for s, p, o in sorted(
            source.triples((None, RDFS.subClassOf, None)),
            key=lambda t: (str(t[0]), str(t[1]), str(t[2])),
        ):
            subclasses.add((s, p, o))

        log.info("Canonicalizing subclasses graph (%d)", len(subclasses))
        ns_mgr = subclasses.namespace_manager
        subclasses = to_canonical_graph(subclasses)
        subclasses.namespace_manager = ns_mgr

        return str(subclasses.serialize(format="turtle", sort_keys=True))

    @staticmethod
    def to_shacl(source: Graph) -> str:
        """Create SHACL constraints from schema.org term definitions."""
        # parse_shape() reads ShExJParser._domain_includes to find a class's
        # properties, which is populated by index_graph(). Without this call
        # shapes come out with no sh:property constraints and conform to
        # everything. Do not rely on generate_files() calling to_shex() first.
        ShExJParser.index_graph(source)
        schema_ns = ShExJParser._schema_ns
        base_ns = BASE if schema_ns == SCHEMA else Namespace(f"{schema_ns}validation#")

        dest = Graph()
        dest.bind("sh", SHACL)
        dest.bind("schema", schema_ns)
        dest.bind("", base_ns)

        shapes = sorted(source.subjects(RDF.type, RDFS.Class), key=str)
        all_datatypes = collect_datatypes(source, schema_ns)

        for shape in shapes:
            if isinstance(shape, URIRef):
                ShaclParser.parse_shape(
                    shape,
                    dest,
                    is_datatype=shape in all_datatypes,
                    schema_ns=schema_ns,
                )

        return str(dest.serialize(format="turtle", sort_keys=True))


def generate_files(
    term_defs_path: str | Path,
    version: str,
    input_format: str = "nt",
    releases: Releases | None = None,
) -> None:
    graph = Graph().parse(Path(term_defs_path), format=input_format)
    graph.bind("schema", _detect_schema_ns(graph))

    rel = releases or Releases(paths.DefaultOutputLayout(), schema.VERSION)

    shexj_path = rel.file(
        version, protocol="", scope="shapes", extension=".shexj"
    )
    shexj_path.write_text(ShExJParser.to_shex(graph), encoding="utf-8")
    log.info("Created %s", shexj_path)

    shacl_path = rel.file(
        version, protocol="", scope="shapes", extension=".shacl"
    )
    shacl_path.write_text(ShaclParser.to_shacl(graph), encoding="utf-8")
    log.info("Created %s", shacl_path)

    subclasses_path = rel.file(
        version, protocol="", scope="subclasses", extension=".shacl"
    )
    subclasses_path.write_text(
        ShaclParser.get_subclasses(graph), encoding="utf-8"
    )
    log.info("Created %s", subclasses_path)


def main(argv: Sequence[str] | None = None) -> None:
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "-s",
        "--sourcefile",
        required=True,
        help="RDF format source file",
    )
    parser.add_argument(
        "-f", "--format", default="nt", help="source file format (default: nt)"
    )
    args = parser.parse_args(argv)

    generate_files(
        term_defs_path=args.sourcefile,
        version=schema.VERSION.current().number(),
        input_format=args.format,
    )


if __name__ == "__main__":
    main()
