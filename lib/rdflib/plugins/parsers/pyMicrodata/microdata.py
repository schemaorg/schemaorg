# -*- coding: utf-8 -*-
"""

The core of the Microdata->RDF conversion, a more or less verbatim implementation of the
U{W3C IG Note<http://www.w3.org/TR/microdata-rdf/>}. Because the implementation was also used to check
the note itself, it tries to be fairly close to the text.


@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
"""

"""
$Id: microdata.py,v 1.4 2012/09/05 16:40:43 ivan Exp $
$Date: 2012/09/05 16:40:43 $

Added a reaction on the RDFaStopParsing exception: if raised while setting up the local execution context, parsing
is stopped (on the whole subtree)
"""

import sys
if sys.version_info[0] >= 3 :
	from urllib.parse import urlsplit, urlunsplit
else :	
	from urlparse import urlsplit, urlunsplit

from types import *

import rdflib
from rdflib	import URIRef
from rdflib	import Literal
from rdflib	import BNode
from rdflib	import Namespace
if rdflib.__version__ >= "3.0.0" :
	from rdflib	import Graph
	from rdflib	import RDF  as ns_rdf
	from rdflib	import RDFS as ns_rdfs
	from rdflib import XSD  as ns_xsd
else :
	from rdflib.Graph	import Graph
	from rdflib.RDFS	import RDFSNS  as ns_rdfs
	from rdflib.Literal import _XSD_NS as ns_xsd
	from rdflib.RDF		import RDFNS   as ns_rdf
	
ns_owl = Namespace("http://www.w3.org/2002/07/owl#")

from .registry import registry, vocab_names
from .utils	   import generate_RDF_collection, get_Literal, get_time_type
from .utils	   import get_lang_from_hierarchy, is_absolute_URI, generate_URI, fragment_escape

MD_VOCAB   = "http://www.w3.org/ns/md#"
RDFA_VOCAB = URIRef("http://www.w3.org/ns/rdfa#usesVocabulary")

from . import debug

# Existing predicate schemes
class PropertySchemes :
	vocabulary = "vocabulary"
	contextual = "contextual"
	
class ValueMethod :
	unordered = "unordered"
	list      = "list"

# ----------------------------------------------------------------------------

class Evaluation_Context :
	"""
	Evaluation context structure. See Section 4.1 of the U{W3C IG Note<http://www.w3.org/TR/microdata-rdf/>}for the details.
	
	@ivar current_type : an absolute URL for the current type, used when an item does not contain an item type
	@ivar memory: mapping from items to RDF subjects
	@type memory: dictionary
	@ivar current_name: an absolute URL for the in-scope name, used for generating URIs for properties of items without an item type
	@ivar current_vocabulary: an absolute URL for the current vocabulary, from the registry
	"""
	def __init__( self ) :
		self.current_type       = None
		self.memory             = {}
		self.current_name       = None
		self.current_vocabulary = None
		
	def get_memory( self, item ) :
		"""
		Get the memory content (ie, RDF subject) for 'item', or None if not stored yet
		@param item: an 'item', in microdata terminology
		@type item: DOM Element Node
		@return: None, or an RDF Subject (URIRef or BNode)
		"""
		if item in self.memory :
			return self.memory[item]
		else :
			return None
		
	def set_memory( self, item, subject ) :
		"""
		Set the memory content, ie, the subject, for 'item'.
		@param item: an 'item', in microdata terminology
		@type item: DOM Element Node
		@param subject: RDF Subject
		@type subject: URIRef or Blank Node
		"""
		self.memory[item] = subject
		
	def new_copy(self, itype) :
		"""
		During the generation algorithm a new copy of the current context has to be done with a new current type.
		
		At the moment, the content of memory is copied, ie, a fresh dictionary is created and the content copied over.
		Not clear whether that is necessary, though, maybe a simple reference is enough...
		@param itype : an absolute URL for the current type
		@return: a new evaluation context instance
		"""
		retval = Evaluation_Context()
		for k in self.memory :
			retval.memory[k] = self.memory[k]

		retval.current_type       = itype		
		retval.current_name       = self.current_name
		retval.current_vocabulary = self.current_vocabulary
		return retval
	
	def __str__(self) :
		retval = "Evaluation context:\n"
		retval += "  current type:       %s\n" % self.current_type
		retval += "  current name:       %s\n" % self.current_name
		retval += "  current vocabulary: %s\n" % self.current_vocabulary
		retval += "  memory:             %s\n" % self.memory
		retval += "----\n"
		return retval
		
