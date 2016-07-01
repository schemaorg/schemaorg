# -*- coding: utf-8 -*-
"""
This serialiser will output an RDF Graph as a JSON-LD formatted document. See:

    http://json-ld.org/

Example usage::

    >>> from rdflib.plugin import register, Serializer
    >>> register('json-ld', Serializer, 'rdflib_jsonld.serializer', 'JsonLDSerializer')

    >>> from rdflib import Graph

    >>> testrdf = '''
    ... @prefix dc: <http://purl.org/dc/terms/> .
    ... <http://example.org/about>
    ...     dc:title "Someone's Homepage"@en .
    ... '''

    >>> g = Graph().parse(data=testrdf, format='n3')

    >>> print(g.serialize(format='json-ld', indent=4).decode())
    [
        {
            "@id": "http://example.org/about",
            "http://purl.org/dc/terms/title": [
                {
                    "@language": "en",
                    "@value": "Someone's Homepage"
                }
            ]
        }
    ]

"""

# NOTE: This code writes the entire JSON object into memory before serialising,
# but we should consider streaming the output to deal with arbitrarily large
# graphs.

import warnings

from rdflib.serializer import Serializer
from rdflib.graph import Graph
from rdflib.term import URIRef, Literal, BNode
from rdflib.namespace import RDF, XSD

from .context import Context, UNDEF
from .util import json
from .keys import CONTEXT, GRAPH, ID, VOCAB, LIST, SET, LANG

__all__ = ['JsonLDSerializer', 'from_rdf']


PLAIN_LITERAL_TYPES = set([XSD.boolean, XSD.integer, XSD.double, XSD.string])


class JsonLDSerializer(Serializer):
    def __init__(self, store):
        super(JsonLDSerializer, self).__init__(store)

    def serialize(self, stream, base=None, encoding=None, **kwargs):
        # TODO: docstring w. args and return value
        encoding = encoding or 'utf-8'
        if encoding not in ('utf-8', 'utf-16'):
            warnings.warn("JSON should be encoded as unicode. " +
                          "Given encoding was: %s" % encoding)

        context_data = kwargs.get('context')
        use_native_types = kwargs.get('use_native_types', True),
        use_rdf_type = kwargs.get('use_rdf_type', False)
        auto_compact = kwargs.get('auto_compact', True)

        indent = kwargs.get('indent', 2)
        separators = kwargs.get('separators', (',', ': '))
        sort_keys = kwargs.get('sort_keys', True)
        ensure_ascii = kwargs.get('ensure_ascii', False)

        obj = from_rdf(self.store, context_data, base,
                use_native_types, use_rdf_type,
                auto_compact=auto_compact)

        data = json.dumps(obj, indent=indent, separators=separators,
                          sort_keys=sort_keys, ensure_ascii=ensure_ascii)

        stream.write(data.encode(encoding, 'replace'))


def from_rdf(graph, context_data=None, base=None,
        use_native_types=False, use_rdf_type=False,
        auto_compact=False, startnode=None, index=False):
    # TODO: docstring w. args and return value
    # TODO: support for index and startnode

    if not context_data and auto_compact:
        context_data = dict(
            (pfx, unicode(ns))
            for (pfx, ns) in graph.namespaces() if pfx and
            unicode(ns) != u"http://www.w3.org/XML/1998/namespace")

    if isinstance(context_data, Context):
        context = context_data
        context_data = context.to_dict()
    else:
        context = Context(context_data, base=base)

    converter = Converter(context, use_native_types, use_rdf_type)
    result = converter.convert(graph)

    if converter.context.active:
        if isinstance(result, list):
            result = {context.get_key(GRAPH): result}
        result[CONTEXT] = context_data

    return result


