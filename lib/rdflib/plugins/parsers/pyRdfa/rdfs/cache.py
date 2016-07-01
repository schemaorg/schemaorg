# -*- coding: utf-8 -*-
"""
Managing Vocab Caching.

@summary: RDFa parser (distiller)
@requires: U{RDFLib<http://rdflib.net>}
@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
"""
import os, sys, datetime, re

PY3 = (sys.version_info[0] >= 3)

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
	from rdflib.Graph 	import Graph

from ..			import HTTPError, RDFaError
from ..host 	import MediaTypes, HostLanguage
from ..utils	import create_file_name, URIOpener, quote_URI
from ..options	import Options
from ..			import ns_rdfa

from . import err_outdated_cache
from . import err_unreachable_vocab
from . import err_unparsable_Turtle_vocab
from . import err_unparsable_xml_vocab
from . import err_unparsable_ntriples_vocab
from . import err_unparsable_rdfa_vocab
from . import err_unrecognised_vocab_type

from . import VocabCachingInfo

# Regular expression object for a general XML application media type
xml_application_media_type = re.compile("application/[a-zA-Z0-9]+\+xml")

from ..utils import URIOpener

#===========================================================================================
if PY3 :
	import pickle
else :
	import cPickle as pickle

# Protocol to be used for pickle files. 0 is good for debug, it stores the data in ASCII; 1 is better for deployment,
# it stores data in binary format. Care should be taken for consistency; when changing from 0 to 1 or back, all
# cached data should be removed/regenerated, otherwise mess may occur...
_Pickle_Protocol = 1

# If I could rely on python 2.5 or 2.6 (or higher) I could use the with...as... idiom for what is below, it
# is indeed nicer. But I cannot...
def _load(fname) :
	"""
	Load a cached file and return the resulting object
	@param fname: file name
	"""
	try :
		f = open(fname)
		return pickle.load(f)
	finally :
		f.close()
	
def _dump(obj, fname) :
	"""
	Dump an object into cached file
	@param obj: Python object to store
	@param fname: file name
	"""
	try :
		f = open(fname, "w")
		pickle.dump(obj, f, _Pickle_Protocol)
		f.flush()
	finally :
		f.close()

#===========================================================================================
class CachedVocabIndex :
	"""
	Class to manage the cache index. Takes care of finding the vocab directory, and manages the index
	to the individual vocab data.
	
	The vocab directory is set to a platform specific area, unless an environment variable
	sets it explicitly. The environment variable is "PyRdfaCacheDir"
	
	Every time the index is changed, the index is put back (via pickle) to the directory.
	
	@ivar app_data_dir: directory for the vocabulary cache directory
	@ivar index_fname: the full path of the index file on the disc
	@ivar indeces: the in-memory version of the index (a directory mapping URI-s to tuples)
	@ivar options: the error handler (option) object to send warnings to
	@type options: L{options.Options}
	@ivar report: whether details on the caching should be reported
	@type report: Boolean
	@cvar vocabs: File name used for the index in the cache directory
	@cvar preference_path: Cache directories for the three major platforms (ie, mac, windows, unix)
	@type preference_path: directory, keyed by "mac", "win", and "unix"
	@cvar architectures: Various 'architectures' as returned by the python call, and their mapping on one of the major platforms. If an architecture is missing, it is considered to be "unix"
	@type architectures: directory, mapping architectures to "mac", "win", or "unix"
	"""
	# File Name used for the index in the cache directory
	vocabs = "cache_index"
	# Cache directories for the three major platforms...
	preference_path = {
		"mac"	: "Library/Application Support/pyRdfa-cache",
		"win"	: "pyRdfa-cache",
		"unix"	: ".pyRdfa-cache"
	}
	# various architectures as returned by the python call, and their mapping on platorm. If an architecture is not here, it is considered as unix
	architectures = {
		"darwin"	: "mac",
		"nt" 		: "win",
		"win32"		: "win",
		"cygwin"	: "win"
	}
	def __init__(self, options = None) :
		"""
		@param options: the error handler (option) object to send warnings to
		@type options: L{options.Options}
		"""
		self.options = options
		self.report  = (options != None) and options.vocab_cache_report
		
		# This is where the cache files should be
		self.app_data_dir	= self._give_preference_path()
		self.index_fname	= os.path.join(self.app_data_dir, self.vocabs)
		self.indeces 		= {}
		
		# Check whether that directory exists.
		if not os.path.isdir(self.app_data_dir) :
			try :
				os.mkdir(self.app_data_dir)
			except Exception :
				(type,value,traceback) = sys.exc_info()
				if self.report: options.add_info("Could not create the vocab cache area %s" % value, VocabCachingInfo)
				return
		else :
			# check whether it is at least readable
			if not os.access(self.app_data_dir, os.R_OK) :
				if self.report: options.add_info("Vocab cache directory is not readable", VocabCachingInfo)
				return
			if not os.access(self.app_data_dir, os.W_OK) :
				if self.report: options.add_info("Vocab cache directory is not writeable, but readable", VocabCachingInfo)
				return

		if os.path.exists(self.index_fname) :
			if os.access(self.index_fname, os.R_OK) :
				self.indeces = _load(self.index_fname)
			else :
				if self.report: options.add_info("Vocab cache index not readable", VocabCachingInfo)				
		else :
			# This is the very initial phase, creation
			# of a a new index
			if os.access(self.app_data_dir, os.W_OK) :
				# This is then put into a pickle file to put the stake in the ground...
				try :
					_dump(self.indeces, self.index_fname)
				except Exception :
					(type,value,traceback) = sys.exc_info()
					if self.report: options.add_info("Could not create the vocabulary index %s" % value, VocabCachingInfo)
			else :
				if self.report: options.add_info("Vocabulary cache directory is not writeable", VocabCachingInfo)				
				self.cache_writeable	= False	
				
	def add_ref(self, uri, vocab_reference) :
		"""
		Add a new entry to the index, possibly removing the previous one.
		
		@param uri: the URI that serves as a key in the index directory
		@param vocab_reference: tuple consisting of file name, modification date, and expiration date
		"""
		# Store the index right away
		self.indeces[uri] = vocab_reference		
		try :
			_dump(self.indeces, self.index_fname)
		except Exception :
			(type,value,traceback) = sys.exc_info()
			if self.report: self.options.add_info("Could not store the cache index %s" % value, VocabCachingInfo)
			
	def get_ref(self, uri) :
		"""
		Get an index entry, if available, None otherwise.
		The return value is a tuple: file name, modification date, and expiration date
		
		@param uri: the URI that serves as a key in the index directory		
		"""
		if uri in self.indeces :
			return tuple(self.indeces[uri])
		else :
			return None

	def _give_preference_path(self) :
		"""
		Find the vocab cache directory.
		"""
		from pyRdfa	import CACHE_DIR_VAR
		if CACHE_DIR_VAR in os.environ :
			return os.environ[CACHE_DIR_VAR]
		else :
			# find the preference path on the architecture
			platform = sys.platform
			if platform in self.architectures :
				system = self.architectures[platform]
			else :
				system = "unix"
	
			if system == "win" :
				# there is a user variable set for that purpose
				app_data = os.path.expandvars("%APPDATA%")
				return os.path.join(app_data,self.preference_path[system])
			else :
				return os.path.join(os.path.expanduser('~'),self.preference_path[system])

