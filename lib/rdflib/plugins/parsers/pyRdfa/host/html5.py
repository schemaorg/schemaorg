# -*- coding: utf-8 -*-
"""
Simple transfomer for HTML5: add a @src for any @data, add a @content for the @value attribute of the <data> element, and interpret the <time> element.

@summary: Add a top "about" to <head> and <body>
@requires: U{RDFLib package<http://rdflib.net>}
@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}
@contact: Ivan Herman, ivan@w3.org
"""

"""
$Id: html5.py,v 1.13 2013-02-01 10:53:48 ivan Exp $
$Date: 2013-02-01 10:53:48 $
"""
try :
	from functools import reduce
except :
	# Not important. This import is necessary in Python 3 only and the newer versions of Python 2.X it is there
	# for a forward compatibility with Python 3
	pass

# The handling of datatime is a little bit more complex... better put this in a separate function for a better management
from datetime import datetime
import re
datetime_type   = "http://www.w3.org/2001/XMLSchema#dateTime"
time_type 	    = "http://www.w3.org/2001/XMLSchema#time"
date_type       = "http://www.w3.org/2001/XMLSchema#date"
date_gYear      = "http://www.w3.org/2001/XMLSchema#gYear"
date_gYearMonth = "http://www.w3.org/2001/XMLSchema#gYearMonth"
date_gMonthDay  = "http://www.w3.org/2001/XMLSchema#gMonthDay"
duration_type   = "http://www.w3.org/2001/XMLSchema#duration"
plain           = "plain"

handled_time_types = [ datetime_type, time_type, date_type, date_gYear, date_gYearMonth, date_gMonthDay, duration_type ]

_formats = {
	date_gMonthDay	  : [ "%m-%d" ],
	date_gYearMonth	  : [ "%Y-%m"],
	date_gYear     	  : [ "%Y" ],
	date_type      	  : [ "%Y-%m-%d", "%Y-%m-%dZ" ],
	time_type      	  : [ "%H:%M",
					      "%H:%M:%S",
					      "%H:%M:%SZ",						
					      "%H:%M:%S.%f" ],
	datetime_type  	  : [ "%Y-%m-%dT%H:%M",
					      "%Y-%m-%dT%H:%M:%S",
					      "%Y-%m-%dT%H:%M:%S.%f",
					      "%Y-%m-%dT%H:%MZ",
					      "%Y-%m-%dT%H:%M:%SZ",
					      "%Y-%m-%dT%H:%M:%S.%fZ" ],
	duration_type     : [ "P%dD",
						  "P%YY%mM%dD",
						  "P%YY%mM",
						  "P%YY%dD",
						  "P%YY",
						  "P%mM",
						  "P%mM%dD",
						 ],
}

_dur_times = [ "%HH%MM%SS", "%HH", "%MM", "%SS", "%HH%MM", "%HH%SS", "%MM%SS" ]

