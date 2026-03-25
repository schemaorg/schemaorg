#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Generate the `shexj` and `shacl` files."""

import argparse
import json
import logging
from pathlib import Path
from typing import Any, Generator, Optional, Set, Union

from rdflib import RDF, RDFS, BNode, Graph, Namespace, URIRef
from rdflib.collection import Collection
from rdflib.term import Node

BASE = Namespace("http://schema.org/validation#")
SCHEMA = Namespace("http://schema.org/")
SHACL = Namespace("http://www.w3.org/ns/shacl#")

PREFIX = "ValidSchema"
FILE_ENCODING = "utf-8"

log = logging.getLogger(__name__)


def replace_prefix(data: URIRef) -> URIRef:
    """
    Replaces schema.org prefix with schema.org validation prefix
    """
    return BASE[PREFIX + str(data).replace("http://schema.org/", "")]


class ShExJParser:
    @staticmethod
    def parse_shape(source: Graph, shape: URIRef, is_datatype: bool) -> dict[str, Any]:
        """
        Creates shape ShExJ shape for schema.org entity

        :param source: source rdflib graph
        :param shape: entity IRI
        :param is_datatype: whether the shape is a datatype
        :return: JSON(dict) with ShEx constraints
        """

        shape_id = replace_prefix(shape)
        node: Optional[dict[str, Any]] = None
        if is_datatype:
            node = {
                "type": "NodeConstraint",
                "nodeKind": "literal",  # There are no more constraints on datatypes.
            }
        else:
            node = {"type": "Shape"}
            properties = list(source.subjects(SCHEMA.domainIncludes, shape))
            # find all subclasses
            ancestors = list(set(ShExJParser.find_parent_classes(source, shape)))
            if properties:
                expression = {
                    "type": "EachOf",
                    "expressions": [ShExJParser.type_constraint(ancestors + [shape])],
                }
                for prop in properties:
                    expression["expressions"].append(
                        ShExJParser.parse_property(source, prop)
                    )
                node["expression"] = expression
            else:
                node["expression"] = ShExJParser.type_constraint(ancestors + [shape_id])
            node["extra"] = [RDF.type]
            parents = [
                replace_prefix(URIRef(x)) for x in source.objects(shape, RDFS.subClassOf)
            ]
            if parents:
                node["extends"] = parents

        return {"type": "ShapeDecl", "id": shape_id, "shapeExpr": node}

    @staticmethod
    def type_constraint(types: list[URIRef]) -> dict[str, Any]:
        """
        Creates rdf:type constraints

        :param types: list of possible rdf:type values
        :return: JSON(dict) with ShExJ representation of rdf:type constraints
        """
        return {
            "type": "TripleConstraint",
            "predicate": RDF.type,
            "valueExpr": {"type": "NodeConstraint", "values": types},
        }

    @staticmethod
    def parse_property(source: Graph, prop: URIRef) -> dict[str, Any]:
        """
        Creates property constraints

        :param source: source rdflib graph
        :param prop: property IRI
        :return: JSON(dict) with ShExJ representation of property constraints
        """
        node = {"type": "TripleConstraint", "predicate": prop, "min": 0, "max": -1}
        prop_range = [
            replace_prefix(URIRef(x)) for x in source.objects(prop, SCHEMA.rangeIncludes)
        ]
        if len(prop_range) == 1:
            node["valueExpr"] = prop_range[0]
        elif prop_range:
            node["valueExpr"] = {"type": "ShapeOr", "shapeExprs": prop_range}
        return node

    @staticmethod
    def find_parent_classes(source: Graph, shape: URIRef) -> list[URIRef]:
        """
        Finds all ancestors of the shape in the subclasses tree using transitive closure.

        :param source: source rdflib graph
        :param shape: child shape IRI
        :return: list of all ancestor IRIs
        """
        # transitive_objects(shape, RDFS.subClassOf) returns an iterator including shape
        # itself, but we want ancestors, so we remove it from the result.
        ancestors = list(source.transitive_objects(shape, RDFS.subClassOf))
        if shape in ancestors:
            ancestors.remove(shape)
        return [URIRef(c) for c in ancestors if isinstance(c, URIRef)]

    @staticmethod
    def to_shex(source: Graph) -> str:
        """
        Creates ShExJ constraints for schema.org terms definition

        :param source: source rdflib graph
        :return: string representation of ShExJ constraints
        """
        shapes = sorted(source.subjects(RDF.type, RDFS.Class), key=str)

        all_datatypes: set[URIRef] = {URIRef(SCHEMA.DataType)}
        # Use transitive_subjects to find all subclasses of DataType
        for dt_sub in source.transitive_subjects(RDFS.subClassOf, SCHEMA.DataType):
            if isinstance(dt_sub, URIRef):
                all_datatypes.add(dt_sub)

        shex = {
            "type": "Schema",
            "shapes": [
                ShExJParser.parse_shape(
                    source, URIRef(shape), is_datatype=shape in all_datatypes
                )
                for shape in shapes
                if isinstance(shape, URIRef)
            ],
        }

        return json.dumps(shex)


