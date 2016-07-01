# -*- coding: utf-8 -*-
"""
Host language sub-package for the pyRdfa package. It contains variables and possible modules necessary to manage various RDFa
host languages.

This module may have to be modified if a new host language is added to the system. In many cases the rdfa_core as a host language is enough, because there is no need for a special processing. However, some host languages may require an initial context, or their value may control some transformations, in which case additional data have to be added to this module. This module header contains all tables and arrays to be adapted, and the module content may contain specific transformation methods.


@summary: RDFa Host package
@requires: U{RDFLib package<http://rdflib.net>}
@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}

@var content_to_host_language: a dictionary mapping a media type to a host language
@var preferred_suffixes: mapping from preferred suffixes for media types; used if the file is local, ie, there is not HTTP return value for the media type. It corresponds to the preferred suffix in the media type registration
@var initial_contexts: mapping from host languages to list of initial contexts
@var accept_xml_base: list of host languages that accept the xml:base attribute for base setting
@var accept_xml_lang: list of host languages that accept the xml:lang attribute for language setting. Note that XHTML and HTML have some special rules, and those are hard coded...
@var warn_xmlns_usage: list of host languages that should generate a warning for the usage of @xmlns (for RDFa 1.1)
@var accept_embedded_rdf_xml: list of host languages that might also include RDF data using an embedded RDF/XML (e.g., SVG). That RDF data may be merged with the output
@var accept_embedded_turtle: list of host languages that might also include RDF data using a C{script} element. That RDF data may be merged with the output
@var require_embedded_rdf: list of languages that must accept embedded RDF, ie, the corresponding option is irrelevant
@var host_dom_transforms: dictionary mapping a host language to an array of methods that are invoked at the beginning of the parsing process for a specific node. That function can do a last minute change on that DOM node, eg, adding or modifying an attribute. The method's signature is (node, state), where node is the DOM node, and state is the L{Execution context<pyRdfa.state.ExecutionContext>}.
@var predefined_1_0_rel: terms that are hardcoded for HTML+RDF1.0 and replace the initial context for that version
@var beautifying_prefixes: this is really just to make the output more attractive: for each media type a dictionary of prefix-URI pairs that can be used to make the terms look better...
@var default_vocabulary: as its name suggests, default @vocab value for a specific host language

"""

"""
$Id: __init__.py,v 1.21 2013-10-16 11:49:11 ivan Exp $
$Date: 2013-10-16 11:49:11 $
"""
__version__ = "3.0"

from .atom  import atom_add_entry_type
from .html5 import html5_extra_attributes, remove_rel

class HostLanguage :
	"""An enumeration style class: recognized host language types for this processor of RDFa. Some processing details may depend on these host languages. "rdfa_core" is the default Host Language is nothing else is defined."""
	rdfa_core 	= "RDFa Core"
	xhtml		= "XHTML+RDFa"
	xhtml5		= "XHTML5+RDFa"
	html5		= "HTML5+RDFa"
	atom		= "Atom+RDFa"
	svg			= "SVG+RDFa"
	
# initial contexts for host languages
initial_contexts = {
	HostLanguage.xhtml      : ["http://www.w3.org/2011/rdfa-context/rdfa-1.1",
                               "http://www.w3.org/2011/rdfa-context/xhtml-rdfa-1.1"],
	HostLanguage.xhtml5     : ["http://www.w3.org/2011/rdfa-context/rdfa-1.1"],
	HostLanguage.html5      : ["http://www.w3.org/2011/rdfa-context/rdfa-1.1"],
	HostLanguage.rdfa_core  : ["http://www.w3.org/2011/rdfa-context/rdfa-1.1"],
	HostLanguage.atom       : ["http://www.w3.org/2011/rdfa-context/rdfa-1.1"],
	HostLanguage.svg        : ["http://www.w3.org/2011/rdfa-context/rdfa-1.1"],
}

beautifying_prefixes = {
	HostLanguage.xhtml	: {
		"xhv" : "http://www.w3.org/1999/xhtml/vocab#"
	},
	# HostLanguage.html5	: {
	# 	"xhv" : "http://www.w3.org/1999/xhtml/vocab#"
	# },	
	# HostLanguage.xhtml5	: {
	# 	"xhv" : "http://www.w3.org/1999/xhtml/vocab#"
	# },
	HostLanguage.atom : {
		"atomrel" : "http://www.iana.org/assignments/relation/"
	}
}


accept_xml_base		= [ HostLanguage.rdfa_core, HostLanguage.atom, HostLanguage.svg,  HostLanguage.xhtml5 ]
accept_xml_lang		= [ HostLanguage.rdfa_core, HostLanguage.atom, HostLanguage.svg ]

accept_embedded_rdf_xml	= [ HostLanguage.svg, HostLanguage.rdfa_core ]
accept_embedded_turtle	= [ HostLanguage.svg, HostLanguage.html5, HostLanguage.xhtml5, HostLanguage.xhtml ]

# some languages, eg, SVG, require that embedded content should be combined with the default graph,
# ie, it cannot be turned down by an option
require_embedded_rdf    = [ HostLanguage.svg ]

warn_xmlns_usage = [ HostLanguage.html5, HostLanguage.xhtml5, HostLanguage.xhtml ]

host_dom_transforms = {
	HostLanguage.atom   : [atom_add_entry_type],
	HostLanguage.html5  : [html5_extra_attributes, remove_rel],
	HostLanguage.xhtml5 : [html5_extra_attributes, remove_rel]
}

