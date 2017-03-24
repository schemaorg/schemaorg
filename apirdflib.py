#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import logging
logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)

import sys
sys.path.append('lib')
import rdflib
from rdflib import Literal
from rdflib.term import URIRef
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from rdflib.plugins.sparql import prepareQuery
import threading
import api
from apimarkdown import Markdown
import StringIO

rdflib.plugin.register("json-ld", Parser, "rdflib_jsonld.parser", "JsonLDParser")
rdflib.plugin.register("json-ld", Serializer, "rdflib_jsonld.serializer", "JsonLDSerializer")

ATTIC = 'attic'
VOCAB = "http://schema.org"
STORE = rdflib.Dataset()
#Namespace mapping#############
nss = {'core': 'http://schema.org/'}
revNss = {}
NSSLoaded = False
allLayersList = []

context_data = "data/internal-context" #Local file containing context to be used loding .jsonld files

RDFLIBLOCK = threading.Lock() #rdflib uses generators which are not threadsafe

from rdflib.namespace import RDFS, RDF, OWL
SCHEMA = rdflib.Namespace('http://schema.org/')

QUERYGRAPH = None
def queryGraph():
    global QUERYGRAPH
    if not QUERYGRAPH:
        try:
            RDFLIBLOCK.acquire()
            if not QUERYGRAPH:
                QUERYGRAPH = rdflib.Graph()
                gs = list(STORE.graphs())
                for g in gs:
                    id = str(g.identifier)
                    if not id.startswith("http://"):#skip some internal graphs
                        continue
                    QUERYGRAPH += g 
                QUERYGRAPH.bind('owl', 'http://www.w3.org/2002/07/owl#')
                QUERYGRAPH.bind('rdfa', 'http://www.w3.org/ns/rdfa#')
                QUERYGRAPH.bind('dct', 'http://purl.org/dc/terms/')
                QUERYGRAPH.bind('schema', 'http://schema.org/')
        finally:
            RDFLIBLOCK.release()
    return QUERYGRAPH

def loadNss():
    global NSSLoaded
    global nss
    global revNss
    if not NSSLoaded:
        NSSLoaded = True
        #log.info("allLayersList: %s"% allLayersList)
        for i in allLayersList:
            if i != "core":
                #log.info("Setting %s to %s" % (i, "http://%s.schema.org/" % i))
                nss.update({i:"http://%s.schema.org/" % i})
        revNss = {v: k for k, v in nss.items()}
               
def getNss(val):
    global nss
    loadNss()
    try:
        return nss[val]
    except KeyError:
        return ""
    
def getRevNss(val):
    global revNss
    loadNss()
    try:
        return revNss[val]
    except KeyError:
        return ""
##############################    

def load_graph(context, files):
    """Read/parse/ingest schemas from data/*.rdfa."""
    import os.path
    import glob
    import re

    log.debug("Loading %s graph." % context)
    for f in files:
        if(f[-5:] == ".rdfa"):
            format = "rdfa"
        elif(f[-7:] == ".jsonld"):
            format = "json-ld"
        else:
            log.info("Unrecognised file format: %s" % f) 
            return       
        if(format == "rdfa"):
            uri = getNss(context)
            g = STORE.graph(URIRef(uri))
            g.parse(file=open(full_path(f),"r"),format=format)
            STORE.bind(context,uri)
        elif(format == "json-ld"):
            STORE.parse(file=open(full_path(f),"r"),format=format, context=context_data)

    QUERYGRAPH = None  #In case we have loaded graphs since the last time QUERYGRAPH was set

def rdfGetTriples(id):
	"""All triples with node as subject."""
	targets = []
	fullId = id

#	log.info("rdfgetTriples(%s)" % fullId)
	if	':' in id: #Includes full path or namespaces
		fullId = id
	else:
		fullId = VOCAB + "/" + id
	#log.info("rdfgetTriples(%s)" % source)
	
	first = True
	unit = None
	
	homeSetTo = None
	typeOfInLayers = []

	try:
		RDFLIBLOCK.acquire()
		q = "SELECT ?g ?p ?o  WHERE {GRAPH ?g {<%s> ?p ?o }}" % fullId
		res = list(STORE.query(q))
	finally:
		RDFLIBLOCK.release()
		
	for row in res:
#		if source == "http://meta.schema.org/":
#		log.info("Triple: %s %s %s %s" % (source, row.p, row.o, row.g))
		layer = str(getRevNss(str(row.g)))
		if first:
			first = False
			unit = api.Unit.GetUnitNoLoad(id,True)
		s = stripID(fullId)
		p = stripID(row.p)
		if p == "rdf:type": 
			typeOfInLayers.append(layer)
		elif(p == "isPartOf"):
			if(unit.home != None and unit.home != layer):
				log.info("WARNING Cannot set %s home to %s - already set to: %s" % (s,layer,unit.home))
			unit.home = layer
			homeSetTo = layer
		elif(p == "category"):
			unit.category = row.o

		prop = api.Unit.GetUnit(p,True)

		if isinstance(row.o,rdflib.Literal):
			api.Triple.AddTripleText(unit, prop, row.o, layer)
		else: 
			api.Triple.AddTriple(unit, prop, api.Unit.GetUnit(stripID(row.o),True), layer)
			
	""" Default Unit.home to core if not specificly set with an 'isPartOf' triple """
	if(unit and homeSetTo == None):
		if('core' in typeOfInLayers or len(typeOfInLayers) == 0):
			unit.home = 'core'
		else:
			log.info("WARNING: %s defined in extensions %s but has no 'isPartOf' triple - cannot default home to core!" % (id,typeOfInLayers))
	return unit