class ShaclParser:
    @staticmethod
    def parse_shape(source: Graph, shape: URIRef, dest: Graph) -> None:
        """
        Creates SHACL shape for schema.org entity

        :param source: source rdflib graph
        :param shape: target shape IRI
        :param dest: output SHACL constraints graph
        """
        node = replace_prefix(shape)
        dest.add((node, RDF.type, SHACL.NodeShape))
        dest.add((node, SHACL.targetClass, shape))
        dest.add((node, SHACL.nodeKind, SHACL.BlankNodeOrIRI))
        properties = list(source.subjects(SCHEMA.domainIncludes, shape))
        for prop in properties:
            if isinstance(prop, URIRef):
                dest.add(
                    (
                        node,
                        SHACL.property,
                        ShaclParser.parse_property(source, prop, dest),
                    )
                )

    @staticmethod
    def parse_property(source: Graph, prop: URIRef, dest: Graph) -> BNode:
        """
        Creates property constraints

        :param source: source rdflib graph
        :param prop: property IRI
        :param dest: output SHACL constraints graph
        :return: property blank node
        """
        node = BNode()
        dest.add((node, SHACL.path, prop))
        property_range = [
            replace_prefix(URIRef(x)) for x in source.objects(prop, SCHEMA.rangeIncludes)
        ]
        if len(property_range) > 1:
            or_node = BNode()
            or_collection = Collection(dest, or_node)
            dest.add((node, SHACL["or"], or_node))
            for shape in property_range:
                t = BNode()
                dest.add((t, SHACL.node, shape))
                or_collection.append(t)
        elif property_range:
            dest.add((node, SHACL.node, property_range[0]))
        return node

    @staticmethod
    def get_subclasses(source: Graph) -> str:
        """
        Creates subclasses tree

        :param source: source rdflib graph
        :return: subclasses tree rdflib graph
        """
        subclasses = Graph()
        subclasses.bind("sh", SHACL)
        subclasses.bind("schema", SCHEMA)
        subclasses.bind("rdfs", RDFS)
        for s, p, o in source.triples((None, RDFS.subClassOf, None)):
            subclasses.add((s, p, o))
        return subclasses.serialize(format="turtle")

    @staticmethod
    def to_shacl(source: Graph) -> str:
        """
        Creates SHACL constraints from schema.org terms definitions

        :param source: source rdflib graph
        :return: string representation of SHACL constraints
        """
        dest = Graph()
        dest.bind("sh", SHACL)
        dest.bind("schema", SCHEMA)
        dest.bind("", BASE)
        shapes = source.subjects(RDF.type, RDFS.Class)
        for shape in shapes:
            if isinstance(shape, URIRef):
                ShaclParser.parse_shape(source, shape, dest)
        return dest.serialize(format="turtle")


def generate_files(
    term_defs_path: Union[str, Path],
    outputdir: Union[str, Path],
    outputfileprefix: str = "",
    input_format: str = "nt",
) -> None:
    term_defs_path = Path(term_defs_path)
    outputdir = Path(outputdir)
    outputdir.mkdir(parents=True, exist_ok=True)

    with term_defs_path.open(encoding=FILE_ENCODING) as f:
        term_defs = f.read()

    graph = Graph().parse(data=term_defs, format=input_format)
    graph.bind("schema", SCHEMA)

    shexj_path = outputdir / f"{outputfileprefix}shapes.shexj"
    shexj_path.write_text(ShExJParser.to_shex(graph), encoding=FILE_ENCODING)
    log.info(f"Created {shexj_path}")

    shacl_path = outputdir / f"{outputfileprefix}shapes.shacl"
    shacl_path.write_text(ShaclParser.to_shacl(graph), encoding=FILE_ENCODING)
    log.info(f"Created {shacl_path}")

    subclasses_path = outputdir / f"{outputfileprefix}subclasses.shacl"
    subclasses_path.write_text(ShaclParser.get_subclasses(graph), encoding=FILE_ENCODING)
    log.info(f"Created {subclasses_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-s", "--sourcefile", help="rdf format source file")
    parser.add_argument(
        "-f", "--format", default="nt", help="source file format (default: .nt)"
    )
    parser.add_argument("-o", "--outputdir", default=".", help="output directory (default: ./)")
    parser.add_argument(
        "-p", "--outputfileprefix", default="", help="output files prefix"
    )
    args = parser.parse_args()

    if args.sourcefile:
        term_defs_path = args.sourcefile
    else:
        term_defs_path = input(".nt terms definitions path: ")

    generate_files(
        term_defs_path=term_defs_path,
        outputdir=args.outputdir,
        outputfileprefix=args.outputfileprefix,
        input_format=args.format,
    )