default_vocabulary = {
	HostLanguage.atom : "http://www.iana.org/assignments/relation/"
}

predefined_1_0_rel  = ['alternate', 'appendix', 'cite', 'bookmark', 'chapter', 'contents',
'copyright', 'glossary', 'help', 'icon', 'index', 'meta', 'next', 'p3pv1', 'prev', 'previous', 
'role', 'section', 'subsection', 'start', 'license', 'up', 'last', 'stylesheet', 'first', 'top']

# ----------------------------------------------------------------------------------------------------------
		
class MediaTypes :
	"""An enumeration style class: some common media types (better have them at one place to avoid misstyping...)"""
	rdfxml 	= 'application/rdf+xml'
	turtle 	= 'text/turtle'
	html	= 'text/html'
	xhtml	= 'application/xhtml+xml'
	svg		= 'application/svg+xml'
	svgi	= 'image/svg+xml'
	smil	= 'application/smil+xml'
	atom	= 'application/atom+xml'
	xml		= 'application/xml'
	xmlt	= 'text/xml'
	nt		= 'text/plain'
	
# mapping from (some) content types to RDFa host languages. This may control the exact processing or at least the initial context (see below)...
content_to_host_language = {
	MediaTypes.html		: HostLanguage.html5,
	MediaTypes.xhtml	: HostLanguage.xhtml,
	MediaTypes.xml		: HostLanguage.rdfa_core,
	MediaTypes.xmlt		: HostLanguage.rdfa_core,
	MediaTypes.smil		: HostLanguage.rdfa_core,
	MediaTypes.svg		: HostLanguage.svg,
	MediaTypes.svgi		: HostLanguage.svg,
	MediaTypes.atom		: HostLanguage.atom,
}

# mapping preferred suffixes to media types...
preferred_suffixes = {
	".rdf"		: MediaTypes.rdfxml,
	".ttl"		: MediaTypes.turtle,
	".n3"		: MediaTypes.turtle,
	".owl"		: MediaTypes.rdfxml,
	".html"		: MediaTypes.html,
	".shtml"    : MediaTypes.html,
	".xhtml"	: MediaTypes.xhtml,
	".svg"		: MediaTypes.svg,
	".smil"		: MediaTypes.smil,
	".xml"		: MediaTypes.xml,
	".nt"		: MediaTypes.nt,
	".atom"		: MediaTypes.atom
}
	
# DTD combinations that may determine the host language and the rdfa version
_XHTML_1_0 = [
	("-//W3C//DTD XHTML+RDFa 1.0//EN", "http://www.w3.org/MarkUp/DTD/xhtml-rdfa-1.dtd")
]

_XHTML_1_1 = [
	("-//W3C//DTD XHTML+RDFa 1.1//EN", "http://www.w3.org/MarkUp/DTD/xhtml-rdfa-2.dtd"),
	("-//W3C//DTD HTML 4.01+RDFa 1.1//EN", "http://www.w3.org/MarkUp/DTD/html401-rdfa11-1.dtd")	
]

_XHTML = [
	("-//W3C//DTD XHTML 1.0 Strict//EN",       "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd"),
	("-//W3C//DTD XHTML 1.0 Transitional//EN", "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd"),
	("-//W3C//DTD XHTML 1.1//EN",              "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd")	
]

def adjust_html_version(input, rdfa_version) :
	"""
	Adjust the rdfa_version based on the (possible) DTD
	@param input: the input stream that has to be parsed by an xml parser
	@param rdfa_version: the current rdfa_version; will be returned if nothing else is found
	@return: the rdfa_version, either "1.0" or "1.1, if the DTD says so, otherwise the input rdfa_version value
	"""
	import xml.dom.minidom
	parse = xml.dom.minidom.parse
	dom = parse(input)
	
	(hl,version) = adjust_xhtml_and_version(dom, HostLanguage.xhtml, rdfa_version)
	return version
	
def adjust_xhtml_and_version(dom, incoming_language, rdfa_version) :
	"""
	Check if the xhtml+RDFa is really XHTML 0 or 1 or whether it should be considered as XHTML5. This is done
	by looking at the DTD. Furthermore, checks whether whether the system id signals an rdfa 1.0, in which case the
	version is also set.
	
	@param dom: top level DOM node
	@param incoming_language: host language to be checked; the whole check is relevant for xhtml only.
	@param rdfa_version: rdfa_version as known by the caller
	@return: a tuple of the possibly modified host language (ie, set to XHTML5) and the possibly modified rdfa version (ie, set to "1.0", "1.1", or the incoming rdfa_version if nothing is found)
	"""
	if incoming_language == HostLanguage.xhtml :
		try :
			# There may not be any doctype set in the first place...
			publicId = dom.doctype.publicId
			systemId = dom.doctype.systemId

			if (publicId, systemId) in _XHTML_1_0 :
				return (HostLanguage.xhtml,"1.0")
			elif (publicId, systemId) in _XHTML_1_1 :
				return (HostLanguage.xhtml,"1.1")
			elif (publicId, systemId) in _XHTML :
				return (HostLanguage.xhtml, rdfa_version)
			else :
				return (HostLanguage.xhtml5, rdfa_version)
		except :
			# If any of those are missing, forget it...
			return (HostLanguage.xhtml5, rdfa_version)
	else :
		return (incoming_language, rdfa_version)