class Converter(object):

    def __init__(self, context, use_native_types, use_rdf_type):
        self.context = context
        self.use_native_types = context.active or use_native_types
        self.use_rdf_type = use_rdf_type

    def convert(self, graph):
        # TODO: bug in rdflib dataset parsing (nquads et al):
        # plain triples end up in separate unnamed graphs (rdflib issue #436)
        if graph.context_aware:
            default_graph = Graph()
            graphs = [default_graph]
            for g in graph.contexts():
                if isinstance(g.identifier, URIRef):
                    graphs.append(g)
                else:
                    default_graph += g
        else:
            graphs = [graph]

        context = self.context

        objs = []
        for g in graphs:
            obj = {}
            graphname = None

            if isinstance(g.identifier, URIRef):
                graphname = context.shrink_iri(g.identifier)
                obj[context.id_key] = graphname

            nodes = self.from_graph(g)

            if not graphname and len(nodes) == 1:
                obj.update(nodes[0])
            else:
                if not nodes:
                    continue
                obj[context.graph_key] = nodes

            if objs and objs[0].get(context.get_key(ID)) == graphname:
                objs[0].update(obj)
            else:
                objs.append(obj)

        if len(graphs) == 1 and len(objs) == 1 and not self.context.active:
            default = objs[0]
            items = default.get(context.graph_key)
            if len(default) == 1 and items:
                objs = items
        elif len(objs) == 1 and self.context.active:
            objs = objs[0]

        return objs

    def from_graph(self, graph):
        nodemap = {}

        for s in set(graph.subjects()):
            ## only iri:s and unreferenced (rest will be promoted to top if needed)
            if isinstance(s, URIRef) or (isinstance(s, BNode)
                    and not any(graph.subjects(None, s))):
                self.process_subject(graph, s, nodemap)

        return nodemap.values()

    def process_subject(self, graph, s, nodemap):
        if isinstance(s, URIRef):
            node_id = self.context.shrink_iri(s)
        elif isinstance(s, BNode):
            node_id = s.n3()
        else:
            node_id = None

        #used_as_object = any(graph.subjects(None, s))
        if node_id in nodemap:
            return None

        node = {}
        node[self.context.id_key] = node_id
        nodemap[node_id] = node

        for p, o in graph.predicate_objects(s):
            self.add_to_node(graph, s, p, o, node, nodemap)

        return node

    def add_to_node(self, graph, s, p, o, s_node, nodemap):
        context = self.context

        if isinstance(o, Literal):
            datatype = unicode(o.datatype) if o.datatype else None
            language = o.language
            term = context.find_term(unicode(p), datatype, language=language)
        else:
            containers = [LIST, None] if graph.value(o, RDF.first) else [None]
            for container in containers:
                for coercion in (ID, VOCAB, UNDEF):
                    term = context.find_term(unicode(p), coercion, container)
                    if term:
                        break
                if term:
                    break

        node = None
        use_set = not context.active

        if term:
            p_key = term.name

            if term.type:
                node = self.type_coerce(o, term.type)
            elif term.language and o.language == term.language:
                node = unicode(o)
            elif context.language and (
                    term.language is None and o.language is None):
                node = unicode(o)

            if term.container == SET:
                use_set = True
            elif term.container == LIST:
                node = [self.type_coerce(v, term.type) or self.to_raw_value(graph, s, v, nodemap)
                        for v in self.to_collection(graph, o)]
            elif term.container == LANG and language:
                value = s_node.setdefault(p_key, {})
                values = value.get(language)
                node = unicode(o)
                if values:
                    if not isinstance(values, list):
                        value[language] = values = [values]
                    values.append(node)
                else:
                    value[language] = node
                return

        else:
            p_key = context.to_symbol(p)
            # TODO: for coercing curies - quite clumsy; unify to_symbol and find_term?
            key_term = context.terms.get(p_key)
            if key_term and (key_term.type or key_term.container):
                p_key = p
            if not term and p == RDF.type and not self.use_rdf_type:
                if isinstance(o, URIRef):
                    node = context.to_symbol(o)
                p_key = context.type_key

        if node is None:
            node = self.to_raw_value(graph, s, o, nodemap)

        value = s_node.get(p_key)
        if value:
            if not isinstance(value, list):
                value = [value]
            value.append(node)
        elif use_set:
            value = [node]
        else:
            value = node
        s_node[p_key] = value

    def type_coerce(self, o, coerce_type):
        if coerce_type == ID:
            if isinstance(o, URIRef):
                return self.context.shrink_iri(o)
            elif isinstance(o, BNode):
                return o.n3()
            else:
                return o
        elif coerce_type == VOCAB and isinstance(o, URIRef):
            return self.context.to_symbol(o)
        elif isinstance(o, Literal) and unicode(o.datatype) == coerce_type:
            return o
        else:
            return None

    def to_raw_value(self, graph, s, o, nodemap):
        context = self.context
        coll = self.to_collection(graph, o)
        if coll is not None:
            coll = [self.to_raw_value(graph, s, lo, nodemap)
                    for lo in self.to_collection(graph, o)]
            return {context.list_key: coll}
        elif isinstance(o, BNode):
            embed = False # TODO: self.context.active or using startnode and only one ref
            onode = self.process_subject(graph, o, nodemap)
            if onode:
                if embed and not any(s2 for s2 in graph.subjects(None, o) if s2 != s):
                    return onode
                else:
                    nodemap[onode[context.id_key]] = onode
            return {context.id_key: o.n3()}
        elif isinstance(o, URIRef):
            # TODO: embed if o != startnode (else reverse)
            return {context.id_key: context.shrink_iri(o)}
        elif isinstance(o, Literal):
            # TODO: if compact
            native = self.use_native_types and o.datatype in PLAIN_LITERAL_TYPES
            if native:
                v = o.toPython()
            else:
                v = unicode(o)
            if o.datatype:
                if native:
                    if self.context.active:
                        return v
                    else:
                        return {context.value_key: v}
                return {context.type_key: context.to_symbol(o.datatype),
                        context.value_key: v}
            elif o.language and o.language != context.language:
                return {context.lang_key: o.language,
                        context.value_key: v}
            elif not context.active or context.language and not o.language:
                return {context.value_key: v}
            else:
                return v

    def to_collection(self, graph, l):
        if l != RDF.nil and not graph.value(l, RDF.first):
            return None
        list_nodes = []
        chain = set([l])
        while l:
            if l == RDF.nil:
                return list_nodes
            if isinstance(l, URIRef):
                return None
            first, rest = None, None
            for p, o in graph.predicate_objects(l):
                if not first and p == RDF.first:
                    first = o
                elif not rest and p == RDF.rest:
                    rest = o
                elif p != RDF.type or o != RDF.List:
                    return None
            list_nodes.append(first)
            l = rest
            if l in chain:
                return None
            chain.add(l)
