# -*- coding: utf-8 -*-
"""
@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}

"""

"""
$Id: process.py,v 1.7 2012-03-23 14:06:38 ivan Exp $ $Date: 2012-03-23 14:06:38 $

"""

import sys
import os

import rdflib
from rdflib	import URIRef
from rdflib	import Literal
from rdflib	import BNode
from rdflib	import Namespace
if rdflib.__version__ >= "3.0.0" :
	from rdflib	import RDF  as ns_rdf
	from rdflib	import RDFS as ns_rdfs
	from rdflib	import Graph
else :
	from rdflib.RDFS	import RDFSNS as ns_rdfs
	from rdflib.RDF		import RDFNS  as ns_rdf
	from rdflib.Graph import Graph
	
ns_owl = Namespace("http://www.w3.org/2002/07/owl#")
	
from ..host import MediaTypes
	
from ..utils	import URIOpener

from . import err_outdated_cache
from . import err_unreachable_vocab
from . import err_unparsable_Turtle_vocab
from . import err_unparsable_xml_vocab
from . import err_unparsable_ntriples_vocab
from . import err_unparsable_rdfa_vocab
from . import err_unrecognised_vocab_type

from .. import VocabReferenceError

from .cache import CachedVocab
from .. import HTTPError, RDFaError

#############################################################################################################

def return_graph(uri, options, newCache = False) :
	"""Parse a file, and return an RDFLib Graph. The URI's content type is checked and either one of
	RDFLib's parsers is invoked (for the Turtle, RDF/XML, and N Triple cases) or a separate RDFa processing is invoked
	on the RDFa content.
			
	The Accept header of the HTTP request gives a preference to Turtle, followed by RDF/XML and then HTML (RDFa), in case content negotiation is used.
	
	This function is used to retreive the vocabulary file and turn it into an RDFLib graph.
	
	@param uri: URI for the graph
	@param options: used as a place where warnings can be sent
	@param newCache: in case this is used with caching, whether a new cache is generated; that modifies the warning text
	@return: A tuple consisting of an RDFLib Graph instance and an expiration date); None if the dereferencing or the parsing was unsuccessful
	"""
	def return_to_cache(msg) :
		if newCache :
			options.add_warning(err_unreachable_vocab % uri, warning_type=VocabReferenceError)
		else :
			options.add_warning(err_outdated_cache % uri, warning_type=VocabReferenceError)
	
	retval 			= None
	expiration_date = None
	content			= None
	
	try :
		content = URIOpener(uri,
							{'Accept' : 'text/html;q=0.8, application/xhtml+xml;q=0.8, text/turtle;q=1.0, application/rdf+xml;q=0.9'})
	except HTTPError :
		(type,value,traceback) = sys.exc_info()
		return_to_cache(value)
		return (None,None)
	except RDFaError :
		(type,value,traceback) = sys.exc_info()
		return_to_cache(value)
		return (None,None)
	except Exception :
		(type,value,traceback) = sys.exc_info()
		return_to_cache(value)
		return (None,None)
	
	# Store the expiration date of the newly accessed data
	expiration_date = content.expiration_date
					
	if content.content_type == MediaTypes.turtle :
		try :
			retval = Graph()
			retval.parse(content.data, format="n3")
		except :
			(type,value,traceback) = sys.exc_info()
			options.add_warning(err_unparsable_Turtle_vocab % (uri,value))
	elif content.content_type == MediaTypes.rdfxml :
		try :
			retval = Graph()
			retval.parse(content.data)
		except :
			(type,value,traceback) = sys.exc_info()
			options.add_warning(err_unparsable_Turtle_vocab % (uri,value))
	elif content.content_type == MediaTypes.nt :
		try :
			retval = Graph()
			retval.parse(content.data, format="nt")
		except :
			(type,value,traceback) = sys.exc_info()
			options.add_warning(err_unparsable_ntriples_vocab % (uri,value))
	elif content.content_type in [MediaTypes.xhtml, MediaTypes.html, MediaTypes.xml] or xml_application_media_type.match(content.content_type) != None :
		try :
			from pyRdfa import pyRdfa
			from pyRdfa.options	import Options
			options = Options()
			retval = pyRdfa(options).graph_from_source(content.data)
		except :
			(type,value,traceback) = sys.exc_info()
			options.add_warning(err_unparsable_rdfa_vocab % (uri,value))
	else :
		options.add_warning(err_unrecognised_vocab_type % (uri, content.content_type))
		
	return (retval, expiration_date)
	
