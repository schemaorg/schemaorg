# -*- coding: utf-8 -*-
"""

@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
@contact: Ivan Herman, ivan@w3.org
@version: $Id: lite.py,v 1.11 2013-09-26 16:37:54 ivan Exp $
$Date: 2013-09-26 16:37:54 $
"""

from ..host        import HostLanguage

non_lite_attributes      = ["about","inlist","datatype","rev","rel","content"]
non_lite_attributes_html = ["about","inlist","datatype","rev"]

def lite_prune(top, options, state) :
	"""
	This is a misnomer. The current version does not remove anything from the tree, just generates warnings as for the
	usage of non-lite attributes. A more aggressive version would mean to remove those attributes, but that would,
	in fact, define an RDFa Lite conformance level in the parser, which is against the WG decisions. So this should
	not be done; the corresponding commands are commented in the code below...
	
	@param top: a DOM node for the top level element
	@param options: invocation options
	@type options: L{Options<pyRdfa.options>}
	@param state: top level execution state
	@type state: L{State<pyRdfa.state>}
	"""
	def generate_warning(node, attr) :
		if attr == "rel" :
			msg = "Attribute @rel should not be used in RDFa Lite (consider using @property)"
		elif attr == "about" :
			msg = "Attribute @about should not be used in RDFa Lite (consider using a <link> element with @href or @resource)"
		else :
			msg = "Attribute @%s should not be used in RDFa Lite" % attr
		options.add_warning(msg, node=node)

	def remove_attrs(node) :
		from ..termorcurie import termname
		# first the @content; this has a special treatment
		# there are some extras to check for HTML dialects
		if options.host_language in [ HostLanguage.html5, HostLanguage.xhtml5, HostLanguage.xhtml ] :
			if node.tagName != "meta" and node.hasAttribute("content") :
				generate_warning(node, "content")
				# node.removeAttribute("content")
			if node.tagName != "link" and node.hasAttribute("rel") :
				# Unfortunately, this has to be checked separately and run-time for <link> where @rel is allowed for non-RDFa purposes...
				# Additional complication: @rel is allowed in an <a> element, for example, if used as a pure term and not as a URI or CURIE
				if node.tagName == "a" :
					vals = node.getAttribute("rel").strip().split()
					if len(vals) != 0 :
						final_vals = [ v for v in vals if not termname.match(v) ]
						if len(final_vals) != 0 :
							generate_warning(node, "rel")
				else :
					generate_warning(node, "rel")
			for attr in non_lite_attributes_html :
				if node.hasAttribute(attr) :
					generate_warning(node, attr)
					# node.removeAttribute(attr)
		else :
			for attr in non_lite_attributes :
				if node.hasAttribute(attr) :
					generate_warning(node, attr)
					# node.removeAttribute(attr)

	remove_attrs(top)
	for n in top.childNodes :
		if n.nodeType == top.ELEMENT_NODE :
			lite_prune(n, options, state)

	