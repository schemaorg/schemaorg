# -*- coding: utf-8 -*-
"""
Transfomer: handles the Dublin Core recommendation for XHTML for adding DC values. What this means is that:

 - DC namespaces are defined via C{<link rel="schema.XX" value="...."/>}
 - The 'XX.term' is used much like QNames in C{<link>} and C{<meta>} elements. For the latter, the namespaced names are added to a C{@property} attribute.

This transformer adds "real" namespaces and changes the DC references in link and meta elements to abide to the
RDFa namespace syntax.

@summary: Dublin Core transformer
@requires: U{RDFLib package<http://rdflib.net>}
@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
@contact: Ivan Herman, ivan@w3.org
"""

"""
@version: $Id: DublinCore.py,v 1.4 2012-01-18 14:16:44 ivan Exp $
$Date: 2012-01-18 14:16:44 $
"""

def DC_transform(html, options, state) :
	"""
	@param html: a DOM node for the top level html element
	@param options: invocation options
	@type options: L{Options<pyRdfa.options>}
	@param state: top level execution state
	@type state: L{State<pyRdfa.state>}
	"""
	from ..host import HostLanguage
	if not( options.host_language in [ HostLanguage.xhtml, HostLanguage.html5, HostLanguage.xhtml5 ] ) :
		return
	
	# the head element is necessary; to be sure, the namespaces are set
	# on that level only
	head = None
	try :
		head = html.getElementsByTagName("head")[0]
	except :
		# no head....
		return

	# At first, the DC namespaces must be found
	dcprefixes = {}
	for link in html.getElementsByTagName("link") :
		if link.hasAttribute("rel") :
			rel = link.getAttribute("rel")
			uri = link.getAttribute("href")
			if uri != None and rel != None and rel.startswith("schema.") :
				# bingo...
				try :
					localname = rel.split(".")[1]
					head.setAttributeNS("", "xmlns:"+localname,uri)
					dcprefixes[localname] = uri
				except :
					# problem with the split; just ignore
					pass

	# get the link elements now to find the dc elements
	for link in html.getElementsByTagName("link") :
		if link.hasAttribute("rel") :
			newProp = ""
			for rel in link.getAttribute("rel").strip().split() :
				# see if there is '.' to separate the attributes
				if rel.find(".") != -1 :
					key   = rel.split(".",1)[0]
					lname = rel.split(".",1)[1]
					if key in dcprefixes and lname != "" :
						# yep, this is one of those...
						newProp += " " + key + ":" + lname
					else :
						newProp += " " + rel
				else :
					newProp += " " + rel
			link.setAttribute("rel",newProp.strip())

	# do almost the same with the meta elements...
	for meta in html.getElementsByTagName("meta") :
		if meta.hasAttribute("name") :
			newProp = ""
			for name in meta.getAttribute("name").strip().split() :
				# see if there is '.' to separate the attributes
				if name.find(".") != -1 :
					key   = name.split(".",1)[0]
					lname = name.split(".",1)[1]
					if key in dcprefixes and lname != "" :
						# yep, this is one of those...
						newProp += " " + key + ":" + lname
					else :
						newProp += " " + name
				else :
					newProp += " " + name
			meta.setAttribute("property", newProp.strip())

