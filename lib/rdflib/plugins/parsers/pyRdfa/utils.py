# -*- coding: utf-8 -*-
"""
Various utilities for pyRdfa.

Most of the utilities are straightforward.

@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}


"""

"""
$Id: utils.py,v 1.9 2012/11/16 17:51:53 ivan Exp $
$Date: 2012/11/16 17:51:53 $
"""
import os, os.path, sys, imp, datetime

# Python 3 vs. 2 switch
if sys.version_info[0] >= 3 :
	from urllib.request import Request, urlopen
	from urllib.parse   import urljoin, quote
	from http.server    import BaseHTTPRequestHandler
	from urllib.error   import HTTPError as urllib_HTTPError
else :
	from urllib2        import Request, urlopen
	from urllib2        import HTTPError as urllib_HTTPError
	from urlparse       import urljoin
	from urllib         import quote
	from BaseHTTPServer import BaseHTTPRequestHandler

from .extras.httpheader import content_type, parse_http_datetime

import rdflib
if rdflib.__version__ >= "3.0.0" :
	from rdflib	import RDF as ns_rdf
else :
	from rdflib.RDF	import RDFNS  as ns_rdf

from .host import HostLanguage, preferred_suffixes

#########################################################################################################
# Handling URIs
class URIOpener :
	"""A wrapper around the urllib2 method to open a resource. Beyond accessing the data itself, the class
	sets a number of instance variable that might be relevant for processing.
	The class also adds an accept header to the outgoing request, namely
	text/html and application/xhtml+xml (unless set explicitly by the caller).
	
	If the content type is set by the server, the relevant HTTP response field is used. Otherwise,
	common suffixes are used (see L{host.preferred_suffixes}) to set the content type (this is really of importance
	for C{file:///} URI-s). If none of these works, the content type is empty.
		
	Interpretation of the content type for the return is done by Deron Meranda's U{httpheader module<http://deron.meranda.us/>}.
	
	@ivar data: the real data, ie, a file-like object
	@ivar headers: the return headers as sent back by the server
	@ivar content_type: the content type of the resource or the empty string, if the content type cannot be determined
	@ivar location: the real location of the data (ie, after possible redirection and content negotiation)
	@ivar last_modified_date: sets the last modified date if set in the header, None otherwise
	@ivar expiration_date: sets the expiration date if set in the header, I{current UTC plus one day} otherwise (this is used for caching purposes, hence this artificial setting)
	"""
	CONTENT_LOCATION	= 'Content-Location'
	CONTENT_TYPE		= 'Content-Type'
	LAST_MODIFIED		= 'Last-Modified'
	EXPIRES				= 'Expires'
	def __init__(self, name, additional_headers = {}) :
		"""
		@param name: URL to be opened
		@keyword additional_headers: additional HTTP request headers to be added to the call
		"""		
		try :
			import sys
			import urllib

			platform = sys.platform
			if platform == 'Windows' or platform == 'win32' or platform == 'nt' or platform == 'win64':
				# Running on Windows which doesn't like file URLs not prefixed with 'file:'
				if not name.startswith('http://') and not name.startswith('https://'):			
					name = 'file:' + urllib.pathname2url(name)

			# Note the removal of the fragment ID. This is necessary, per the HTTP spec
			req = Request(url=name.split('#')[0])

			for key in additional_headers :
				req.add_header(key, additional_headers[key])
			if 'Accept' not in additional_headers :
				req.add_header('Accept', 'text/html, application/xhtml+xml')
				
			self.data		= urlopen(req)
			self.headers	= self.data.info()
			
			if URIOpener.CONTENT_TYPE in self.headers :
				# The call below will remove the possible media type parameters, like charset settings
				ct = content_type(self.headers[URIOpener.CONTENT_TYPE])
				self.content_type = ct.media_type
				if 'charset' in ct.parmdict :
					self.charset = ct.parmdict['charset']
				else :
					self.charset = None
				# print
			else :
				# check if the suffix can be used for the content type; this may be important
				# for file:// type URI or if the server is not properly set up to return the right
				# mime type
				self.charset = None
				self.content_type = ""
				for suffix in preferred_suffixes.keys() :
					if name.endswith(suffix) :
						self.content_type = preferred_suffixes[suffix]
						break
			
			if URIOpener.CONTENT_LOCATION in self.headers :
				self.location = urljoin(self.data.geturl(),self.headers[URIOpener.CONTENT_LOCATION])
			else :
				self.location = name
			
			self.expiration_date = datetime.datetime.utcnow() + datetime.timedelta(days=1)
			if URIOpener.EXPIRES in self.headers :
				try :
					# Thanks to Deron Meranda for the HTTP date conversion method...
					self.expiration_date = parse_http_datetime(self.headers[URIOpener.EXPIRES])
				except :
					# The Expires date format was wrong, sorry, forget it...
					pass

			self.last_modified_date = None
			if URIOpener.LAST_MODIFIED in self.headers :
				try :
					# Thanks to Deron Meranda for the HTTP date conversion method...
					self.last_modified_date = parse_http_datetime(self.headers[URIOpener.LAST_MODIFIED])
				except :
					# The last modified date format was wrong, sorry, forget it...
					pass
				
		except urllib_HTTPError :
			e = sys.exc_info()[1]
			from . import HTTPError
			msg = BaseHTTPRequestHandler.responses[e.code]
			raise HTTPError('%s' % msg[1], e.code)
		except Exception :
			e = sys.exc_info()[1]
			from . import RDFaError
			raise RDFaError('%s' % e)