############################################################################################
type 				= ns_rdf["type"]
Property 			= ns_rdf["Property"]
Class 				= ns_rdfs["Class"]
subClassOf			= ns_rdfs["subClassOf"]
subPropertyOf		= ns_rdfs["subPropertyOf"]
equivalentProperty	= ns_owl["equivalentProperty"]
equivalentClass 	= ns_owl["equivalentClass"]

class MiniOWL :
	"""
	Class implementing the simple OWL RL Reasoning required by RDFa in managing vocabulary files. This is done via
	a forward chaining process (in the L{closure} method) using a few simple rules as defined by the RDF and the OWL Semantics
	specifications.
	
	@ivar graph: the graph that has to be expanded
	@ivar added_triples: each cycle collects the triples that are to be added to the graph eventually.
	@type added_triples: a set, to ensure the unicity of triples being added
	"""
	def __init__(self, graph, schema_semantics = False) :
		self.graph         		= graph
		self.added_triples 		= None
		self.schema_semantics 	= schema_semantics

	def closure(self) :
		"""
		   Generate the closure the graph. This is the real 'core'.

		   The processing rules store new triples via the L{separate method<store_triple>} which stores
		   them in the L{added_triples<added_triples>} array. If that array is emtpy at the end of a cycle,
		   it means that the whole process can be stopped.
		"""

		# Go cyclically through all rules until no change happens
		new_cycle = True
		cycle_num = 0
		while new_cycle :
			# yes, there was a change, let us go again
			cycle_num += 1

			# go through all rules, and collect the replies (to see whether any change has been done)
			# the new triples to be added are collected separately not to interfere with
			# the current graph yet
			self.added_triples = set()

			# Execute all the rules; these might fill up the added triples array
			for t in self.graph : self.rules(t)

			# Add the tuples to the graph (if necessary, that is). If any new triple has been generated, a new cycle
			# will be necessary...
			new_cycle = len(self.added_triples) > 0

			for t in self.added_triples : self.graph.add(t)

	def store_triple(self, t) :
		"""
		In contrast to its name, this does not yet add anything to the graph itself, it just stores the tuple in an
		L{internal set<added_triples>}. (It is important for this to be a set: some of the rules in the various closures may
		generate the same tuples several times.) Before adding the tuple to the set, the method checks whether
		the tuple is in the final graph already (if yes, it is not added to the set).

		The set itself is emptied at the start of every processing cycle; the triples are then effectively added to the
		graph at the end of such a cycle. If the set is
		actually empty at that point, this means that the cycle has not added any new triple, and the full processing can stop.

		@param t: the triple to be added to the graph, unless it is already there
		@type t: a 3-element tuple of (s,p,o)
		"""
		(s,p,o) = t
		if t not in self.graph :
			self.added_triples.add(t)

	def rules(self, t) :
		"""
			Go through the OWL-RL entailement rules prp-spo1, prp-eqp1, prp-eqp2, cax-sco, cax-eqc1, and cax-eqc2 by extending the graph.
			@param t: a triple (in the form of a tuple)
		"""
		s,p,o = t
		if self.schema_semantics :
			# extra resonings on the vocabulary only to reduce the overall load by reducing the expected number of chaining cycles
			if p == subPropertyOf :
				for Z,Y,xxx in self.graph.triples((o, subPropertyOf, None)) :
					self.store_triple((s,subPropertyOf,xxx))  
			elif p == equivalentProperty :
				for Z,Y,xxx in self.graph.triples((o, equivalentProperty, None)) :
					self.store_triple((s,equivalentProperty,xxx))  
				for xxx,Y,Z in self.graph.triples((None, equivalentProperty, s)) :
					self.store_triple((xxx,equivalentProperty,o))  
			elif p == subClassOf :
				for Z,Y,xxx in self.graph.triples((o, subClassOf, None)) :
					self.store_triple((s,subClassOf,xxx))
			elif p == equivalentClass :
				for Z,Y,xxx in self.graph.triples((o, equivalentClass, None)) :
					self.store_triple((s,equivalentClass,xxx))  
				for xxx,Y,Z in self.graph.triples((None, equivalentClass, s)) :
					self.store_triple((xxx,equivalentClass,o))  
		else :
			if p == subPropertyOf :
				# prp-spo1
				for zzz,Z,www in self.graph.triples((None, s, None)) :
					self.store_triple((zzz, o, www))
			elif p == equivalentProperty :
				# prp-eqp1
				for zzz,Z,www in self.graph.triples((None, s, None)) :
					self.store_triple((zzz, o, www))
				# prp-eqp2
				for zzz,Z,www in self.graph.triples((None, o, None)) :
					self.store_triple((zzz, s, www))					
			elif p == subClassOf :
				# cax-sco
				for vvv,Y,Z in self.graph.triples((None, type, s)) :
					self.store_triple((vvv, type, o))
			elif p == equivalentClass :
				# cax-eqc1
				for vvv,Y,Z in self.graph.triples((None, type, s)) :
					self.store_triple((vvv, type, o))
				# cax-eqc2
				for vvv,Y,Z in self.graph.triples((None, type, o)) :
					self.store_triple((vvv, type, s))

