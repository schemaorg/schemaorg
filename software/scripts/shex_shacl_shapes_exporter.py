#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import json
import rdflib
from rdflib import Graph
from rdflib import BNode, URIRef
from rdflib import Namespace
from rdflib import RDFS, RDF
from rdflib.collection import Collection

BASE = Namespace('http://schema.org/validation#')
SCHEMA = Namespace('http://schema.org/')
SHACL = Namespace('http://www.w3.org/ns/shacl#')

PREFIX = 'ValidSchema'


def replace_prefix(data):
    """
    Replaces schema.org prefix with schema.org validation prefix
    """
    return BASE[PREFIX + data.replace('http://schema.org/', '')]


class ShExJParser:
    def parse_shape(self, source, shape):
        """
        Creates shape ShExJ shape for schema.org entity

        :param source: source rdflib graph
        :param shape: entity IRI
        :return: JSON(dict) with ShEx constraints
        """
        node = {'type': 'Shape',
                'id': replace_prefix(shape)}
        properties = list(source.subjects(SCHEMA['domainIncludes'], shape))
        # find all subclasses
        ancestors = list(set(self.find_subclasses(source, shape)))
        if len(properties) > 0:
            expression = {'type': 'EachOf', 'expressions': [self.type_constraint(ancestors + [shape])]}
            for prop in properties:
                expression['expressions'].append(self.parse_property(source, prop))
            node['expression'] = expression
        else:
            node['expression'] = self.type_constraint(ancestors + [node['id']])
        node['extra'] = [RDF.type]
        parents = [replace_prefix(x) for x in source.objects(shape, RDFS.subClassOf)]
        if len(parents) > 0:
            and_node = {'type': 'ShapeAnd', 'id': node['id'], 'shapeExprs': parents + [node]}
            del node['id']
            node = and_node

        return node

    def type_constraint(self, types):
        """
        Creates rdf:type constraints

        :param types: list of possible rdf:type values
        :return: JSON(dict) with ShExJ representation of rdf:type constraints
        """
        node = {'type': 'TripleConstraint', 'predicate': RDF.type,
                'valueExpr': {'type': 'NodeConstraint', 'values': types}}
        return node

    def parse_property(self, source, prop):
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

    def find_subclasses(self, source, shape):
        """
        Recursively finds all ancestors of the shape in the subclasses tree

        :param source: source rdflib graph
        :param shape: child shape IRI
        :return: list of all ancestor IRIs
        """
        subclasses = list(source.objects(shape, RDFS.subClassOf))
        for parent in subclasses:
            subclasses.extend(self.find_subclasses(source, parent))
        return subclasses

    def to_shex(self, source):
        """
        Creates ShExJ constraints for schema.org terms definition

        :param source: source rdflib graph
        :return: string representation of ShExJ constraints
        """
        shapes = set(list(source.subjects(RDF['type'], RDFS['Class'])))
        shex = {'type': 'Schema', 'shapes': []}
        for shape in shapes:
            shex['shapes'].append(self.parse_shape(source, shape))
        return json.dumps(shex)


class ShaclParser:
    def parse_shape(self, source, shape, dest):
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
            dest.add((node, SHACL['property'], self.parse_property(source, prop, dest)))

    def parse_property(self, source, prop, dest):
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

    def get_subclasses(self, source):
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

    def to_shacl(self, source):
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
            self.parse_shape(source, shape, dest)
        return dest.serialize(format='turtle')


if __name__ == '__main__':
    term_defs_path = input('.nt terms definitions path: ')
    term_defs = open(term_defs_path).read()
    g = Graph().parse(data=term_defs, format='nt')
    g.bind('schema', SCHEMA)
    shexj = ShExJParser().to_shex(g)
    open('res.shexj', 'w',encoding='utf8').write(shexj)
    shacl = ShaclParser().to_shacl(g)
    open('res.shacl', 'w',encoding='utf8').write(shacl)
    subclasses_tree = ShaclParser().get_subclasses(g)
    open('subclasses.shacl', 'w',encoding='utf8').write(subclasses_tree)
