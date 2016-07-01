# -*- coding: utf-8 -*-
"""
Management of vocabularies, terms, and their mapping to URI-s. The main class of this module (L{TermOrCurie}) is,
conceptually, part of the overall state of processing at a node (L{state.ExecutionContext}) but putting it into a separate
module makes it easider to maintain.

@summary: Management of vocabularies, terms, and their mapping to URI-s.
@requires: U{RDFLib package<http://rdflib.net>}
@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}

@var XHTML_PREFIX: prefix for the XHTML vocabulary URI (set to 'xhv')
@var XHTML_URI: URI prefix of the XHTML vocabulary
@var ncname: Regular expression object for NCNAME
@var termname: Regular expression object for a term
@var xml_application_media_type: Regular expression object for a general XML application media type
"""

"""
$Id: termorcurie.py,v 1.12 2013-10-16 11:48:54 ivan Exp $
$Date: 2013-10-16 11:48:54 $
"""

import re, sys
import xml.dom.minidom
import random

if sys.version_info[0] >= 3 :
	from urllib.parse import urlsplit
else :	
	from urlparse import urlsplit


import rdflib
from rdflib	import URIRef
from rdflib	import Literal
from rdflib	import BNode
from rdflib	import Namespace
if rdflib.__version__ >= "3.0.0" :
	from rdflib	import Graph
	from rdflib	import RDF  as ns_rdf
	from rdflib	import RDFS as ns_rdfs
else :
	from rdflib.Graph	import Graph
	from rdflib.RDFS	import RDFSNS as ns_rdfs
	from rdflib.RDF		import RDFNS  as ns_rdf

from .options		import Options
from .utils 		import quote_URI, URIOpener
from .host 			import MediaTypes, HostLanguage, predefined_1_0_rel, warn_xmlns_usage
from .				import IncorrectPrefixDefinition, RDFA_VOCAB, UnresolvableReference, PrefixRedefinitionWarning
from .				import ns_rdfa

from . import err_redefining_URI_as_prefix		
from . import err_xmlns_deprecated				
from . import err_bnode_local_prefix				
from . import err_col_local_prefix				
from . import err_missing_URI_prefix				
from . import err_invalid_prefix					
from . import err_no_default_prefix				
from . import err_prefix_and_xmlns				
from . import err_non_ncname_prefix				
from . import err_absolute_reference				
from . import err_query_reference				
from . import err_fragment_reference
from . import err_prefix_redefinition


# Regular expression object for NCNAME
ncname   = re.compile("^[A-Za-z][A-Za-z0-9._-]*$")

# Regular expression object for term name
termname = re.compile("^[A-Za-z]([A-Za-z0-9._-]|/)*$")

# Regular expression object for a general XML application media type
xml_application_media_type = re.compile("application/[a-zA-Z0-9]+\+xml")

XHTML_PREFIX = "xhv"
XHTML_URI    = "http://www.w3.org/1999/xhtml/vocab#"

#### Managing blank nodes for CURIE-s: mapping from local names to blank nodes.
_bnodes = {}
_empty_bnode = BNode()

####

