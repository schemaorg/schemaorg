# -*- coding: utf-8 -*-
"""
Built-in version of the initial contexts for RDFa Core, and RDFa + HTML

@summary: Management of vocabularies, terms, and their mapping to URI-s.
@requires: U{RDFLib package<http://rdflib.net>}
@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}

@var initial_context: dictionary for all the initial context data, keyed through the context URI-s
"""

class Wrapper :
	pass
	
initial_context = {
	"http://www.w3.org/2011/rdfa-context/rdfa-1.1" 		 : Wrapper(),
	"http://www.w3.org/2011/rdfa-context/xhtml-rdfa-1.1" : Wrapper(),
}

initial_context["http://www.w3.org/2011/rdfa-context/rdfa-1.1"].ns = {
	'dcat'		: 'http://www.w3.org/ns/dcat#',
    'qb'		: 'http://purl.org/linked-data/cube#',
    'org'		: 'http://www.w3.org/ns/org#',
	'owl'		: 'http://www.w3.org/2002/07/owl#',
	'gr'		: 'http://purl.org/goodrelations/v1#',
	'ctag'		: 'http://commontag.org/ns#',
	'cc'		: 'http://creativecommons.org/ns#',
	'grddl'		: 'http://www.w3.org/2003/g/data-view#',
	'rif'		: 'http://www.w3.org/2007/rif#',
	'sioc'		: 'http://rdfs.org/sioc/ns#',
	'skos'		: 'http://www.w3.org/2004/02/skos/core#',
	'xml'		: 'http://www.w3.org/XML/1998/namespace',
	'rr'		: 'http://www.w3.org/ns/r2rml#',
	'rdfs'		: 'http://www.w3.org/2000/01/rdf-schema#',
	'rev'		: 'http://purl.org/stuff/rev#',
	'rdfa'		: 'http://www.w3.org/ns/rdfa#',
	'dc'		: 'http://purl.org/dc/terms/',
	'dcterms'	: 'http://purl.org/dc/terms/',
	'dc11'	    : 'http://purl.org/dc/elements/1.1/',	
	'foaf'		: 'http://xmlns.com/foaf/0.1/',
	'void'		: 'http://rdfs.org/ns/void#',
	'ical'		: 'http://www.w3.org/2002/12/cal/icaltzd#',
	'vcard'		: 'http://www.w3.org/2006/vcard/ns#',
	'wdrs'		: 'http://www.w3.org/2007/05/powder-s#',
	'og'		: 'http://ogp.me/ns#',
	'wdr'		: 'http://www.w3.org/2007/05/powder#',
	'rdf'		: 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
	'xhv'		: 'http://www.w3.org/1999/xhtml/vocab#',
	'xsd'		: 'http://www.w3.org/2001/XMLSchema#',
	'v'			: 'http://rdf.data-vocabulary.org/#',
	'skosxl'	: 'http://www.w3.org/2008/05/skos-xl#',
	'schema'	: 'http://schema.org/',
	'ma'		: 'http://www.w3.org/ns/ma-ont#',
	'sd'        : 'http://www.w3.org/ns/sparql-service-description#',
	'prov'      : 'http://www.w3.org/ns/prov#',
}

initial_context["http://www.w3.org/2011/rdfa-context/rdfa-1.1"].terms = {
	'describedby'	: 'http://www.w3.org/2007/05/powder-s#describedby',
	'role'			: 'http://www.w3.org/1999/xhtml/vocab#role',
	'license'		: 'http://www.w3.org/1999/xhtml/vocab#license',
}

initial_context["http://www.w3.org/2011/rdfa-context/rdfa-1.1"].vocabulary = ""

initial_context["http://www.w3.org/2011/rdfa-context/xhtml-rdfa-1.1"].ns = {
}

initial_context["http://www.w3.org/2011/rdfa-context/xhtml-rdfa-1.1"].vocabulary = ""

initial_context["http://www.w3.org/2011/rdfa-context/xhtml-rdfa-1.1"].terms = {
	'alternate'				: 'http://www.w3.org/1999/xhtml/vocab#alternate',
	'appendix'				: 'http://www.w3.org/1999/xhtml/vocab#appendix',
	'cite'					: 'http://www.w3.org/1999/xhtml/vocab#cite',
	'bookmark'				: 'http://www.w3.org/1999/xhtml/vocab#bookmark',
	'chapter'				: 'http://www.w3.org/1999/xhtml/vocab#chapter',
	'contents'				: 'http://www.w3.org/1999/xhtml/vocab#contents',
	'copyright'				: 'http://www.w3.org/1999/xhtml/vocab#copyright',
	'glossary'				: 'http://www.w3.org/1999/xhtml/vocab#glossary',
	'help'					: 'http://www.w3.org/1999/xhtml/vocab#help',
	'icon'					: 'http://www.w3.org/1999/xhtml/vocab#icon',
	'index'					: 'http://www.w3.org/1999/xhtml/vocab#index',
	'meta'					: 'http://www.w3.org/1999/xhtml/vocab#meta',
	'next'					: 'http://www.w3.org/1999/xhtml/vocab#next',
	'license'				: 'http://www.w3.org/1999/xhtml/vocab#license',
	'p3pv1'					: 'http://www.w3.org/1999/xhtml/vocab#p3pv1',
	'prev'					: 'http://www.w3.org/1999/xhtml/vocab#prev',
	'previous'				: 'http://www.w3.org/1999/xhtml/vocab#previous',
	'role'					: 'http://www.w3.org/1999/xhtml/vocab#role',
	'section'				: 'http://www.w3.org/1999/xhtml/vocab#section',
	'stylesheet'			: 'http://www.w3.org/1999/xhtml/vocab#stylesheet',
	'subsection'			: 'http://www.w3.org/1999/xhtml/vocab#subsection',
	'start'					: 'http://www.w3.org/1999/xhtml/vocab#start',
	'up'					: 'http://www.w3.org/1999/xhtml/vocab#up',
	'last'					: 'http://www.w3.org/1999/xhtml/vocab#last',
	'first'					: 'http://www.w3.org/1999/xhtml/vocab#first',
	'top'					: 'http://www.w3.org/1999/xhtml/vocab#top',
}

