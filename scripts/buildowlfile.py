#!/usr/bin/env python2.7
import unittest
import os
from os import path, getenv
from os.path import expanduser
import logging # https://docs.python.org/2/library/logging.html#logging-levels
import glob
import argparse
import sys
import csv
from time import gmtime, strftime

sys.path.append( os.getcwd() )
sys.path.insert( 1, 'lib' ) #Pickup libs, rdflib etc., from shipped lib directory
sys.path.insert( 1, 'sdopythonapp' ) #Pickup sdopythonapp functionality
sys.path.insert( 1, 'sdopythonapp/lib' ) #Pickup sdopythonapp libs, rdflib etc., from shipped lib directory
sys.path.insert( 1, 'sdopythonapp/site' ) #Pickup sdopythonapp from shipped site
sys.path.insert( 1, 'lib' ) #Pickup libs, rdflib etc., from shipped lib directory
# Ensure that the google.appengine.* packages are available
# in tests as well as all bundled third-party packages.

sdk_path = getenv('APP_ENGINE',  expanduser("~") + '/google-cloud-sdk/platform/google_appengine/')
sys.path.insert(0, sdk_path) # add AppEngine SDK to path

import dev_appserver
dev_appserver.fix_sys_path()

from testharness import *
#Setup testharness state BEFORE importing sdo libraries
setInTestHarness(True)

from api import *
import rdflib
from rdflib import Graph
from rdflib.term import URIRef, Literal
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from rdflib.plugins.sparql import prepareQuery
from rdflib.compare import graph_diff
from rdflib.namespace import RDFS, RDF
import threading

os.environ["WARMUPSTATE"] = "off"
from sdoapp import *
from sdoapp import SCHEMA_VERSION


from api import inLayer, read_file, full_path, read_schemas, read_extensions, read_examples, namespaces, DataCache, getMasterStore
from apirdflib import getNss, getRevNss
from apimarkdown import Markdown

from sdordf2csv import sdordf2csv


rdflib.plugin.register("json-ld", Serializer, "rdflib_jsonld.serializer", "JsonLDSerializer")

# Ensure that the google.appengine.* packages are available
# in tests as well as all bundled third-party packages.
import dev_appserver
dev_appserver.fix_sys_path()

TODAY = strftime("%Y-%m-%d",gmtime())
parser = argparse.ArgumentParser()
parser.add_argument("-e","--exclude", default= [[]],action='append',nargs='*', help="Exclude graph(s) [core|extensions|all|bib|auto|meta|{etc} (Repeatable) -  'attic' always excluded")
parser.add_argument("-o","--output", default="docs/schemaorg.owl", help="output file (default: docs/schemaorg.owl)")
args = parser.parse_args()
#print "%s: Arguments: %s" % (sys.argv[0],args)


logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

#Setup testharness state BEFORE importing sdoapp
import sdoapp
from sdoapp import ENABLED_EXTENSIONS 
from xml.etree import ElementTree as ET
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from apimarkdown import Markdown


NAMESPACES = {
    "xml:base":"http://schema.org/",
    "xmlns": "http://schema.org/",
    "xmlns:schema": "http://schema.org/",
    "xmlns:rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "xmlns:rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xmlns:owl": "http://www.w3.org/2002/07/owl#",
    "xmlns:dcterms": "http://purl.org/dc/terms/",
    "xmlns:xsd": "http://www.w3.org/2001/XMLSchema#"
}

from rdflib.term import URIRef
DOMAININC = URIRef("http://schema.org/domainIncludes")
RANGEINC = URIRef("http://schema.org/rangeIncludes")
INVERSEOF = URIRef("http://schema.org/inverseOf")
SUPERSEDEDBY = URIRef("http://schema.org/supersededBy")
DEFAULTRANGES = ["http://schema.org/Text","http://schema.org/URL","http://schema.org/Role"]
DATATYPES = ["http://schema.org/Boolean",
            "http://schema.org/Date",
            "http://schema.org/DateTime",
            "http://schema.org/Number",
            "http://schema.org/Float",
            "http://schema.org/Integer",
            "http://schema.org/Time"]

