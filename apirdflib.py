#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import sys
sys.path.append('lib')
import rdflib
from rdflib.term import URIRef
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from rdflib.plugins.sparql import prepareQuery
import threading
import api

from rdflib import RDF

rdflib.plugin.register("json-ld", Parser, "rdflib_jsonld.parser", "JsonLDParser")
rdflib.plugin.register("json-ld", Serializer, "rdflib_jsonld.serializer", "JsonLDSerializer")

import logging
logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)

VOCAB = "http://schema.org"
STORE = rdflib.Dataset()
#Namespace mapping#############
nss = {'core': 'http://schema.org/'}
revNss = {}
NSSLoaded = False
allLayersList = []


def loadNss():
    global NSSLoaded
    global nss
    global revNss
    if not NSSLoaded:
        NSSLoaded = True
        for i in allLayersList:
            if i != "core":
                nss.update({i:"http://%s.schema.org" % i})
        revNss = {v: k for k, v in nss.items()}
               
def getNss(val):
    global nss
    loadNss()
    return nss[val]
    
def getRevNss(val):
    global revNss
    loadNss()
    return revNss[val]
##############################    


ROWSLOCK = threading.Lock() #rdflib uses generators which are not threadsafe

GETTRIPS = prepareQuery("SELECT ?g ?p ?o  WHERE {GRAPH ?g {?sub ?p ?o }}")
GGETALL = prepareQuery("SELECT ?g ?s ?p ?o  WHERE {GRAPH ?g {?s ?p ?o }}")
GETALL = prepareQuery("SELECT ?s ?p ?o  WHERE {?s ?p ?o }")
GETP = prepareQuery("SELECT DISTINCT ?p   WHERE {GRAPH ?g { ?s ?p ?o }} ORDER BY ?p")

def load_graph(context, files):
    """Read/parse/ingest schemas from data/*.rdfa."""
    import os.path
    import glob
    import re


    log.info("Loading %s graph." % context)
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
            STORE.parse(file=open(full_path(f),"r"),format=format)
							
def rdfGetTriples(id):
	"""All triples with node as subject."""
	targets = []
	fullId = id
	if	':' in id: #Includes full path or namespaces
		fullId = id
	else:
		fullId = VOCAB + "/" + id
	source = URIRef(fullId)
	
	first = True
	unit = None
	
#	log.info("Getting triples for %s" % source)
	homeSetTo = None
	typeOfInLayers = []

	try:
		ROWSLOCK.acquire()
		res = list(STORE.query(GETTRIPS, initBindings={'sub':source}))
	finally:
		ROWSLOCK.release()
		
	for row in res:
		layer = str(getRevNss(str(row.g)))
		if first:
			first = False
			unit = api.Unit.GetUnitNoLoad(id,True)
#		log.info("Triples ?s: %s ?p %s ?o %s - %s" % (source,row.p,row.o,layer))
		s = stripID(source)
		p = stripID(row.p)
		if p == "rdf:type": 
			typeOfInLayers.append(layer)
		elif(p == "isPartOf"):
			if(unit.home != None and unit.home != layer):
				log.info("WARNING Cannot set %s home to %s - already set to: %s" % (s,layer,unit.home))
			unit.home = layer
			homeSetTo = layer

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
		ROWSLOCK.acquire()
		res = list(STORE.query(q))
		#log.info("RESCOUNT %s" % len(res))
	finally:
		ROWSLOCK.release()

	for row in res:
		layer = str(getRevNss(str(row.g)))
		unit = api.Unit.GetUnit(stripID(row.s))
		p = stripID(row.p)
		prop = api.Unit.GetUnit(p,True)
		obj = api.Unit.GetUnit(stripID(fullId),True)
		api.Triple.AddTriple(unit, prop, obj, layer)
	
def stripID (str):
    #log.info("%s %s " % (len('http://schema.org'), len('http://www.w3.org/2000/01/rdf-schema#')))
    l = len(str)
    if (l > 16 and (str[:17] == 'http://schema.org')):
        return str[18:]
    elif (l > 24 and (str[:25] == 'http://purl.org/dc/terms/')):
        return "dc:" + str[25:]
    elif (l > 36 and (str[:37] == 'http://www.w3.org/2000/01/rdf-schema#')):
        return "rdfs:" + str[37:]
    elif (l > 42 and (str[:43] == 'http://www.w3.org/1999/02/22-rdf-syntax-ns#')):
        return "rdf:" + str[43:]
    else:
        return str
			

def full_path(filename):
	"""convert local file name to full path."""
	import os.path
	folder = os.path.dirname(os.path.realpath(__file__))
	return os.path.join(folder, filename)
