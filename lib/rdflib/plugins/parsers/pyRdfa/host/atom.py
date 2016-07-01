# -*- coding: utf-8 -*-
"""
Simple transfomer for Atom: the C{@typeof=""} is added to the C{<entry>} element (unless something is already there).

@summary: Add a top "about" to <head> and <body>
@requires: U{RDFLib package<http://rdflib.net>}
@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
@contact: Ivan Herman, ivan@w3.org
"""

"""
$Id: atom.py,v 1.3 2013-01-07 13:03:16 ivan Exp $
$Date: 2013-01-07 13:03:16 $
"""

def atom_add_entry_type(node, state) :
	"""
	@param node: the current node that could be modified
	@param state: current state
	@type state: L{Execution context<pyRdfa.state.ExecutionContext>}
	"""
	def res_set(node) :	
		return True in [ node.hasAttribute(a) for a in ["resource", "about", "href", "src"] ]
	
	if node.tagName == "entry" and not res_set(node) and node.hasAttribute("typeof") == False :
		node.setAttribute("typeof","")