def _format_test(string) :
	"""
	Tests the string format to see whether it fits one of the time datatypes
	@param string: attribute value to test
	@return: a URI for the xsd datatype or the string 'plain'
	"""
	# Try to get the easy cases:
	for key in _formats :
		for format in _formats[key] :
			try :
				# try to check if the syntax is fine
				d = datetime.strptime(string, format)
				# bingo!
				return key
			except ValueError :
				pass
			
	# Now come the special cases:-(
	# Check first for the duration stuff, that is the nastiest.
	if len(string) > 2 and (string[0] == 'P' or (string[0] == '-' and string[1] == 'P')) :
		# this is meant to be a duration type
		# first of all, get rid of the leading '-' and check again
		if string[0] == '-' :
			for format in _formats[duration_type] :
				try :
					# try to check if the syntax is fine
					d = datetime.strptime(string, format)
					# bingo!
					return duration_type
				except ValueError :
					pass
		# Let us see if the value contains a separate time portion, and cut that one
		durs = string.split('T')
		if len(durs) == 2 :
			# yep, so we should check again
			dur = durs[0]
			tm  = durs[1]
			# Check the duration part
			td = False
			for format in _formats[duration_type] :
				try :
					# try to check if the syntax is fine
					d = datetime.strptime(dur, format)
					# bingo!
					td = True
					break
				except ValueError :
					pass
			if td == True :
				# Getting there...
				for format in _dur_times :
					try :
						# try to check if the syntax is fine
						d = datetime.strptime(tm, format)
						# bingo!
						return duration_type
					except ValueError :
						pass
			# something went wrong...
			return plain			
		else :
			# Well, no more tricks, this is a plain type
			return plain
	
	
	# If we got here, we should check the time zone
	# there is a discrepancy betwen the python and the HTML5/XSD lexical string,
	# which means that this has to handled separately for the date and the timezone portion
	try :
		# The time-zone-less portion of the string
		str = string[0:-6]
		# The time-zone portion
		tz = string[-5:]
		try :
			t = datetime.strptime(tz,"%H:%M")
		except ValueError :
			# Bummer, this is not a correct time
			return plain
		# The time-zone is fine, the datetime portion has to be checked		
		for format in _formats[datetime_type] :
			try :
				# try to check if it is fine
				d = datetime.strptime(str, format)
				# Bingo!
				return datetime_type
			except ValueError :
				pass
	except :
		pass
	return plain

def html5_extra_attributes(node, state) :
	"""
	@param node: the current node that could be modified
	@param state: current state
	@type state: L{Execution context<pyRdfa.state.ExecutionContext>}
	"""
	def _get_literal(Pnode):
		"""
		Get (recursively) the full text from a DOM Node.
	
		@param Pnode: DOM Node
		@return: string
		"""
		rc = ""
		for node in Pnode.childNodes:
			if node.nodeType == node.TEXT_NODE:
				rc = rc + node.data
			elif node.nodeType == node.ELEMENT_NODE :
				rc = rc + self._get_literal(node)
		if state.options.space_preserve :
			return rc
		else :
			return re.sub(r'(\r| |\n|\t)+'," ",rc).strip()
		#return re.sub(r'(\r| |\n|\t)+',"",rc).strip()
	# end _getLiteral

	def _set_time(value) :
		if not node.hasAttribute("datatype") :			
			# Check the datatype:
			dt = _format_test(value)
			if dt != plain :
				node.setAttribute("datatype",dt)
		# Finally, set the value itself
		node.setAttribute("content",value)
	# end _set_time

	if not node.hasAttribute("content") :
		# @content has top priority over the others...
		if node.hasAttribute("datetime") :
			_set_time( node.getAttribute("datetime") )
		elif node.hasAttribute("dateTime") :
			_set_time( node.getAttribute("dateTime") )
		elif node.tagName == "time" :
			# Note that a possible @datetime value has already been taken care of
			_set_time( _get_literal(node) )
		
def remove_rel(node, state):
	"""
	If @property and @rel/@rev are on the same element, then only CURIE and URI can appear as a rel/rev value.
	
	@param node: the current node that could be modified
	@param state: current state
	@type state: L{Execution context<pyRdfa.state.ExecutionContext>}
	"""
	from ..termorcurie import termname
	def _massage_node(node,attr) :
		"""The real work for remove_rel is done here, parametrized with @rel and @rev"""
		if node.hasAttribute("property") and node.hasAttribute(attr) :
			vals = node.getAttribute(attr).strip().split()
			if len(vals) != 0 :
				final_vals = [ v for v in vals if not termname.match(v) ]
				if len(final_vals) == 0 :
					node.removeAttribute(attr)
				else :
					node.setAttribute(attr, reduce(lambda x,y: x+' '+y,final_vals))
	
	_massage_node(node, "rev")
	_massage_node(node, "rel")
	
	
	
	
	
	
	
	
	
	
	
	
	