#===========================================================================================
class CachedVocab(CachedVocabIndex) :
	"""
	Cache for a specific vocab. The content of the cache is the graph. These are also the data that are stored
	on the disc (in pickled form)
	
	@ivar graph: the RDF graph
	@ivar URI: vocabulary URI
	@ivar filename: file name (not the complete path) of the cached version
	@ivar creation_date: creation date of the cache
	@type creation_date: datetime
	@ivar expiration_date: expiration date of the cache
	@type expiration_date: datetime
	@cvar runtime_cache : a run time cache for already 'seen' vocabulary files. Apart from (marginally) speeding up processing, this also prevents recursion
	@type runtime_cache : dictionary
	"""
	def __init__(self, URI, options = None) :
		"""
		@param URI: real URI for the vocabulary file
		@param options: the error handler (option) object to send warnings to
		@type options: L{options.Options}
		"""
		# First see if this particular vocab has been handled before. If yes, it is extracted and everything
		# else can be forgotten. 
		self.uri													= URI
		(self.filename, self.creation_date, self.expiration_date)	= ("",None,None)
		self.graph													= Graph()

		try :
			CachedVocabIndex.__init__(self, options)
			vocab_reference 	= self.get_ref(URI)
			self.caching 		= True
		except Exception :
			# what this means is that the caching becomes impossible through some system error...
			(type,value,traceback) = sys.exc_info()
			if self.report: options.add_info("Could not access the vocabulary cache area %s" % value, VocabCachingInfo, URI)
			vocab_reference		= None
			self.caching		= False

		if vocab_reference == None :
			# This has never been cached before
			if self.report: options.add_info("No cache exists for %s, generating one" % URI, VocabCachingInfo)
			
			# Store all the cache data unless caching proves to be impossible
			if self._get_vocab_data(newCache = True) and self.caching :
				self.filename = create_file_name(self.uri)
				self._store_caches()
				if self.report:
					options.add_info("Generated a cache for %s, with an expiration date of %s" % (URI,self.expiration_date), VocabCachingInfo, URI)
		else :
			(self.filename, self.creation_date, self.expiration_date) = vocab_reference
			if self.report: options.add_info("Found a cache for %s, expiring on %s" % (URI,self.expiration_date), VocabCachingInfo)
			# Check if the expiration date is still away
			if options.refresh_vocab_cache == False and datetime.datetime.utcnow() <= self.expiration_date :
				# We are fine, we can just extract the data from the cache and we're done
				if self.report: options.add_info("Cache for %s is still valid; extracting the data" % URI, VocabCachingInfo)
				fname = os.path.join(self.app_data_dir, self.filename)
				try :
					self.graph = _load(fname)
				except Exception :
					# what this means is that the caching becomes impossible VocabCachingInfo
					(type,value,traceback) = sys.exc_info()
					sys.excepthook(type,value,traceback)
					if self.report: options.add_info("Could not access the vocab cache %s (%s)" % (value,fname), VocabCachingInfo, URI)
			else :
				if self.report :
					if options.refresh_vocab_cache == True :
						options.add_info("Time check is bypassed; refreshing the cache for %s" % URI, VocabCachingInfo)
					else :
						options.add_info("Cache timeout; refreshing the cache for %s" % URI, VocabCachingInfo)
				# we have to refresh the graph
				if self._get_vocab_data(newCache = False) == False :
					# bugger; the cache could not be refreshed, using the current one, and setting the cache artificially
					# to be valid for the coming hour, hoping that the access issues will be resolved by then...
					if self.report:
						options.add_info("Could not refresh vocabulary cache for %s, using the old cache, extended its expiration time by an hour (network problems?)" % URI, VocabCachingInfo, URI)
					fname = os.path.join(self.app_data_dir, self.filename)
					try :
						self.graph = _load(fname)
						self.expiration_date = datetime.datetime.utcnow() + datetime.timedelta(hours=1)
					except Exception :
						# what this means is that the caching becomes impossible VocabCachingInfo
						(type,value,traceback) = sys.exc_info()
						sys.excepthook(type,value,traceback)
						if self.report: options.add_info("Could not access the vocabulary cache %s (%s)" % (value,fname), VocabCachingInfo, URI)
				self.creation_date = datetime.datetime.utcnow()
				if self.report:
					options.add_info("Generated a new cache for %s, with an expiration date of %s" % (URI,self.expiration_date), VocabCachingInfo, URI)
					
				self._store_caches()

	def _get_vocab_data(self, newCache = True) :
		"""Just a macro like function to get the data to be cached"""		
		from pyRdfa.rdfs.process import return_graph
		(self.graph, self.expiration_date) = return_graph(self.uri, self.options, newCache)
		return self.graph != None

	def _store_caches(self) :
		"""Called if the creation date, etc, have been refreshed or new, and
		all content must be put into a cache file
		"""
		# Store the cached version of the vocabulary file
		fname = os.path.join(self.app_data_dir, self.filename)
		try :
			_dump(self.graph, fname)
		except Exception :
			(type,value,traceback) = sys.exc_info()
			if self.report : self.options.add_info("Could not write cache file %s (%s)", (fname,value), VocabCachingInfo, self.uri)
		# Update the index
		self.add_ref(self.uri,(self.filename, self.creation_date, self.expiration_date))
		
