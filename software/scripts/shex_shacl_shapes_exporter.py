#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Generate the `shexj` and `shacl` files."""

import argparse
import json
import logging
import os
import sys
from pathlib import Path

if os.getcwd() not in sys.path:
    sys.path.insert(1, os.getcwd())

from rdflib import RDF, RDFS, BNode, Graph, Namespace, URIRef
from rdflib.compare import to_canonical_graph
from rdflib.collection import Collection
from rdflib.term import Node

from software.util.sort_dict import sort_dict

BASE = Namespace("http://schema.org/validation#")
SCHEMA = Namespace("http://schema.org/")
SHACL = Namespace("http://www.w3.org/ns/shacl#")

PREFIX = "ValidSchema"
FILE_ENCODING = "utf-8"

log = logging.getLogger(__name__)


def replace_prefix(data):
    """
    Replaces schema.org prefix with schema.org validation prefix
    """
    return BASE[PREFIX + str(data).replace("http://schema.org/", "")]


class ShExJParser:
    _ancestor_cache = {}
    _domain_includes = {}
    _range_includes = {}
    _subclass_of = {}

    @classmethod
    def clear_caches(cls):
        cls._ancestor_cache = {}
        cls._domain_includes = {}
        cls._range_includes = {}
        cls._subclass_of = {}

    @classmethod
    def index_graph(cls, source):
        cls.clear_caches()
        for s, o in source.subject_objects(SCHEMA.domainIncludes):
            cls._domain_includes.setdefault(o, []).append(s)
        for s, o in source.subject_objects(SCHEMA.rangeIncludes):
            cls._range_includes.setdefault(s, []).append(o)
        for s, o in source.subject_objects(RDFS.subClassOf):
            cls._subclass_of.setdefault(s, []).append(o)

        # Pre-sort indexed lists for predictability
        for k in cls._domain_includes:
            cls._domain_includes[k].sort(key=str)
        for k in cls._range_includes:
            cls._range_includes[k].sort(key=str)
        for k in cls._subclass_of:
            cls._subclass_of[k].sort(key=str)

    @classmethod
    def parse_shape(cls, source, shape, is_datatype):
        """
        Creates shape ShExJ shape for schema.org entity

        :param source: source rdflib graph
        :param shape: entity IRI
        :param is_datatype: whether the shape is a datatype
        :return: JSON(dict) with ShEx constraints
        """

        shape_id = replace_prefix(shape)
        node = None
        if is_datatype:
            node = {
                "type": "NodeConstraint",
                "nodeKind": "literal",  # There are no more constraints on datatypes.
            }
        else:
            node = {"type": "Shape"}
            properties = cls._domain_includes.get(shape, [])

            # find all subclasses
            ancestors = sorted(list(set(cls.find_parent_classes(source, shape))), key=str)
            if properties:
                expression = {
                    "type": "EachOf",
                    "expressions": [cls.type_constraint(sorted(ancestors + [shape], key=str))],
                }
                for prop in sorted(properties, key=str):
                    expression["expressions"].append(
                        cls.parse_property(source, prop)
                    )
                node["expression"] = expression
            else:
                node["expression"] = cls.type_constraint(sorted(ancestors + [shape], key=str))
            node["extra"] = [RDF.type]

            parents = sorted([
                replace_prefix(URIRef(x)) for x in cls._subclass_of.get(shape, [])
            ], key=str)
            if parents:
                node["extends"] = parents

        return {"type": "ShapeDecl", "id": shape_id, "shapeExpr": node}

    @staticmethod
    def type_constraint(types):
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

    @classmethod
    def parse_property(cls, source, prop):
        """
        Creates property constraints

        :param source: source rdflib graph
        :param prop: property IRI
        :return: JSON(dict) with ShExJ representation of property constraints
        """
        node = {"type": "TripleConstraint", "predicate": prop, "min": 0, "max": -1}
        prop_range = sorted([
            replace_prefix(URIRef(x)) for x in cls._range_includes.get(prop, [])
        ], key=str)
        if len(prop_range) == 1:
            node["valueExpr"] = prop_range[0]
        elif prop_range:
            node["valueExpr"] = {"type": "ShapeOr", "shapeExprs": prop_range}
        return node

    @classmethod
    def find_parent_classes(cls, source, shape):
        """
        Finds all ancestors of the shape in the subclasses tree using transitive closure.

        :param source: source rdflib graph
        :param shape: child shape IRI
        :return: list of all ancestor IRIs
        """
        if shape in cls._ancestor_cache:
            return cls._ancestor_cache[shape]

        # transitive_objects(shape, RDFS.subClassOf) returns an iterator including shape
        # itself, but we want ancestors, so we remove it from the result.
        ancestors = list(source.transitive_objects(shape, RDFS.subClassOf))
        if shape in ancestors:
            ancestors.remove(shape)
        res = [URIRef(c) for c in ancestors if isinstance(c, URIRef)]
        cls._ancestor_cache[shape] = res
        return res

    @classmethod
    def to_shex(cls, source):
        """
        Creates ShExJ constraints for schema.org terms definition

        :param source: source rdflib graph
        :return: string representation of ShExJ constraints
        """
        cls.index_graph(source)
        shapes = sorted(source.subjects(RDF.type, RDFS.Class), key=str)

        all_datatypes = {URIRef(SCHEMA.DataType)}
        # Use transitive_subjects to find all subclasses of DataType
        for dt_sub in source.transitive_subjects(RDFS.subClassOf, SCHEMA.DataType):
            if isinstance(dt_sub, URIRef):
                all_datatypes.add(dt_sub)

        shex = {
            "type": "Schema",
            "shapes": [
                cls.parse_shape(
                    source, URIRef(shape), is_datatype=shape in all_datatypes
                )
                for shape in shapes
                if isinstance(shape, URIRef)
            ],
        }

        return json.dumps(sort_dict(shex))


