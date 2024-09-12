#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import os
from typing import Generator, Any, Union, Set

from rdflib import Graph
from rdflib import BNode, URIRef
from rdflib import Namespace
from rdflib import RDFS, RDF
from rdflib.collection import Collection
from rdflib.term import Node

BASE = Namespace('http://schema.org/validation#')
SCHEMA = Namespace('http://schema.org/')
SHACL = Namespace('http://www.w3.org/ns/shacl#')

PREFIX = 'ValidSchema'
FILE_ENCODING = 'utf-8'

def replace_prefix(data):
    """
    Replaces schema.org prefix with schema.org validation prefix
    """
    return BASE[PREFIX + data.replace('http://schema.org/', '')]


class ShExJParser:

    @staticmethod
    def parse_shape(source: Graph, shape: URIRef, is_datatype: bool) -> dict:
        """
        Creates shape ShExJ shape for schema.org entity

        :param source: source rdflib graph
        :param shape: entity IRI
        :return: JSON(dict) with ShEx constraints
        """

        id = replace_prefix(shape)
        node: Union[dict[Any], None] = None
        if is_datatype:
            node = {
                'type': 'NodeConstraint',
                'nodeKind': 'literal'  # There are no more constraints on datatypes.
            }
        else:
            node = {'type': 'Shape'}
            properties = list(source.subjects(SCHEMA['domainIncludes'], shape))
            # find all subclasses
            ancestors = list(set(ShExJParser.find_parent_classes(source, shape)))
            if len(properties) > 0:
                expression = {'type': 'EachOf', 'expressions': [ShExJParser.type_constraint(ancestors + [shape])]}
                for prop in properties:
                    expression['expressions'].append(ShExJParser.parse_property(source, prop))
                node['expression'] = expression
            else:
                node['expression'] = ShExJParser.type_constraint(ancestors + [id])
            node['extra'] = [RDF.type]
            parents = [replace_prefix(x) for x in source.objects(shape, RDFS.subClassOf)]
            if len(parents) > 0:
                node['extends'] = parents

        return {
            'type': 'ShapeDecl',
            'id': id,
            'shapeExpr': node
        }

    @staticmethod
    def type_constraint(types):
        """
        Creates rdf:type constraints

        :param types: list of possible rdf:type values
        :return: JSON(dict) with ShExJ representation of rdf:type constraints
        """
        node = {'type': 'TripleConstraint', 'predicate': RDF.type,
                'valueExpr': {'type': 'NodeConstraint', 'values': types}}
        return node

    @staticmethod
    def parse_property(source, prop):
        """
        Creates property constraints

        :param source: source rdflib graph
        :param prop: property IRI
        :return: JSON(dict) with ShExJ representation of property constraints
        """
        node = {'type': 'TripleConstraint', 'predicate': prop, 'min': 0, 'max': -1}
        prop_range = list([replace_prefix(x) for x in source.objects(prop, SCHEMA['rangeIncludes'])])
        if len(prop_range) == 1:
            node['valueExpr'] = prop_range[0]
        elif len(prop_range) > 0:
            node['valueExpr'] = {'type': 'ShapeOr', 'shapeExprs': prop_range}
        return node

    @staticmethod
    def find_parent_classes(source, shape):
        """
        Recursively finds all ancestors of the shape in the subclasses tree

        :param source: source rdflib graph
        :param shape: child shape IRI
        :return: list of all ancestor IRIs
        """
        parent_classes = list(source.objects(shape, RDFS.subClassOf))
        for parent in parent_classes:
            parent_classes.extend(ShExJParser.find_parent_classes(source, parent))
        return parent_classes

    @staticmethod
    def to_shex(source):
        """
        Creates ShExJ constraints for schema.org terms definition

        :param source: source rdflib graph
        :return: string representation of ShExJ constraints
        """
        shapes: list[URIRef] = list(source.subjects(RDF['type'], RDFS['Class']))
        shapes.sort(key=lambda u: str(u))
        top_level_datatypes: Generator[Node, None, None] = source.subjects(RDF.type, SCHEMA.DataType)
        all_datatypes: set[URIRef] = {URIRef(SCHEMA.DataType)}
        all_datatypes.update(ShExJParser.chase_subclasses(source, top_level_datatypes))

        shex = {'type': 'Schema'}
        shex['shapes'] = [ShExJParser.parse_shape(source, shape, is_datatype = shape in all_datatypes) for shape in shapes]

        return json.dumps(shex)

    @staticmethod
    def chase_subclasses(source: Graph, terms: Generator[Node, None, None]) -> Set[URIRef]:
        ret: set[URIRef] = set()
        for term in terms:
            ret.add(term)
            subclass_terms: Generator[Node, None, None] = source.subjects(RDFS.subClassOf, term)
            ret.update(ShExJParser.chase_subclasses(source, subclass_terms))
        return ret