class InitialContext :
	"""
	Get the initial context values. In most cases this class has an empty content, except for the
	top level (in case of RDFa 1.1). Each L{TermOrCurie} class has one instance of this class. It provides initial
	mappings for terms, namespace prefixes, etc, that the top level L{TermOrCurie} instance uses for its own initialization.
	
	@ivar terms: collection of all term mappings
	@type terms: dictionary
	@ivar ns: namespace mapping
	@type ns: dictionary
	@ivar vocabulary: default vocabulary
	@type vocabulary: string
	"""	
	
	def __init__(self, state, top_level) :
		"""
		@param state: the state behind this term mapping
		@type state: L{state.ExecutionContext}
		@param top_level : whether this is the top node of the DOM tree (the only place where initial contexts are handled)
		@type top_level : boolean
		"""		
		self.state = state

		# This is to store the local terms
		self.terms  = {}
		# This is to store the local Namespaces (a.k.a. prefixes)
		self.ns     = {}
		# Default vocabulary
		self.vocabulary = None
		
		if state.rdfa_version < "1.1" or top_level == False :
			return
		
		from .initialcontext	import initial_context    as context_data
		from .host 				import initial_contexts   as context_ids
		from .host				import default_vocabulary

		for id in context_ids[state.options.host_language] :
			# This gives the id of a initial context, valid for this media type:
			data = context_data[id]
			
			# Merge the context data with the overall definition
			if state.options.host_language in default_vocabulary :
				self.vocabulary = default_vocabulary[state.options.host_language]
			elif data.vocabulary != "" :
				self.vocabulary = data.vocabulary

			for key in data.terms :
				self.terms[key] = URIRef(data.terms[key])
			for key in data.ns :
				self.ns[key] = (Namespace(data.ns[key]),False)


##################################################################################################################

