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
from api import schemasInitialized

from rdflib import RDF

rdflib.plugin.register("json-ld", Parser, "rdflib_jsonld.parser", "JsonLDParser")
rdflib.plugin.register("json-ld", Serializer, "rdflib_jsonld.serializer", "JsonLDSerializer")

import logging
logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)

VOCAB = "http://schema.org"
STORE = rdflib.Dataset()

ROWSLOCK = threading.Lock() #rdflib uses generators which are not threadsafe

GETTRIPS = prepareQuery("SELECT ?g ?p ?o  WHERE {GRAPH ?g {?sub ?p ?o }}")
GETALL = prepareQuery("SELECT ?g ?p ?o  WHERE {GRAPH ?g {?s ?p ?o }}")

def load_graph(context, files):
	"""Read/parse/ingest schemas from data/*.rdfa."""
	import os.path
	import glob
	import re

	
	log.info("Loading %s graph." % context)
	g = rdflib.Graph(identifier=context)
	STORE.add_graph(g)
	for f in files:
		log.info("parse(%s,%s %s)" % (context, f, full_path(f)))
		g.parse(file=open(full_path(f),"r"),format="rdfa")

'''	subUri = rdflib.URIRef("http://schema.org/Thing")	
	res = STORE.query(GETTRIPS, initBindings={'sub':subUri})
	
	for row in res:
		log.info("=====================>  %s %s %s" % (row.g, row.p, row.o))
	
	log.info("SIZE %s" % len(list(STORE.triples( (None, None, None, None) ))))	

	res = STORE.query(GETALL)

	for row in res:
		log.info("====>  %s %s %s %s" % (row.s, row.p, row.o, row.g))
'''	
			
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
		layer = str(row.g)
		if first:
			first = False
			unit = api.Unit.GetUnitNoLoad(id,True)
#		log.info("Triples ?s: %s ?p %s ?o %s - %s" % (source,row.p,row.o,layer))
		s = stripID(source)
		p = stripID(row.p)
		if isinstance(row.o,rdflib.Literal):
			api.Triple.AddTripleText(unit, api.Unit.GetUnit(p,True), row.o, layer)
		else:
			obj = api.Unit.GetUnit(stripID(row.o),True)
			if p == "rdf:type": 
				typeOfInLayers.append(layer)
			
			if(p == "isPartOf"):
				if(unit.home != None and unit.home != layer):
					log.info("WARNING Cannot set %s home to %s - already set to: %s" % (s,layer,unit.home))
				unit.home = layer
				homeSetTo = layer
			
			prop = api.Unit.GetUnit(p,True)
			api.Triple.AddTriple(unit, prop, obj, layer)
			
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
		layer = str(row.g)
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