class ShaclParser:
    @staticmethod
    def parse_shape(source, shape, dest):
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
        properties = sorted(ShExJParser._domain_includes.get(shape, []), key=str)
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
    def parse_property(source, prop, dest):
        """
        Creates property constraints

        :param source: source rdflib graph
        :param prop: property IRI
        :param dest: output SHACL constraints graph
        :return: property blank node
        """
        node = BNode()
        dest.add((node, SHACL.path, prop))
        property_range = sorted([
            replace_prefix(URIRef(x)) for x in ShExJParser._range_includes.get(prop, [])
        ], key=str)
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
    def get_subclasses(source):
        """
        Creates subclasses tree

        :param source: source rdflib graph
        :return: subclasses tree rdflib graph
        """
        subclasses = Graph()
        subclasses.bind("sh", SHACL)
        subclasses.bind("schema", SCHEMA)
        subclasses.bind("rdfs", RDFS)
        # Use str() for sorting to be deterministic and fast enough
        for s, p, o in sorted(source.triples((None, RDFS.subClassOf, None)), key=lambda t: (str(t[0]), str(t[1]), str(t[2]))):
            subclasses.add((s, p, o))

        log.info(f"Canonicalizing subclasses graph ({len(subclasses)})")
        nsMgr = subclasses.namespace_manager
        subclasses = to_canonical_graph(subclasses)
        subclasses.namespace_manager = nsMgr

        return subclasses.serialize(format="turtle", sort_keys=True)

    @staticmethod
    def to_shacl(source):
        """
        Creates SHACL constraints from schema.org terms definitions

        :param source: source rdflib graph
        :return: string representation of SHACL constraints
        """
        dest = Graph()
        dest.bind("sh", SHACL)
        dest.bind("schema", SCHEMA)
        dest.bind("", BASE)
        shapes = sorted(source.subjects(RDF.type, RDFS.Class), key=str)
        for shape in shapes:
            if isinstance(shape, URIRef):
                ShaclParser.parse_shape(source, shape, dest)

        # Use to_canonical_graph to ensure deterministic blank node naming and sorting
        # This takes about 25 minutes to compute, so we leave it out for the moment.
        # log.info(f"Canonicalizing ShAcl shapes graph ({len(dest)})")
        # nsMgr = dest.namespace_manager
        # dest = to_canonical_graph(dest)
        # dest.namespace_manager = nsMgr

        return dest.serialize(format="turtle", sort_keys=True)


def generate_files(
    term_defs_path,
    outputdir,
    outputfileprefix="",
    input_format="nt",
):
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