def rdfGetSourceTriples(target):
	"""All source nodes for a specified arc pointing to a specified node (within any of the specified layers)."""
	id = target.id
	target.sourced = True
	sources = []
	fullId = id
	if	':' in id: #Includes full path or namespaces
		fullId = id
	else:
		fullId = VOCAB + "/" + id
	
	targ = fullId
	if fullId.startswith('http://'):
		targ = "<%s>" % fullId
				
	q = "SELECT ?g ?s ?p  WHERE {GRAPH ?g {?s ?p %s }}" % targ

	try:
		RDFLIBLOCK.acquire()
		res = list(STORE.query(q))
		#log.info("RESCOUNT %s" % len(res))
	finally:
		RDFLIBLOCK.release()

	for row in res:
		layer = str(getRevNss(str(row.g)))
		unit = api.Unit.GetUnit(stripID(row.s))
		p = stripID(row.p)
		prop = api.Unit.GetUnit(p,True)
		obj = api.Unit.GetUnit(stripID(fullId),True)
		api.Triple.AddTriple(unit, prop, obj, layer)
        
def countFilter(extension="ALL",includeAttic=False):
    excludeAttic = "FILTER NOT EXISTS {?term schema:isPartOf <http://attic.schema.org>}."
    if includeAttic or extension == ATTIC:
        excludeAttic = ""
    
    extensionSel = ""
    if extension == "ALL":
        extensionSel = ""
    elif extension == "core":
        extensionSel = "FILTER NOT EXISTS {?term schema:isPartOf ?ex}."
        excludeAttic = ""
    else:
        extensionSel = "FILTER EXISTS {?term schema:isPartOf <http://%s.schema.org>}." % extension

    return extensionSel + "\n" + excludeAttic
        
def countTypes(extension="ALL",includeAttic=False):
    filter = countFilter(extension=extension, includeAttic=includeAttic)
    query= ('''select (count (?term) as ?cnt) where { 
         ?term a rdfs:Class. 
         ?term rdfs:subClassOf* schema:Thing.
       %s
    }''') % filter
    graph = queryGraph()
    count = 0
    try:
        RDFLIBLOCK.acquire()
        res = graph.query(query)
        for row in res:
            count = row.cnt
    finally:
        RDFLIBLOCK.release()
    return count

def countProperties(extension="ALL",includeAttic=False):
 filter = countFilter(extension=extension, includeAttic=includeAttic)
 query= ('''select (count (?term) as ?cnt) where { 
        ?term a rdf:Property.
        FILTER EXISTS {?term rdfs:label ?l}.
        BIND(STR(?term) AS ?strVal).
        FILTER(STRLEN(?strVal) >= 18 && SUBSTR(?strVal, 1, 18) = "http://schema.org/").
    %s
 }''') % filter
 graph = queryGraph()
 count = 0
 try:
     RDFLIBLOCK.acquire()
     res = graph.query(query)
     for row in res:
         count = row.cnt
 finally:
     RDFLIBLOCK.release()
 return count
        
def countEnums(extension="ALL",includeAttic=False):
    filter = countFilter(extension=extension, includeAttic=includeAttic)
    query= ('''select (count (?term) as ?cnt) where { 
         ?term a ?type. 
         ?type rdfs:subClassOf* <http://schema.org/Enumeration>.
       %s
    }''') % filter
    graph = queryGraph()
    count = 0
    try:
        RDFLIBLOCK.acquire()
        res = graph.query(query)
        for row in res:
            count = row.cnt
    finally:
        RDFLIBLOCK.release()
    return count
    
def serializeSingleTermGrapth(node,format="json-ld",excludeAttic=True,markdown=True):
    graph = buildSingleTermGraph(node=node,excludeAttic=excludeAttic,markdown=markdown)
    file = StringIO.StringIO()
    kwargs = {'sort_keys': True}
    file.write(graph.serialize(format=format,**kwargs))
    data = file.getvalue()
    file.close()
    return data
    
