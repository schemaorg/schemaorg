#!/usr/bin/env python
# -*- coding: utf-8 -*-
# https://www.w3.org/2001/sw/wiki/How_to_diff_RDF#RDFLib

# Compare two releases of schema.org

from rdflib import Graph
from rdflib.compare import to_isomorphic, graph_diff

if __name__ == '__main__':

    sdons = 'http://schema.org/'
    g1 = Graph()
    g2 = Graph()
    p = Graph()

    #       first = str(sys.argv[1])
    #	second = str(sys.argv[2]
    first = 'data/releases/2.2/schema.rdfa'
    second = 'data/releases/3.0/schema.rdfa'

    g1.parse(first, format='rdfa', pgraph=p)#, charset="utf8")
    g2.parse(second, format='rdfa', pgraph=p)#, charset="utf8")

    in_both, in_first, in_second = graph_diff(g1, g2)

    in_both.bind('schema', sdons)
    in_first.bind('schema', sdons)
    in_second.bind('schema', sdons)

    print(n_both.serialize(format="n3"))

#	print in_first.serialize(format="n3")
#	print in_second.serialize(format="n3")
