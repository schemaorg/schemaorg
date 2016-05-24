# -*- coding: utf-8 -*-
"""
Extracting possible embedded RDF/XML content from the file and parse it separately into the Graph. This is used, for example
by U{SVG 1.2 Tiny<http://www.w3.org/TR/SVGMobile12/>}.

@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
@contact: Ivan Herman, ivan@w3.org
@version: $Id: embeddedRDF.py,v 1.15 2012/11/16 17:51:53 ivan Exp $
"""

# Python 3 foolproof way...
try :
	from io import StringIO
except :
	from StringIO import StringIO

from .host  import HostLanguage, accept_embedded_rdf_xml, accept_embedded_turtle
from .utils import return_XML
import re, sys

def handle_embeddedRDF(node, graph, state) :
	"""
	Handles embedded RDF. There are two possibilities:
	
	 - the file is one of the XML dialects that allows for an embedded RDF/XML portion. See the L{host.accept_embedded_rdf_xml} for those (a typical example is SVG). 
	 - the file is HTML and there is a turtle portion in the C{<script>} element with type text/turtle. 
	
	@param node: a DOM node for the top level element
	@param graph: target rdf graph
	@type graph: RDFLib's Graph object instance
	@param state: the inherited state (namespaces, lang, etc)
	@type state: L{state.ExecutionContext}
	@return: whether an RDF/XML or turtle content has been detected or not. If TRUE, the RDFa processing should not occur on the node and its descendents. 
	@rtype: Boolean
	"""
	#def _get_prefixes_in_turtle() :
	#	retval = ""
	#	for key in state.term_or_curie.ns :
	#		retval += "@prefix %s: <%s> .\n" % (key, state.term_or_curie.ns[key])
	#	retval += '\n'
	#	return retval
	
	# This feature is optional!
	def _get_literal(Pnode):
		"""
		Get the full text
		@param Pnode: DOM Node
		@return: string
		"""
		rc = ""
		for node in Pnode.childNodes:
			if node.nodeType in [node.TEXT_NODE, node.CDATA_SECTION_NODE] :
				rc = rc + node.data
		# Sigh... the HTML5 parser does not recognize the CDATA escapes, ie, it just passes on the <![CDATA[ and ]]> strings:-(
		return rc.replace("<![CDATA[","").replace("]]>","")

	if state.options.embedded_rdf  :
		# Embedded turtle, per the latest Turtle draft
		if state.options.host_language in accept_embedded_turtle and node.nodeName.lower() == "script" :
			if node.hasAttribute("type") and node.getAttribute("type") == "text/turtle" :
				#prefixes = _get_prefixes_in_turtle()
				#content  = _get_literal(node)
				#rdf = StringIO(prefixes + content)
				content  = _get_literal(node)
				rdf = StringIO(content)
				try :
					graph.parse(rdf, format="n3", publicID = state.base)
					state.options.add_info("The output graph includes triples coming from an embedded Turtle script")
				except :
					(type,value,traceback) = sys.exc_info()
					state.options.add_error("Embedded Turtle content could not be parsed (problems with %s?); ignored" % value)
			return True
		elif state.options.host_language in accept_embedded_rdf_xml and node.localName == "RDF" and node.namespaceURI == "http://www.w3.org/1999/02/22-rdf-syntax-ns#" :
			rdf = StringIO(return_XML(state, node))
			try :
				graph.parse(rdf)
				state.options.add_info("The output graph includes triples coming from an embedded RDF/XML subtree")
			except :
				(type,value,traceback) = sys.exc_info()
				state.options.add_error("Embedded RDF/XML content could not parsed (problems with %s?); ignored" % value)
			return True
		else :
			return False
	else :
		return False