#########################################################################################################

# 'safe' characters for the URI quoting, ie, characters that can safely stay as they are. Other 
# special characters are converted to their %.. equivalents for namespace prefixes
_unquotedChars = ':/\?=#~'
_warnChars     = [' ','\n','\r','\t']

def quote_URI(uri, options = None) :
	"""
	'quote' a URI, ie, exchange special characters for their '%..' equivalents. Some of the characters
	may stay as they are (listed in L{_unquotedChars}. If one of the characters listed in L{_warnChars} 
	is also in the uri, an extra warning is also generated.
	@param uri: URI
	@param options: 
	@type options: L{Options<pyRdfa.Options>}
	"""
	from . import err_unusual_char_in_URI
	suri = uri.strip()
	for c in _warnChars :
		if suri.find(c) != -1 :
			if options != None :
				options.add_warning(err_unusual_char_in_URI % suri)
			break
	return quote(suri, _unquotedChars)
	
#########################################################################################################
	
def create_file_name(uri) :
	"""
	Create a suitable file name from an (absolute) URI. Used, eg, for the generation of a file name for a cached vocabulary file.
	"""
	suri = uri.strip()
	final_uri = quote(suri,_unquotedChars)
	# Remove some potentially dangereous characters
	return final_uri.replace(' ','_').replace('%','_').replace('-','_').replace('+','_').replace('/','_').replace('?','_').replace(':','_').replace('=','_').replace('#','_')

#########################################################################################################
def has_one_of_attributes(node,*args) :
	"""
	Check whether one of the listed attributes is present on a (DOM) node.
	@param node: DOM element node
	@param args: possible attribute names
	@return: True or False
	@rtype: Boolean
	"""
	if len(args) == 0 :
		return None
	if isinstance(args[0], tuple) or isinstance(args[0], list) :
		rargs = args[0]
	else :
		rargs = args
	
	return True in [ node.hasAttribute(attr) for attr in rargs ]

#########################################################################################################
def traverse_tree(node, func) :
	"""Traverse the whole element tree, and perform the function C{func} on all the elements.
	@param node: DOM element node
	@param func: function to be called on the node. Input parameter is a DOM Element Node. If the function returns a boolean True, the recursion is stopped.
	"""
	if func(node) :
		return

	for n in node.childNodes :
		if n.nodeType == node.ELEMENT_NODE :
			traverse_tree(n, func)

#########################################################################################################
def return_XML(state, inode, base = True, xmlns = True) :
	"""
	Get (recursively) the XML Literal content of a DOM Element Node. (Most of the processing is done
	via a C{node.toxml} call of the xml minidom implementation.)

	@param inode: DOM Node
	@param state: L{pyRdfa.state.ExecutionContext}
	@param base: whether the base element should be added to the output
	@type base: Boolean
	@param xmlns: whether the namespace declarations should be repeated in the generated node
	@type xmlns: Boolean
	@return: string
	"""
	node = inode.cloneNode(True)
	# Decorate the element with namespaces.lang values and, optionally, base
	if base :
		node.setAttribute("xml:base",state.base)
	if xmlns :
		for prefix in state.term_or_curie.xmlns :
			if not node.hasAttribute("xmlns:%s" % prefix) :
				node.setAttribute("xmlns:%s" % prefix,"%s" % state.term_or_curie.xmlns[prefix])
		# Set the default namespace, if not done (and is available)
		if not node.getAttribute("xmlns") and state.defaultNS != None :
			node.setAttribute("xmlns", state.defaultNS)
	# Get the lang, if necessary
	if state.lang :
		if state.options.host_language in [ HostLanguage.xhtml, HostLanguage.xhtml5, HostLanguage.html5 ] :
			if not node.getAttribute("lang") :
				node.setAttribute("lang", state.lang)
		else :
			if not node.getAttribute("xml:lang") :
				node.setAttribute("xml:lang", state.lang)
	
	if sys.version_info[0] >= 3 :
		return node.toxml()
	else :
		q = node.toxml(encoding='utf-8')
		return unicode(q, encoding='utf-8')

#########################################################################################################

def dump(node) :
	"""
	This is just for debug purposes: it prints the essential content of the node in the tree starting at node.

	@param node: DOM node
	"""
	print( node.toprettyxml(indent="", newl="") )
	

	