class Microdata :
	"""
	This class encapsulates methods that are defined by the U{microdata spec<http://dev.w3.org/html5/md/Overview.html>},
	as opposed to the RDF conversion note.
	
	@ivar document: top of the DOM tree, as returned by the HTML5 parser
	@ivar base: the base URI of the Dom tree, either set from the outside or via a @base element
	"""
	def __init__( self, document, base = None) :
		"""
		@param document: top of the DOM tree, as returned by the HTML5 parser
		@param base: the base URI of the Dom tree, either set from the outside or via a @base element
		"""
		self.document = document
		
		#-----------------------------------------------------------------
		# set the document base, will be used to generate top level URIs
		self.base = None
		# handle the base element case for HTML
		for set_base in document.getElementsByTagName("base") :
			if set_base.hasAttribute("href") :
				# Yep, there is a local setting for base
				self.base = set_base.getAttribute("href")
				return
		# If got here, ie, if no local setting for base occurs, the input argument has it
		self.base = base	

	def get_top_level_items( self ) :
		"""
		A top level item is and element that has the @itemscope set, but no @itemtype. They have to
		be collected in pre-order and depth-first fashion.
		
		@return: list of items (ie, DOM Nodes)
		"""
		def collect_items( node ) :
			items = []
			for child in node.childNodes :
				if child.nodeType == node.ELEMENT_NODE :
					items += collect_items( child )
					
			if node.hasAttribute("itemscope") and not node.hasAttribute("itemprop") :
				# This is also a top level item
				items.append(node)
			
			return items
				
		return collect_items( self.document )
		
	def get_item_properties( self, item ) :
		"""
		Collect the item's properties, ie, all DOM descendent nodes with @itemprop until the subtree hits another
		@itemscope. @itemrefs are also added at this point.
		
		@param item: current item
		@type item: DOM Node
		@return: array of items, ie, DOM Nodes
		"""
		# go down the tree until another itemprop is hit, take care of the itemrefs, too; see the microdata doc
		# probably the ugliest stuff
		# returns a series of element nodes.
		# Is it worth filtering the ones with itemprop at that level???
		results = []
		memory  = [ item ]		
		pending = [ child for child in item.childNodes if child.nodeType == item.ELEMENT_NODE ]
		
		if item.hasAttribute("itemref") :
			for id in item.getAttribute("itemref").strip().split() :
				obj = self.getElementById(id)
				if obj != None : pending.append(obj)
		
		while len(pending) > 0 :
			current = pending.pop(0)
			if current in memory :
				# in general this raises an error; the same item cannot be there twice. In this case this is
				# simply ignored
				continue
			else :
				# this for the check above
				memory.append(current)
			
			# @itemscope is the barrier...
			if not current.hasAttribute("itemscope") :
				pending = [ child for child in current.childNodes if child.nodeType == child.ELEMENT_NODE ] + pending

			if current.hasAttribute("itemprop") and current.getAttribute("itemprop").strip() != "" :
				results.append(current)
				
		return results
	
	def getElementById(self, id) :
		"""This is a method defined for DOM 2 HTML, but the HTML5 parser does not seem to define it. Oh well...
		@param id: value of an @id attribute to look for
		@return: array of nodes whose @id attribute matches C{id} (formally, there should be only one...)
		"""
		def collect_ids( node ) :
			ids = []
			for child in node.childNodes :
				if child.nodeType == node.ELEMENT_NODE :
					ids += collect_ids( child )
					
			if node.hasAttribute("id") and node.getAttribute("id") == id :
				# This is also a top level item
				ids.append(node)
			
			return ids
		
		ids = collect_ids(self.document)
		if len(ids) > 0 :
			return ids[0]
		else :
			return None
				