class OwlBuild():
    def __init__(self):
        Markdown.setPre("http://schema.org/")
        self.typesCount = self.propsCount = self.namedCount = 0
        self.openFile()
        self.createDom()
        self.setSkips()
        self.getGraphs()
        self.loadGraphs()
        self.cleanup()
        self.closeFile()
        

    def setSkips(self):
        self.skiplist = [''] 
        for e in args.exclude:
            for s in e:
                if s == "core":
                    self.skiplist.append("http://schema.org/")
                elif s == "extensions":
                    for i in sdoapp.ENABLED_EXTENSIONS:
                        self.skiplist.append(getNss(i))
                elif s == "all":
                    self.skiplist.append("http://schema.org/")
                    for i in sdoapp.ENABLED_EXTENSIONS:
                        self.skiplist.append(getNss(i))
                else:
                    self.skiplist.append(getNss(s))
        if not getNss('attic') in self.skiplist: #Always skip attic by defualt
            self.skiplist.append(getNss('attic'))

    def openFile(self):
        self.file = open(args.output,'w')
        
    def createDom(self):
        self.dom = Element('rdf:RDF')
        for (k,v) in NAMESPACES.items():
            self.dom.set(k,v)
        
        self.dom.append(Comment("\n\tGenerated from Schema.org version: %s on: %s\n\t" % (SCHEMA_VERSION,TODAY)))
        self.ont = SubElement(self.dom,"owl:Ontology")
        self.ont.set("rdf:about","http://schema.org/")
        info = SubElement(self.ont,"owl:versionInfo")
        info.set("rdf:datatype","http://www.w3.org/2001/XMLSchema#string")
        info.text = SCHEMA_VERSION
        x = SubElement(self.ont,"rdfs:label")
        x.text = "Schema.org Vocabulary"
        x = SubElement(self.ont,"dcterms:modified")
        x.set("rdf:datatype", "http://www.w3.org/2001/XMLSchema#dat")
        x.text = strftime("%Y-%m-%d",gmtime())
        self.dom.append(Comment("\n\t/////////////////////\n\t/ Definitions\n\t/////////////////////\n\n\t"))
        
        
    def cleanup(self):
        out = self.prettify(self.dom)
        self.file.write(out)
        #log.info("OUT>\n%s" % out)
        
    def prettify(self,elem):
        # log.info("doc: %s" % ET.tostring(elem))
        doc = minidom.parseString(ET.tostring(elem))
        return doc.toprettyxml(encoding='UTF-8')

            
    def closeFile(self):
        log.info( "Wrote %s types %s properties %s NamedIndividuals to %s" % (self.typesCount, self.propsCount, self.namedCount, args.output))
        self.file.close()
        
    def getGraphs(self):
        self.store = getMasterStore()
        self.fullGraph = getQueryGraph()
        #read_schemas(loadExtensions=True)
        #read_extensions(sdoapp.ENABLED_EXTENSIONS)
        self.graphs = list(self.store.graphs())



    def loadGraphs(self):
        gs = sorted(list(self.store.graphs()),key=lambda u: u.identifier)

        for g in gs: #Put core first
            if str(g.identifier) == "http://schema.org/":
                gs.remove(g)
                gs.insert(0,g)
                break
        outgraph = Graph()

        for g in gs:
            id = str(g.identifier)
            if not id.startswith("http://"):#skip some internal graphs
                continue    
            if id not in self.skiplist:
                print "%s: Processing: %s  (%s) " % (sys.argv[0],id,len(g))
                #self.list(g)
                outgraph += g
        self.list(outgraph)

    def list(self, graph):
        types = {}
        props = {}
        exts = []
        self.dom.append(Comment("\n\t/////////////////////\n\t/ Class Definitions\n\t/////////////////////\n\t"))
        
        for (s,p,o) in graph.triples((None,RDF.type,RDFS.Class)):
            if s.startswith("http://schema.org"):
                types.update({s:graph.identifier})

        for t in sorted(types.keys()):
            self.outputType(t,graph)
            
        self.dom.append(Comment("\n\t/////////////////////\n\t/ Property Definitions\n\t/////////////////////\n\t"))
        for (s,p,o) in graph.triples((None,RDF.type,RDF.Property)):
            if s.startswith("http://schema.org"):
                props.update({s:graph.identifier})

        for p in sorted(props.keys()):
            self.outputProp(p,graph)
            
        self.dom.append(Comment("\n\t/////////////////////\n\t/ Named Individuals Definitions\n\t/////////////////////\n\t"))
        self.outputEnums(graph)
        self.outputNamedIndividuals("http://schema.org/True",graph)    
        self.outputNamedIndividuals("http://schema.org/False",graph)    

    def outputType(self, uri, graph):
        self.typesCount += 1
        
        typ = SubElement(self.dom,"owl:Class")
        typ.set("rdf:about",uri)
        ext = None
        for (p,o) in graph.predicate_objects(uri):
            if p == RDFS.label:
                l = SubElement(typ,"rdfs:label")
                l.set("xml:lang","en")
                l.text = o
            elif p == RDFS.comment:
                c = SubElement(typ,"rdfs:comment")
                c.set("xml:lang","en")
                c.text = Markdown.parse(o)
            elif p == RDFS.subClassOf:
                s = SubElement(typ,"rdfs:subClassOf")
                s.set("rdf:resource",o)
            elif p == URIRef("http://schema.org/isPartOf"): #Defined in an extension
                ext = str(o)
            elif p == RDF.type and o == URIRef("http://schema.org/DataType"): #A datatype
                s = SubElement(typ,"rdfs:subClassOf")
                s.set("rdf:resource","http://schema.org/DataType")
        
        typ.append(self.addDefined(uri,ext))
                
    def outputProp(self,uri, graph):
        self.propsCount += 1
        children = []
        domains = {}
        ranges = []
        datatypeonly = True
        ext = None        
        for (p,o) in graph.predicate_objects(uri):
            if p == RDFS.label:
                l = Element("rdfs:label")
                l.set("xml:lang","en")
                l.text = o
                children.append(l)
            elif p == RDFS.comment:
                c = Element("rdfs:comment")
                c.set("xml:lang","en")
                c.text = Markdown.parse(o)
                children.append(c)
            elif p == RDFS.subPropertyOf:
                sub = Element("rdfs:subPropertyOf")
                subval = str(o)
                if subval == "rdf:type":  #Fixes a special case with schema:additionalType
                    subval = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"
                    
                sub.set("rdf:resource",subval)
                children.append(sub)
            elif p == INVERSEOF:
                sub = Element("owl:inverseOf")
                sub.set("rdf:resource",o)
                children.append(sub)
            elif p == SUPERSEDEDBY:
                sub = Element("schema:supersededBy")
                sub.set("rdf:resource",o)
                children.append(sub)
            elif p == DOMAININC:
                domains[o] = True
            elif p == RANGEINC:
                ranges.append(str(o))
                if str(o) not in DATATYPES:
                    datatypeonly = False
            elif p == URIRef("http://schema.org/isPartOf"):
                ext = str(o)
                
        children.append(self.addDefined(uri,ext))
                
                
        if not datatypeonly:
            for r in DEFAULTRANGES:
                if r not in ranges:
                    ranges.append(r)
                
        if len(domains):
            d = Element("rdfs:domain")
            children.append(d)
            cl = SubElement(d,"owl:Class")
            u = SubElement(cl,"owl:unionOf")
            u.set("rdf:parseType","Collection")
            for target in domains.keys():
                targ = SubElement(u,"owl:Class")
                targ.set("rdf:about",target)

        if len(ranges):
            r = Element("rdfs:range")
            children.append(r)
            cl = SubElement(r,"owl:Class")
            u = SubElement(cl,"owl:unionOf")
            u.set("rdf:parseType","Collection")
            for target in ranges:
                targ = SubElement(u,"owl:Class")
                targ.set("rdf:about",target)
                
                
        if datatypeonly:
            prop = SubElement(self.dom,"owl:DatatypeProperty")            
        else:
            prop = SubElement(self.dom,"owl:ObjectProperty")
        prop.set("rdf:about",uri)
        for sub in children:
            prop.append(sub)
            
    def addDefined(self,uri,ext=None):
        if not ext:
            ext = "http://schema.org"
        ext = ext.replace("http://", "https://")
        defn = Element("rdfs:isDefinedBy")
        path = "%s/%s" % (ext,os.path.basename(uri))
        defn.set("rdf:resource",path)
        return defn
        
                

    def outputEnums(self,graph):
        q = """ prefix schema: <http://schema.org/>
        select Distinct ?enum ?parent where{
    		?parent rdfs:subClassOf schema:Enumeration.
            ?enum rdfs:subClassOf ?parent.
        }
        """
        enums = list(graph.query(q))
        log.info("Count %s" % len(enums))
        for row in enums:
            self.outputNamedIndividuals(row.enum,graph,parent=row.parent)
        
    def outputNamedIndividuals(self,idividual,graph,parent=None):
        self.namedCount += 1
        
        typ = SubElement(self.dom,"owl:NamedIndividual")
        typ.set("rdf:about",idividual)
        ext = None
        for (p,o) in graph.predicate_objects(URIRef(idividual)):
            if p == RDFS.label:
                l = SubElement(typ,"rdfs:label")
                l.set("xml:lang","en")
                l.text = o
            elif p == RDFS.comment:
                c = SubElement(typ,"rdfs:comment")
                c.set("xml:lang","en")
                c.text = Markdown.parse(o)
            elif p == URIRef("http://schema.org/isPartOf"):
                ext = str(o)

        typ.append(self.addDefined(idividual,ext))

        if parent:
            s = SubElement(typ,"rdfs:subClassOf")
            s.set("rdf:resource",parent)
 
                
if __name__ == "__main__":
    ex = OwlBuild()
    

    