def buildSingleTermGraph(node,excludeAttic=True,markdown=True):
    
    g = rdflib.Graph()
    g.bind('owl', 'http://www.w3.org/2002/07/owl#')
    g.bind('rdfa', 'http://www.w3.org/ns/rdfa#')
    g.bind('dct', 'http://purl.org/dc/terms/')
    g.bind('schema', 'http://schema.org/')
    
    full = "http://schema.org/" + node
    #n = URIRef(full)
    n = SCHEMA.term(node)
    n = n
    full = str(n)
    q = queryGraph()
    ret = None
    
    #log.info("NAME %s %s"% (n,full))
    atts = None
    try:
        RDFLIBLOCK.acquire()
        atts = list(q.triples((n,SCHEMA.isPartOf,URIRef("http://attic.schema.org"))))
    finally:
        RDFLIBLOCK.release()    
    if len(atts):
        #log.info("ATTIC TERM %s" % n)
        excludeAttic = False
    #Outgoing triples
    try:
        RDFLIBLOCK.acquire()
        ret = list(q.triples((n,None,None)))
    finally:
        RDFLIBLOCK.release()
    for (s,p,o) in ret:
        #log.info("adding %s %s %s" % (s,p,o))
        g.add((s,p,o))

    #Incoming triples
    ret = list(q.triples((None,None,n)))
    for (s,p,o) in ret:
        #log.info("adding %s %s %s" % (s,p,o))
        g.add((s,p,o))

    #super classes
    query='''select * where {
    ?term (^rdfs:subClassOf*) <%s>.
    ?term rdfs:subClassOf ?super.
    ?super ?pred ?obj.
    }''' % n
    try:
        RDFLIBLOCK.acquire()
        ret = q.query(query)
    finally:
        RDFLIBLOCK.release()
    for row in ret:
        #log.info("adding %s %s %s" % (row.term,RDFS.subClassOf,row.super))
        g.add((row.term,RDFS.subClassOf,row.super))
        g.add((row.super,row.pred,row.obj))
         
    #poperties with superclasses in domain
    query='''select * where{
    ?term (^rdfs:subClassOf*) <%s>.
    ?prop <http://schema.org/domainIncludes> ?term.
    ?prop ?pred ?obj.
    }
    ''' % n
    try:
        RDFLIBLOCK.acquire()
        ret = q.query(query)
    finally:
        RDFLIBLOCK.release()
    for row in ret:
        g.add((row.prop,SCHEMA.domainIncludes,row.term))
        g.add((row.prop,row.pred,row.obj))

    #super properties
    query='''select * where {
    ?term (^rdfs:subPropertyOf*) <%s>.
    ?term rdfs:subPropertyOf ?super.
    ?super ?pred ?obj.
    }''' % n
    try:
        RDFLIBLOCK.acquire()
        ret = q.query(query)
    finally:
        RDFLIBLOCK.release()
    for row in ret:
        #log.info("adding %s %s %s" % (row.term,RDFS.subPropertyOf,row.super))
        g.add((row.term,RDFS.subPropertyOf,row.super))
        g.add((row.super,row.pred,row.obj))

    #Enumeration for an enumeration value
    query='''select * where {
    <%s> a ?type.
    ?type ?pred ?obj.
    FILTER NOT EXISTS{?type a rdfs:class}.
    }''' % n
    try:
        RDFLIBLOCK.acquire()
        ret = q.query(query)
    finally:
        RDFLIBLOCK.release()
    for row in ret:
        #log.info("adding %s %s %s" % (row.type,row.pred,row.obj))
        g.add((row.type,row.pred,row.obj))

    if excludeAttic: #Remove triples referencing terms part of http://attic.schema.org
        trips = list(g.triples((None,None,None)))
        try:
            RDFLIBLOCK.acquire()
            for (s,p,o) in trips:
                atts = list(q.triples((s,SCHEMA.isPartOf,URIRef("http://attic.schema.org"))))
                if isinstance(o, URIRef):
                    atts.extend(q.triples((o,SCHEMA.isPartOf,URIRef("http://attic.schema.org"))))
                for (rs,rp,ro) in atts:
                    #log.info("Removing %s" % rs)
                    g.remove((rs,None,None))
                    g.remove((None,None,rs))
        finally:
            RDFLIBLOCK.release()
    if markdown:
        try:
            RDFLIBLOCK.acquire()
            trips = list(g.triples((None,RDFS.comment,None)))
            Markdown.setPre("http://schema.org/")
            for (s,p,com) in trips:
                mcom = Markdown.parse(com)
                g.remove((s,p,com))
                g.add((s,p,Literal(mcom)))
        finally:
            RDFLIBLOCK.release()
            Markdown.setPre()
    return g

def stripID (str):
    l = len(str)
    if (l > 17 and (str[:18] == 'http://schema.org/')):
        return str[18:]
    elif (l > 24 and (str[:25] == 'http://purl.org/dc/terms/')):
        return "dc:" + str[25:]
    elif (l > 36 and (str[:37] == 'http://www.w3.org/2000/01/rdf-schema#')):
        return "rdfs:" + str[37:]
    elif (l > 42 and (str[:43] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')):
        return "rdf:" + str[43:]
    elif (l > 29 and (str[:30] == 'http://www.w3.org/2002/07/owl#')):
        return "owl:" + str[30:]
    else:
        return str
			

def full_path(filename):
	"""convert local file name to full path."""
	import os.path
	folder = os.path.dirname(os.path.realpath(__file__))
	return os.path.join(folder, filename)