class MicrodataConversion(Microdata) :
	"""
	Top level class encapsulating the conversion algorithms as described in the W3C note.
	
	@ivar graph: an RDF graph; an RDFLib Graph
	@type graph: RDFLib Graph
	@ivar document: top of the DOM tree, as returned by the HTML5 parser
	@ivar ns_md: the Namespace for the microdata vocabulary
	@ivar base: the base of the Dom tree, either set from the outside or via a @base element
	"""
	def __init__( self, document, graph, base = None, vocab_expansion = False, vocab_cache = True  ) :
		"""
		@param graph: an RDF graph; an RDFLib Graph
		@type graph: RDFLib Graph
		@param document: top of the DOM tree, as returned by the HTML5 parser
		@keyword base: the base of the Dom tree, either set from the outside or via a @base element
		@keyword vocab_expansion: whether vocab expansion should be performed or not
		@type vocab_expansion: Boolean
		@keyword vocab_cache: if vocabulary expansion is done, then perform caching of the vocabulary data
		@type vocab_cache: Boolean
		"""
		Microdata.__init__(self, document, base)
		self.vocab_expansion   = vocab_expansion
		self.vocab_cache       = vocab_cache
		self.graph             = graph
		self.ns_md             = Namespace( MD_VOCAB )
		self.graph.bind( "md",MD_VOCAB )
		self.vocabularies_used = False

		# Get the vocabularies defined in the registry bound to proper names, if any...

		def _use_rdfa_context () :
			try :
				from ..pyRdfa.initialcontext import initial_context
			except :
				from pyRdfa.initialcontext import initial_context
			retval = {}
			vocabs = initial_context["http://www.w3.org/2011/rdfa-context/rdfa-1.1"].ns
			for prefix in list(vocabs.keys()) :
				uri = vocabs[prefix]				
				if uri not in vocab_names and uri not in registry : retval[uri] = prefix
			return retval
				
		for vocab in registry :
			if vocab in vocab_names :
				self.graph.bind( vocab_names[vocab],vocab )
			else :
				hvocab = vocab + '#'
				if hvocab in vocab_names :
					self.graph.bind( vocab_names[hvocab],hvocab )
					
		# Add the prefixes defined in the RDFa initial context to improve the outlook of the output
		# I put this into a try: except: in case the pyRdfa package is not available...
		try :
			try :
				from ..pyRdfa.initialcontext import initial_context
			except :
				from pyRdfa.initialcontext import initial_context
			vocabs = initial_context["http://www.w3.org/2011/rdfa-context/rdfa-1.1"].ns
			for prefix in list(vocabs.keys()) :
				uri = vocabs[prefix]
				if uri not in registry :
					# if it is in the registry, then it may have needed some special microdata massage...
					self.graph.bind( prefix,uri )
		except :
			pass
		
	def convert( self ) :
		"""
		Top level entry to convert and generate all the triples. It finds the top level items,
		and generates triples for each of them; additionally, it generates a top level entry point
		to the items from base in the form of an RDF list.
		"""
		item_list = []
		for top_level_item in self.get_top_level_items() :
			item_list.append( self.generate_triples(top_level_item, Evaluation_Context()) )
		list = generate_RDF_collection( self.graph, item_list )
		self.graph.add( (URIRef(self.base),self.ns_md["item"],list) )
		
		# If the vocab expansion is also switched on, this is the time to do it.

		# This is the version with my current proposal: the basic expansion is always there;
		# the follow-your-nose inclusion of vocabulary is optional
		if self.vocabularies_used :
			try :
				try :
					from ..pyRdfa.rdfs.process import MiniOWL, process_rdfa_sem
					from ..pyRdfa.options      import Options
				except :
					from pyRdfa.rdfs.process import MiniOWL, process_rdfa_sem
					from pyRdfa.options      import Options
				# if we did not get here, the pyRdfa package could not be
				# imported. Too bad, but life should go on in the except branch...
				if self.vocab_expansion :
					# This is the full deal
					options = Options(vocab_expansion = self.vocab_expansion, vocab_cache = self.vocab_cache)
					process_rdfa_sem(self.graph, options)
				else :
					MiniOWL(self.graph).closure()
			except :
				pass

	def generate_triples( self, item, context ) :
		"""
		Generate the triples for a specific item. See the W3C Note for the details.
		
		@param item: the DOM Node for the specific item
		@type item: DOM Node
		@param context: an instance of an evaluation context
		@type context: L{Evaluation_Context}
		@return: a URIRef or a BNode for the (RDF) subject
		"""
		# Step 1,2: if the subject has to be set, store it in memory
		subject = context.get_memory( item )
		if subject == None :
			# nop, there is no subject set. If there is a valid @itemid, that carries it
			if item.hasAttribute("itemid") and is_absolute_URI( item.getAttribute("itemid") ):
				subject = URIRef( item.getAttribute("itemid").strip() )
			else :
				subject = BNode()
			context.set_memory( item, subject )
			
		# Step 3: set the type triples if any
		types = []
		if item.hasAttribute("itemtype") :
			types = item.getAttribute("itemtype").strip().split()
			for t in types :
				if is_absolute_URI( t ) :
					self.graph.add( (subject, ns_rdf["type"], URIRef(t)) )
		
		# Step 4, 5 and 6 to set the typing variable
		if len(types) == 0 :
			itype = None
		else :
			if is_absolute_URI(types[0]) :
				itype = types[0]
				context.current_name = None
			elif context.current_type != None :
				itype = context.current_type
			else :
				itype = None

		# Step 7, 8, 9: Check the registry for possible keys and set the vocab
		vocab = None
		if itype != None :
			for key in list(registry.keys()) :
				if itype.startswith(key) :
					# There is a predefined vocabulary for this type...
					vocab = key
					# Step 7: Issue an rdfa usesVocabulary triple
					self.graph.add( (URIRef(self.base), RDFA_VOCAB, URIRef(vocab)))
					self.vocabularies_used = True
					break
			# The registry has not set the vocabulary; has to be extracted from the type
			if vocab == None :
				parsed = urlsplit(itype)
				if parsed.fragment != "" :
					vocab = urlunsplit( (parsed.scheme,parsed.netloc,parsed.path,parsed.query,"") ) + '#'					
				elif parsed.path == "" and parsed.query == "" :
					vocab = itype
					if vocab[-1] != '/' : vocab += '/'
				else :
					vocab = itype.rsplit('/',1)[0] + '/'
		
		# Step 9: update vocab in the context
		if vocab != None :
			context.current_vocabulary = vocab
		elif item.hasAttribute("itemtype") :
			context.current_vocabulary = None

		# Step 10: set up a property list; this will be used to generate triples later.
		# each entry in the dictionary is an array of RDF objects
		property_list = {}
		
		# Step 11: Get the item properties and run a cycle on those
		for prop in self.get_item_properties(item) :
			for name in prop.getAttribute("itemprop").strip().split() :
				# 11.1.1. set a new context
				new_context = context.new_copy(itype)
				# 11.1.2, generate the URI for the property name, that will be the predicate
				# Also update the context
				new_context.current_name = predicate = self.generate_predicate_URI( name,new_context )
				# 11.1.3, generate the property value. The extra flag signals that the value is a new item
				# Note that 10.1.4 step is done in the method itself, ie, a recursion may occur there
				# if a new item is hit (in which case the return value is a RDF resource chaining to a subject)
				value  = self.get_property_value( prop, new_context )
				# 11.1.5, store all the values
				if predicate in property_list :
					property_list[predicate].append(value)
				else :
					property_list[predicate] = [ value ]
						
		# step 12: generate the triples
		for property in list(property_list.keys()) :
			self.generate_property_values( subject, URIRef(property), property_list[property], context )
			
		# Step 13: return the subject to the caller
		return subject
		
	def generate_predicate_URI( self, name, context ) :
		"""
		Generate a full URI for a predicate, using the type, the vocabulary, etc.
		
		For details of this entry, see Section 4.4
		@param name: name of the property, ie, what appears in @itemprop
		@param context: an instance of an evaluation context
		@type context: L{Evaluation_Context}
		"""
		if debug: print( "name: %s, %s" % (name,context) )
		
		# Step 1: absolute URI-s are fine, take them as they are
		if is_absolute_URI(name) : return name
		
		# Step 2: if type is none, that this is just used as a fragment
		# if not context.current_type  :
		if context.current_type == None and context.current_vocabulary == None  :
			if self.base[-1] == '#' :
				b = self.base[:-1]
			else :
				b = self.base
			return b + '#' + fragment_escape(name)

		#if context.current_type == None :
		#	return generate_URI( self.base, name )
		
		# Step 3: set the scheme
		try :
			if context.current_vocabulary in registry and "propertyURI" in registry[context.current_vocabulary] :
				scheme = registry[context.current_vocabulary]["propertyURI"]
			else :
				scheme = PropertySchemes.vocabulary
		except :
			# This is when the structure of the registry is broken
			scheme = PropertySchemes.vocabulary
			
		name = fragment_escape( name )
		if scheme == PropertySchemes.contextual :
			# Step 5.1
			s = context.current_name
			# s = context.current_type
			if s != None and s.startswith("http://www.w3.org/ns/md?type=") :
				# Step 5.2
				expandedURI = s + '.' + name
			else :
				# Step 5.3
				expandedURI =  "http://www.w3.org/ns/md?type=" + fragment_escape(context.current_type) + "&prop=" + name
		else :
			# Step 4
			if context.current_vocabulary[-1] == '#' or context.current_vocabulary[-1] == '/' :
				expandedURI =  context.current_vocabulary + name
			else :
				expandedURI =  context.current_vocabulary + '#' + name

		# see if there are subproperty/equivalentproperty relations
		try :
			vocab_mapping = registry[context.current_vocabulary]["properties"][name]
			# if we got that far, we may have some mappings

			expandedURIRef = URIRef(expandedURI)
			try :
				subpr = vocab_mapping["subPropertyOf"]
				if subpr != None :
					if isinstance(subpr,list) :
						for p in subpr :
							self.graph.add( (expandedURIRef, ns_rdfs["subPropertyOf"], URIRef(p)) )
					else :
						self.graph.add( (expandedURIRef, ns_rdfs["subPropertyOf"], URIRef(subpr)) )
			except :
				# Ok, no sub property
				pass
			try :
				subpr = vocab_mapping["equivalentProperty"]
				if subpr != None :
					if isinstance(subpr,list) :
						for p in subpr :
							self.graph.add( (expandedURIRef, ns_owl["equivalentProperty"], URIRef(p)) )
					else :
						self.graph.add( (expandedURIRef, ns_owl["equivalentProperty"], URIRef(subpr)) )
			except :
				# Ok, no sub property
				pass
		except :
			# no harm done, no extra vocabulary term
			pass


		return expandedURI
		
	def get_property_value(self, node, context) :
		"""
		Generate an RDF object, ie, the value of a property. Note that if this element contains
		an @itemscope, then a recursive call to L{MicrodataConversion.generate_triples} is done and the
		return value of that method (ie, the subject for the corresponding item) is return as an
		object.
		
		Otherwise, either URIRefs are created for <a>, <img>, etc, elements, or a Literal; the latter
		gets a time-related type for the <time> element.
		
		@param node: the DOM Node for which the property values should be generated
		@type node: DOM Node
		@param context: an instance of an evaluation context
		@type context: L{Evaluation_Context}
		@return: an RDF resource (URIRef, BNode, or Literal)
		"""
		URI_attrs = {
			"audio"		: "src",
			"embed"		: "src",
			"iframe"	: "src",
			"img"		: "src",
			"source"	: "src",
			"track"		: "src",
			"video"		: "src",
			"data"		: "src",
			"a"			: "href",
			"area"		: "href",
			"link"		: "href", 
			"object"	: "data" 
		}
		lang = get_lang_from_hierarchy( self.document, node )

		if node.hasAttribute("itemscope") :
			# THIS IS A RECURSION ENTRY POINT!
			return self.generate_triples( node, context )
			
		elif node.tagName in URI_attrs and node.hasAttribute(URI_attrs[node.tagName]) :
			return URIRef( generate_URI( self.base, node.getAttribute(URI_attrs[node.tagName]).strip() ) )
			
		elif node.tagName == "meta" and node.hasAttribute("content") :
			if lang :
				return Literal( node.getAttribute("content"), lang = lang )
			else :
				return Literal( node.getAttribute("content") )

		elif node.tagName == "meter" or node.tagName == "data" :
			if node.hasAttribute("value") :
				val  = node.getAttribute("value")
				# check whether the attribute value can be defined as a float or an integer
				try :
					fval = int(val)
					dt   = ns_xsd["integer"]
				except :
					# Well, not an int, try then a integer
					try :
						fval = float(val)
						dt   = ns_xsd["float"]
					except :
						# Sigh, this is not a valid value, but let it go through as a plain literal nevertheless
						fval = val
						dt   = None
				if dt :
					return Literal( val, datatype = dt)
				else :
					return Literal( val )
			else :
				return Literal( "" )

		elif node.tagName == "time" and node.hasAttribute("datetime") :
			litval = node.getAttribute("datetime")
			dtype  = get_time_type(litval)
			if dtype :
				return Literal( litval, datatype = dtype )
			else :
				return Literal( litval )

		else :
			if lang :
				return Literal( get_Literal(node), lang = lang )
			else :
				return Literal( get_Literal(node) )
		
	def generate_property_values( self, subject, predicate, objects, context) :
		"""
		Generate the property values for a specific subject and predicate. The context should specify whether
		the objects should be added in an RDF list or each triples individually.
		
		@param subject: RDF subject
		@type subject: RDFLib Node (URIRef or blank node)
		@param predicate: RDF predicate
		@type predicate: RDFLib URIRef
		@param objects: RDF objects
		@type objects: list of RDFLib nodes (URIRefs, Blank Nodes, or literals)
		@param context: evaluation context
		@type context: L{Evaluation_Context}
		"""
		# generate triples with a list, or a bunch of triples, depending on the context
		# The biggest complication is to find the method...
		method = ValueMethod.unordered
		superproperties = None
		
		# This is necessary because predicate is a URIRef, and I am not sure the comparisons would work well
		# to be tested, in fact...
		pred_key = "%s" % predicate
		for key in registry :
			if predicate.startswith(key) :
				# This the part of the registry corresponding to the predicate's vocabulary
				registry_object = registry[key]
				try :
					if "multipleValues" in registry_object : method = registry_object["multipleValues"]
					# The generic definition can be overwritten for a specific property. The simplest is to rely on a 'try'
					# with the right structure...
					try :
						method = registry_object["properties"][pred_key[len(key):]]["multipleValues"]
					except :
						pass
				except :
					pass
		
		if method == ValueMethod.unordered :
			for object in objects :
				self.graph.add( (subject, predicate, object) )
		else :
			self.graph.add( (subject,predicate,generate_RDF_collection( self.graph, objects )) )
		
						
				
					
		

