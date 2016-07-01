# -*- coding: utf-8 -*-
"""
Extraction parser RDF embedded verbatim into HTML or XML files. This is based
on:

* The specification on embedding turtle into html:
    http://www.w3.org/TR/turtle/#in-html

For SVG (and currently SVG only) the method also extracts an embedded RDF/XML
data, per SVG specification

License: W3C Software License,
http://www.w3.org/Consortium/Legal/copyright-software
Author: Ivan Herman
Copyright: W3C
"""

from rdflib.parser import Parser
from .pyRdfa import pyRdfa, Options
from .pyRdfa.state import ExecutionContext
from .pyRdfa.embeddedRDF import handle_embeddedRDF
from .structureddata import _get_orig_source, _check_error

try:
    import html5lib
    assert html5lib
    html5lib = True
except ImportError:
    import warnings
    warnings.warn(
        'html5lib not found! RDFa and Microdata parsers ' +
        'will not be available.')
    html5lib = False


class HTurtle(pyRdfa):
    """
    Bastardizing the RDFa 1.1 parser to do a hturtle extractions
    """
    def __init__(self, options=None, base="", media_type=""):
        pyRdfa.__init__(self, options=options, base=base,
                        media_type=media_type, rdfa_version="1.1")

    def graph_from_DOM(self, dom, graph, pgraph=None):
        """
        Stealing the parsing function from the original class, to do
        turtle extraction only
        """

        def copyGraph(tog, fromg):
            for t in fromg:
                tog.add(t)
            for k, ns in fromg.namespaces():
                tog.bind(k, ns)

        def _process_one_node(node, graph, state):
            if handle_embeddedRDF(node, graph, state):
                # we got an RDF content that has been extracted into Graph;
                # the recursion should stop
                return
            else:
                # recurse through all the child elements of the current node
                for n in node.childNodes:
                    if n.nodeType == node.ELEMENT_NODE:
                        _process_one_node(n, graph, state)

        topElement = dom.documentElement
        state = ExecutionContext(topElement, graph, base=self.base,
                                 options=self.options, rdfa_version="1.1")
        _process_one_node(topElement, graph, state)
        if pgraph is not None:
            copyGraph(pgraph, self.options.processor_graph.graph)

# This is the parser interface as it would look when called from the rest of
# RDFLib


class HTurtleParser(Parser):
    def parse(self, source, graph, pgraph=None, media_type=""):
        """
        @param source: one of the input sources that the RDFLib package defined
        @type source: InputSource class instance
        @param graph: target graph for the triples; output graph, in RDFa spec.
        parlance
        @type graph: RDFLib Graph
        @keyword media_type: explicit setting of the preferred media type
        (a.k.a. content type) of the the RDFa source. None means the content
        type of the HTTP result is used, or a guess is made based on the
        suffix of a file
        @type media_type: string
        """
        if html5lib is False:
            raise ImportError(
                'html5lib is not installed, cannot ' +
                'use RDFa and Microdata parsers.')

        (baseURI, orig_source) = _get_orig_source(source)
        self._process(
            graph, pgraph, baseURI, orig_source, media_type=media_type)

    def _process(self, graph, baseURI, orig_source, media_type=""):
        self.options = Options(output_processor_graph=None,
                               embedded_rdf=True,
                               vocab_expansion=False,
                               vocab_cache=False)

        if media_type is None:
            media_type = ""
        processor = HTurtle(
            self.options, base=baseURI, media_type=media_type)
        processor.graph_from_source(
            orig_source, graph=graph, pgraph=None, rdfOutput=False)
        # get possible error triples to raise exceptions
        _check_error(graph)
