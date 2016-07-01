# -*- coding: utf-8 -*-
"""
Encoding of the RDFa prototype vocabulary behavior. This means processing the graph by adding and removing triples
based on triples using the rdfa:Prototype and rdfa:ref class and property, respectively. For details, see the HTML5+RDFa document.


@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
@contact: Ivan Herman, ivan@w3.org
@version: $Id: prototype.py,v 1.1 2013-01-18 09:41:49 ivan Exp $
$Date: 2013-01-18 09:41:49 $
"""
import rdflib
from rdflib	import Namespace
if rdflib.__version__ >= "3.0.0" :
	from rdflib	import RDF  as ns_rdf
else :
	from rdflib.RDF	import RDFNS  as ns_rdf

from .. import ns_rdfa

Prototype = ns_rdfa["Pattern"]
pref      = ns_rdfa["copy"]

def handle_prototypes(graph) :
	to_remove = set()
	for (x,ref,PR) in graph.triples((None,pref,None)) :
		if (PR,ns_rdf["type"],Prototype) in graph :
			to_remove.add((PR,ns_rdf["type"],Prototype))
			to_remove.add((x,ref,PR))
			# there is a reference to a prototype here
			for (PR,p,y) in graph.triples((PR,None,None)) :
				if not ( p == ns_rdf["type"] and y == Prototype ) :
					graph.add((x,p,y))
					to_remove.add((PR,p,y))
	for t in to_remove : graph.remove(t)