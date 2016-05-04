# -*- coding: utf-8 -*-
"""
Separate module to handle vocabulary expansions. The L{cache} module takes care of caching vocabulary graphs; the L{process}
module takes care of the expansion itself.

@organization: U{World Wide Web Consortium<http://www.w3.org>}
@author: U{Ivan Herman<a href="http://www.w3.org/People/Ivan/">}
@license: This software is available for use under the
U{W3C® SOFTWARE NOTICE AND LICENSE<href="http://www.w3.org/Consortium/Legal/2002/copyright-software-20021231">}

"""

"""
$Id: __init__.py,v 1.4 2012/08/20 13:15:28 ivan Exp $ $Date: 2012/08/20 13:15:28 $

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
	from rdflib.Graph 	import Graph

from .. import RDFaError, pyRdfaError
from .. import ns_rdfa, ns_xsd, ns_distill

VocabCachingInfo = ns_distill["VocabCachingInfo"]


# Error message texts

err_outdated_cache  			= "Vocab document <%s> could not be dereferenced; using possibly outdated cache"
err_unreachable_vocab  			= "Vocab document <%s> could not be dereferenced"
err_unparsable_Turtle_vocab 	= "Could not parse vocab in Turtle at <%s> (%s)"
err_unparsable_xml_vocab 		= "Could not parse vocab in RDF/XML at <%s> (%s)"
err_unparsable_ntriples_vocab 	= "Could not parse vocab in N-Triple at <%s> (%s)"
err_unparsable_rdfa_vocab 		= "Could not parse vocab in RDFa at <%s> (%s)"
err_unrecognised_vocab_type		= "Unrecognized media type for the vocab file <%s>: '%s'"