class ShaclParser:

    @staticmethod
    def parse_shape(source, shape, dest):
        """
        Creates SHACL shape for schema.org entity

        :param source: source rdflib graph
        :param shape: target shape IRI
        :param dest: output SHACL constraints graph
        """
        node = URIRef(replace_prefix(shape))
        dest.add((node, RDF.type, SHACL['NodeShape']))
        dest.add((node, SHACL['targetClass'], shape))
        dest.add((node, SHACL['nodeKind'], SHACL['BlankNodeOrIRI']))
        properties = list(source.subjects(SCHEMA['domainIncludes'], shape))
        for prop in properties:
            dest.add((node, SHACL['property'], ShaclParser.parse_property(source, prop, dest)))

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
        dest.add((node, SHACL['path'], prop))
        property_range = list([replace_prefix(x) for x in source.objects(prop, SCHEMA['rangeIncludes'])])
        if len(property_range) > 1:
            or_node = BNode()
            or_collection = Collection(dest, or_node)
            dest.add((node, SHACL['or'], or_node))
            for shape in property_range:
                t = BNode()
                dest.add((t, SHACL['node'], shape))
                or_collection.append(t)
        else:
            dest.add((node, SHACL['node'], property_range[0]))
        return node

    @staticmethod
    def get_subclasses(source):
        """
        Creates subclasses tree

        :param source: source rdflib graph
        :return: subclasses tree rdflib graph
        """
        subclasses = Graph()
        subclasses.namespace_manager.bind('sh', SHACL)
        subclasses.namespace_manager.bind('schema', SCHEMA)
        subclasses.namespace_manager.bind('rdfs', RDFS)
        for quad in list(source[None:RDFS['subClassOf']:None]):
            subclasses.add([quad[0], RDFS['subClassOf'], quad[1]])
        return subclasses.serialize(format='turtle')

    @staticmethod
    def to_shacl(source):
        """
        Creates SHACL constraints from schema.org terms definitions

        :param source: source rdflib graph
        :return: string representation of SHACL constraints
        """
        dest = Graph()
        dest.namespace_manager.bind('sh', SHACL)
        dest.namespace_manager.bind('schema', SCHEMA)
        dest.namespace_manager.bind('', BASE)
        shapes = set(list(source.subjects(RDF['type'], RDFS['Class'])))
        for shape in shapes:
            ShaclParser.parse_shape(source, shape, dest)
        return dest.serialize(format='turtle')


def generate_files(term_defs_path, outputdir, outputfileprefix='', input_format='nt'):
    with open(term_defs_path) as term_def_file:
        term_defs = term_def_file.read()
    graph = Graph().parse(data=term_defs, format=input_format)
    graph.bind('schema', SCHEMA)

    shexj_path = os.path.join(outputdir, outputfileprefix + 'shapes.shexj')
    with open(shexj_path, 'w', encoding=FILE_ENCODING) as shexj_file:
        shexj_file.write(ShExJParser.to_shex(graph))
    print("Created %s" % shexj_path)

    shacl_path = os.path.join(outputdir, outputfileprefix + 'shapes.shacl')
    with open(shexj_path, 'w', encoding=FILE_ENCODING) as shacl_file:
        shacl_file.write(ShaclParser.to_shacl(graph))
    print("Created %s" % shacl_path)

    subclasses_tree = ShaclParser().get_subclasses(graph)
    subclasses_path = os.path.join(outputdir, outputfileprefix + 'subclasses.shacl')
    with open(subclasses_path, 'w', encoding=FILE_ENCODING) as subclasses_file:
        subclasses_file.write(ShaclParser.get_subclasses(graph))
    print("Created %s" % subclasses_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("-s","--sourcefile", help="rdf format source file")
    parser.add_argument("-f","--format", default="nt", help="source file format (default: .nt)")
    parser.add_argument("-o","--outputdir", help="output directory (default: ./)")
    parser.add_argument("-p","--outputfileprefix", default="", help="output files prefix")
    args = parser.parse_args()

    if args.sourcefile:
        term_defs_path = args.sourcefile
    else:
        term_defs_path = input('.nt terms definitions path: ')
    generate_files(
        term_defs_path = term_defs_path,
        outputdir = args.outputdir,
        outputfileprefix = args.outputfileprefix,
        input_format = args.format)