########################################################################################################

def process_rdfa_sem(graph, options) :
	"""
	Expand the graph through the minimal RDFS and OWL rules defined for RDFa.
	
	The expansion is done in several steps:
	 1. the vocabularies are retrieved from the incoming graph (there are RDFa triples generated for that)
	 2. all vocabularies are merged into a separate vocabulary graph
	 3. the RDFS/OWL expansion is done on the vocabulary graph, to take care of all the subproperty, subclass, etc, chains
	 4. the (expanded) vocabulary graph content is added to the incoming graph
	 5. the incoming graph is expanded
	 6. the triples appearing in the vocabulary graph are removed from the incoming graph, to avoid unnecessary extra triples from the data
	 
	@param graph: an RDFLib Graph instance, to be expanded
	@param options: options as defined for the RDFa run; used to generate warnings
	@type options: L{pyRdfa.Options}
	"""
	# 1. collect the vocab URI-s
	vocabs = set()
	from pyRdfa import RDFA_VOCAB
	for ((s,p,v)) in graph.triples((None,RDFA_VOCAB,None)) :
		vocabs.add((str(v)))

	if len(vocabs) >= 0 :
		# 2. get all the vocab graphs
		vocab_graph = Graph()
		for uri in vocabs :
			if options.vocab_cache :
				v_graph = CachedVocab(uri, options).graph
			else :
				(v_graph, exp_date) = return_graph(uri, options)
			if v_graph != None :
				for t in v_graph :
					vocab_graph.add(t)
				
		# 3. Get the closure of the vocab graph; this will take care of local subproperty, etc, statements
		# Strictly speaking this is not necessary, but will speed up processing, because it may save chaining cycles on the
		# real graph
		MiniOWL(vocab_graph, schema_semantics = True).closure()
		
		# 4. Now get the vocab graph content added to the default graph
		for t in vocab_graph :
			graph.add(t)
						
		# 5. get the graph expanded through RDFS
		MiniOWL(graph).closure()
		
		# 4. clean up the graph by removing the schema triples
		for t in vocab_graph : graph.remove(t)
	
	# That was it...
	return graph