#########################################################################################################################################

def offline_cache_generation(args) :
	"""Generate a cache for the vocabulary in args.
	
	@param args: array of vocabulary URIs.
	"""
	class LocalOption :
		def __init__(self) :
			self.vocab_cache_report = True

		def pr(self, wae, txt, warning_type, context) :
			print( "====" )
			if warning_type != None : print( warning_type )
			print( wae + ": " + txt )
			if context != None: print( context )
			print( "====" )
			
		def add_warning(self, txt, warning_type=None, context=None) :
			"""Add a warning to the processor graph.
			@param txt: the warning text. 
			@keyword warning_type: Warning Class
			@type warning_type: URIRef
			@keyword context: possible context to be added to the processor graph
			@type context: URIRef or String
			"""
			self.pr("Warning",txt,warning_type,context)
	
		def add_info(self, txt, info_type=None, context=None) :
			"""Add an informational comment to the processor graph.
			@param txt: the information text. 
			@keyword info_type: Info Class
			@type info_type: URIRef
			@keyword context: possible context to be added to the processor graph
			@type context: URIRef or String
			"""
			self.pr("Info",txt,info_type,context)
	
		def add_error(self, txt, err_type=None, context=None) :
			"""Add an error  to the processor graph.
			@param txt: the information text. 
			@keyword err_type: Error Class
			@type err_type: URIRef
			@keyword context: possible context to be added to the processor graph
			@type context: URIRef or String
			"""
			self.pr("Error",txt,err_type,context)
			
	for uri in args :
		# This should write the cache
		print( ">>>>> Writing Cache <<<<<" )
		writ = CachedVocab(uri,options = LocalOption(),report = True)
		# Now read it back and print the content for tracing
		print( ">>>>> Reading Cache <<<<<" )
		rd = CachedVocab(uri,options = LocalOption(),report = True)
		print( "URI: " + uri )
		print( "default vocab: " + rd.vocabulary )
		print( "terms: %s prefixes: %s" % (rd.terms,rd.ns) )

	