class TermOrCurie :
	"""
	Wrapper around vocabulary management, ie, mapping a term to a URI, as well as a CURIE to a URI. Each instance of this class belongs to a
	"state", instance of L{state.ExecutionContext}. Context definitions are managed at initialization time.
	
	(In fact, this class is, conceptually, part of the overall state at a node, and has been separated here for an
	easier maintenance.)
	
	The class takes care of the stack-like behavior of vocabulary items, ie, inheriting everything that is possible
	from the "parent". At initialization time, this works through the prefix definitions (i.e., C{@prefix} or C{@xmln:} attributes)
	and/or C{@vocab} attributes.
	
	@ivar state: State to which this instance belongs
	@type state: L{state.ExecutionContext}
	@ivar graph: The RDF Graph under generation
	@type graph: rdflib.Graph
	@ivar terms: mapping from terms to URI-s
	@type terms: dictionary
	@ivar ns: namespace declarations, ie, mapping from prefixes to URIs
	@type ns: dictionary
	@ivar default_curie_uri: URI for a default CURIE
	"""
	def __init__(self, state, graph, inherited_state) :
		"""Initialize the vocab bound to a specific state. 
		@param state: the state to which this vocab instance belongs to
		@type state: L{state.ExecutionContext}
		@param graph: the RDF graph being worked on
		@type graph: rdflib.Graph
		@param inherited_state: the state inherited by the current state. 'None' if this is the top level state.
		@type inherited_state: L{state.ExecutionContext}
		"""
		def check_prefix(pr) :
			from . import uri_schemes
			if pr in uri_schemes :
				# The prefix being defined is a registered URI scheme, better avoid it...
				state.options.add_warning(err_redefining_URI_as_prefix % pr, node=state.node.nodeName)
				
		self.state	= state
		self.graph	= graph
		
		# --------------------------------------------------------------------------------
		# This is set to non-void only on the top level and in the case of 1.1
		default_vocab = InitialContext(self.state, inherited_state == None)
		
		# Set the default CURIE URI
		if inherited_state == None :
			# This is the top level...
			self.default_curie_uri = Namespace(XHTML_URI)
			# self.graph.bind(XHTML_PREFIX, self.default_curie_uri)
		else :
			self.default_curie_uri = inherited_state.term_or_curie.default_curie_uri
		
		# --------------------------------------------------------------------------------
		# Set the default term URI
		# This is a 1.1 feature, ie, should be ignored if the version is < 1.0
		if state.rdfa_version >= "1.1" :
			# that is the absolute default setup...
			if inherited_state == None :
				self.default_term_uri = None
			else :
				self.default_term_uri = inherited_state.term_or_curie.default_term_uri
				
			# see if the initial context has defined a default vocabulary:
			if default_vocab.vocabulary :
				self.default_term_uri = default_vocab.vocabulary
				
			# see if there is local vocab that would override previous settings
			# However, care should be taken with the vocab="" value that should not become a URI...
			# Indeed, this value is used to 'vipe out', ie, get back to the default vocabulary...
			if self.state.node.hasAttribute("vocab") and self.state.node.getAttribute("vocab") == "" :
				self.default_term_uri = default_vocab.vocabulary
			else :
				def_term_uri = self.state.getURI("vocab")
				if def_term_uri and def_term_uri != "" :			
					self.default_term_uri = def_term_uri
					self.graph.add((URIRef(self.state.base),RDFA_VOCAB,URIRef(def_term_uri)))
		else :
			self.default_term_uri = None
		
		# --------------------------------------------------------------------------------
		# The simpler case: terms, adding those that have been defined by a possible initial context
		if inherited_state is None :
			# this is the vocabulary belonging to the top level of the tree!
			self.terms = {}
			if state.rdfa_version >= "1.1" :
				# Simply get the terms defined by the default vocabularies. There is no need for merging
				for key in default_vocab.terms :
					self.terms[key] = default_vocab.terms[key]
			else :
				# The terms are hardwired...
				for key in predefined_1_0_rel :
					self.terms[key] = URIRef(XHTML_URI + key)
		else :
			# just refer to the inherited terms
			self.terms = inherited_state.term_or_curie.terms

		#-----------------------------------------------------------------
		# the locally defined namespaces
		dict = {}
		# locally defined xmlns namespaces, necessary for correct XML Literal generation
		xmlns_dict = {}

		# Add the locally defined namespaces using the xmlns: syntax
		for i in range(0, state.node.attributes.length) :
			attr = state.node.attributes.item(i)
			if attr.name.find('xmlns:') == 0 :	
				# yep, there is a namespace setting
				prefix = attr.localName
				if prefix != "" : # exclude the top level xmlns setting...
					if state.rdfa_version >= "1.1" and state.options.host_language in warn_xmlns_usage :
						state.options.add_warning(err_xmlns_deprecated % prefix, IncorrectPrefixDefinition, node=state.node.nodeName)
					if prefix == "_" :
						state.options.add_warning(err_bnode_local_prefix, IncorrectPrefixDefinition, node=state.node.nodeName)
					elif prefix.find(':') != -1 :
						state.options.add_warning(err_col_local_prefix % prefix, IncorrectPrefixDefinition, node=state.node.nodeName)
					else :					
						# quote the URI, ie, convert special characters into %.. This is
						# true, for example, for spaces
						uri = quote_URI(attr.value, state.options)
						# create a new RDFLib Namespace entry
						ns = Namespace(uri)
						# Add an entry to the dictionary if not already there (priority is left to right!)
						if state.rdfa_version >= "1.1" :
							pr = prefix.lower()
						else :
							pr = prefix
						dict[pr]       = ns
						xmlns_dict[pr] = ns
						self.graph.bind(pr,ns)
						check_prefix(pr)

		# Add the locally defined namespaces using the @prefix syntax
		# this may override the definition @xmlns
		if state.rdfa_version >= "1.1" and state.node.hasAttribute("prefix") :
			pr = state.node.getAttribute("prefix")
			if pr != None :
				# separator character is whitespace
				pr_list = pr.strip().split()
				# range(0, len(pr_list), 2) 
				for i in range(len(pr_list) - 2, -1, -2) :
					prefix = pr_list[i]
					# see if there is a URI at all
					if i == len(pr_list) - 1 :
						state.options.add_warning(err_missing_URI_prefix % (prefix,pr), node=state.node.nodeName)
						break
					else :
						value = pr_list[i+1]
					
					# see if the value of prefix is o.k., ie, there is a ':' at the end
					if prefix[-1] != ':' :
						state.options.add_warning(err_invalid_prefix % (prefix,pr), IncorrectPrefixDefinition, node=state.node.nodeName)
						continue
					elif prefix == ":" :
						state.options.add_warning(err_no_default_prefix % pr, IncorrectPrefixDefinition, node=state.node.nodeName)
						continue						
					else :
						prefix = prefix[:-1]
						uri    = Namespace(quote_URI(value, state.options))
						if prefix == "" :
							#something to be done here
							self.default_curie_uri = uri
						elif prefix == "_" :
							state.options.add_warning(err_bnode_local_prefix, IncorrectPrefixDefinition, node=state.node.nodeName)
						else :
							# last check: is the prefix an NCNAME?
							if ncname.match(prefix) :
								real_prefix = prefix.lower()
								dict[real_prefix] = uri
								self.graph.bind(real_prefix,uri)
								# Additional warning: is this prefix overriding an existing xmlns statement with a different URI? if
								# so, that may lead to discrepancies between an RDFa 1.0 and RDFa 1.1 run...
								if (prefix in xmlns_dict and xmlns_dict[prefix] != uri) or (real_prefix in xmlns_dict and xmlns_dict[real_prefix] != uri) :
									state.options.add_warning(err_prefix_and_xmlns % (real_prefix,real_prefix), node=state.node.nodeName)
								check_prefix(real_prefix)

							else :
								state.options.add_warning(err_non_ncname_prefix % (prefix,pr), IncorrectPrefixDefinition, node=state.node.nodeName)

		# See if anything has been collected at all.
		# If not, the namespaces of the incoming state is
		# taken over by reference. Otherwise that is copied to the
		# the local dictionary
		if inherited_state == None :
			self.default_prefixes = default_vocab.ns
			inherited_prefixes    = {}
		else :
			self.default_prefixes = inherited_state.term_or_curie.default_prefixes
			inherited_prefixes    = inherited_state.term_or_curie.ns

		if len(dict) == 0 :
			self.ns = inherited_prefixes
		else :
			self.ns = {}
			for key in inherited_prefixes : self.ns[key] = inherited_prefixes[key]
			for key in dict : 
				if (key in inherited_prefixes and dict[key] != inherited_prefixes[key]) or (key in self.default_prefixes and dict[key] != self.default_prefixes[key][0]) :
					state.options.add_warning(err_prefix_redefinition % key, PrefixRedefinitionWarning, node=state.node.nodeName)
				self.ns[key] = dict[key]

		
		# the xmlns prefixes have to be stored separately, again for XML Literal generation	
		self.xmlns = {}
		if len(xmlns_dict) == 0 and inherited_state :
			self.xmlns = inherited_state.term_or_curie.xmlns
		else :
			if inherited_state :
				for key in inherited_state.term_or_curie.xmlns	: self.xmlns[key] = inherited_state.term_or_curie.xmlns[key]
				for key in xmlns_dict							: self.xmlns[key] = xmlns_dict[key]
			else :
				self.xmlns = xmlns_dict
	# end __init__

	def _check_reference(self, val) :
		"""Checking the CURIE reference for correctness. It is probably not 100% foolproof, but may take care
		of some of the possible errors. See the URI RFC for the details.
		"""
		def char_check(s, not_allowed = ['#','[',']']) :
			for c in not_allowed :
				if s.find(c) != -1 : return False
			return True
		# Creating an artificial http URI to fool the urlparse module...
		scheme, netloc, url, query, fragment = urlsplit('http:' + val)
		if netloc != "" and self.state.rdfa_version >= "1.1" :
			self.state.options.add_warning(err_absolute_reference % (netloc, val), UnresolvableReference, node=self.state.node.nodeName)
			return False
		elif not char_check(query) :
			self.state.options.add_warning(err_query_reference % (query, val), UnresolvableReference, node=self.state.node.nodeName)
			return False
		elif not char_check(fragment) :
			self.state.options.add_warning(err_fragment_reference % (fragment, val), UnresolvableReference, node=self.state.node.nodeName)
			return False
		else :
			return True

	def CURIE_to_URI(self, val) :
		"""CURIE to URI mapping. 
		
		This method does I{not} take care of the last step of CURIE processing, ie, the fact that if
		it does not have a CURIE then the value is used a URI. This is done on the caller's side, because this has
		to be combined with base, for example. The method I{does} take care of BNode processing, though, ie,
		CURIE-s of the form "_:XXX".
		
		@param val: the full CURIE
		@type val: string
		@return: URIRef of a URI or None.
		"""
		# Just to be on the safe side:
		if val == "" :
			return None
		elif val == ":" :
			if self.default_curie_uri :
				return URIRef(self.default_curie_uri)
			else :
				return None
		
		# See if this is indeed a valid CURIE, ie, it can be split by a colon
		curie_split = val.split(':',1)
		if len(curie_split) == 1 :
			# there is no ':' character in the string, ie, it is not a valid CURIE
			return None
		else :
			if self.state.rdfa_version >= "1.1" :
				prefix	= curie_split[0].lower()
			else :
				prefix	= curie_split[0]
			reference = curie_split[1]

			#if len(reference) > 0 :
			#	if self.state.rdfa_version >= "1.1" and (len(prefix) == 0 or prefix in self.ns) and reference.startswith('//') :
			#		# This has been defined as illegal in RDFa 1.1
			#		self.state.options.add_warning(err_absolute_reference % (reference, val), UnresolvableReference, node=self.state.node.nodeName)
			#		return None
			#	if reference[0] == ":" :
			#		return None
			
			# first possibility: empty prefix
			if len(prefix) == 0 :
				if self.default_curie_uri and self._check_reference(reference) :
					return self.default_curie_uri[reference]
				else :
					return None
			else :
				# prefix is non-empty; can be a bnode
				if prefix == "_" :
					# yep, BNode processing. There is a difference whether the reference is empty or not...
					if len(reference) == 0 :
						return _empty_bnode
					else :
						# see if this variable has been used before for a BNode
						if reference in _bnodes :
							return _bnodes[reference]
						else :
							# a new bnode...
							retval = BNode()
							_bnodes[reference] = retval
							return retval
				# check if the prefix is a valid NCNAME
				elif ncname.match(prefix) :
					# see if there is a binding for this:					
					if prefix in self.ns and self._check_reference(reference) :
						# yep, a binding has been defined!
						if len(reference) == 0 :
							return URIRef(str(self.ns[prefix]))
						else :
							return self.ns[prefix][reference]
					elif prefix in self.default_prefixes and self._check_reference(reference) :
						# this has been defined through the default context
						if len(reference) == 0 :
							return URIRef(str(self.default_prefixes[prefix][0]))
						else :
							(ns,used) = self.default_prefixes[prefix]
							# lazy binding of prefixes (to avoid unnecessary prefix definitions in the serializations at the end...)
							if not used :
								self.graph.bind(prefix,ns)
								self.default_prefixes[prefix] = (ns,True)
							return ns[reference]
					else :
						# no definition for this thing...
						return None
				else :
					return None
	# end CURIE_to_URI

	def term_to_URI(self, term) :
		"""A term to URI mapping, where term is a simple string and the corresponding
		URI is defined via the @vocab (ie, default term uri) mechanism. Returns None if term is not defined
		@param term: string
		@return: an RDFLib URIRef instance (or None)
		"""
		if len(term) == 0 : return None

		if termname.match(term) :
			# It is a valid NCNAME
			
			# First of all, a @vocab nukes everything. That has to be done first...
			if self.default_term_uri != None :
				return URIRef(self.default_term_uri + term)

			# For default terms, the algorithm is (see 7.4.3 of the document): first make a case sensitive match;
			# if that fails than make a case insensive one			
			# 1. simple, case sensitive test:
			if term in self.terms :
				# yep, term is a valid key as is
				# lazy binding of the xhv prefix for terms...
				self.graph.bind(XHTML_PREFIX, XHTML_URI)
				return self.terms[term]
				
			# 2. case insensitive test
			for defined_term in self.terms :
				if term.lower() == defined_term.lower() :
					# lazy binding of the xhv prefix for terms...
					self.graph.bind(XHTML_PREFIX, XHTML_URI)
					return self.terms[defined_term]

		# If it got here, it is all wrong...
		return None
