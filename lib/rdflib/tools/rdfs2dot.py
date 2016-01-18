"""
A commandline tool for drawing RDFS Class diagrams in Graphviz DOT
format

You can draw the graph of an RDFS file directly:

.. code-block: bash

   rdf2dot my_rdfs_file.rdf | dot -Tpng | display
"""

import rdflib.extras.cmdlineutils

import sys
import itertools
import collections


from rdflib import XSD, RDF, RDFS


XSDTERMS = [XSD[x] for x in (
    "anyURI", "base64Binary", "boolean", "byte", "date", "dateTime", "decimal",
    "double", "duration", "float", "gDay", "gMonth", "gMonthDay", "gYear",
    "gYearMonth", "hexBinary", "ID", "IDREF", "IDREFS", "int", "integer",
    "language", "long", "Name", "NCName", "negativeInteger", "NMTOKEN",
    "NMTOKENS", "nonNegativeInteger", "nonPositiveInteger", "normalizedString",
    "positiveInteger", "QName", "short", "string", "time", "token",
    "unsignedByte", "unsignedInt", "unsignedLong", "unsignedShort")]

EDGECOLOR = "blue"
NODECOLOR = "black"
ISACOLOR = "black"


def rdfs2dot(g, stream, opts={}):
    """
    Convert the RDFS schema in a graph
    writes the dot output to the stream
    """

    fields = collections.defaultdict(set)
    nodes = {}

    def node(x):

        if x not in nodes:
            nodes[x] = "node%d" % len(nodes)
        return nodes[x]

    def label(x, g):

        l = g.value(x, RDFS.label)
        if l is None:
            try:
                l = g.namespace_manager.compute_qname(x)[2]
            except:
                pass  # bnodes and some weird URIs cannot be split
        return l

    stream.write(u"digraph { \n node [ fontname=\"DejaVu Sans\" ] ; \n")

    for x in g.subjects(RDF.type, RDFS.Class):
        n = node(x)

    for x, y in g.subject_objects(RDFS.subClassOf):
        x = node(x)
        y = node(y)
        stream.write(u"\t%s -> %s [ color=%s ] ;\n" % (y, x, ISACOLOR))

    for x in g.subjects(RDF.type, RDF.Property):
        for a, b in itertools.product(
                g.objects(x, RDFS.domain), g.objects(x, RDFS.range)):
            if b in XSDTERMS or b == RDFS.Literal:
                l = label(b, g)
                if b == RDFS.Literal:
                    l = "literal"
                fields[node(a)].add((label(x, g), l))
            else:
    #            if a in nodes and b in nodes:
                stream.write(
                    "\t%s -> %s [ color=%s, label=\"%s\" ];\n" % (
                        node(a), node(b), EDGECOLOR, label(x, g)))

    for u, n in nodes.items():
        stream.write(u"# %s %s\n" % (u, n))
        f = [u"<tr><td align='left'>%s</td><td>%s</td></tr>" %
             x for x in sorted(fields[n])]
        opstr = u"%s [ shape=none, color=%s label=< <table color='#666666'" + \
                u" cellborder=\"0\" cellspacing='0' border=\"1\"><tr>" + \
                u"<td colspan=\"2\" bgcolor='grey'><B>%s</B></td>" + \
                u"</tr>%s</table> > ] \n"
        stream.write(opstr % (n, NODECOLOR, label(u, g), u"".join(f)))

    stream.write("}\n")


def _help():
    sys.stderr.write("""
rdfs2dot.py [-f <format>] files...
Read RDF files given on STDOUT, writes a graph of the RDFS schema in
DOT language to stdout
-f specifies parser to use, if not given,

""")


def main():
    rdflib.extras.cmdlineutils.main(rdfs2dot, _help)

if __name__ == '__main__':
    main()
