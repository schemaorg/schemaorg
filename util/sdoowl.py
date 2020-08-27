#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
import os
for path in [os.getcwd(),"Util","SchemaPages","SchemaExamples"]:
  sys.path.insert( 1, path ) #Pickup libs from local  directories
  
import glob
import re

import rdflib
from rdflib import Graph
from rdflib.term import URIRef, Literal
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from rdflib.plugins.sparql import prepareQuery
from rdflib.compare import graph_diff
from rdflib.namespace import RDFS, RDF

from xml.etree import ElementTree as ET
from xml.dom import minidom
from xml.etree.ElementTree import Element, SubElement, Comment, tostring

from buildsitepages import *
from sdotermsource import SdoTermSource 
from sdoterm import *
from localmarkdown import Markdown

VOCABURI = SdoTermSource.vocabUri()

NAMESPACES = {
    "xml:base": VOCABURI,
    "xmlns": VOCABURI,
    "xmlns:schema": VOCABURI,
    "xmlns:rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    "xmlns:rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "xmlns:owl": "http://www.w3.org/2002/07/owl#",
    "xmlns:dcterms": "http://purl.org/dc/terms/",
    "xmlns:xsd": "http://www.w3.org/2001/XMLSchema#"
}

from rdflib.term import URIRef
DOMAININC = URIRef(VOCABURI + "domainIncludes")
RANGEINC = URIRef(VOCABURI + "rangeIncludes")
INVERSEOF = URIRef(VOCABURI + "inverseOf")
SUPERSEDEDBY = URIRef(VOCABURI + "supersededBy")
DEFAULTRANGES = [VOCABURI + "Text",VOCABURI + "URL",VOCABURI + "Role"]
DATATYPES = [VOCABURI + "Boolean",
            VOCABURI + "Date",
            VOCABURI + "DateTime",
            VOCABURI + "Number",
            VOCABURI + "Float",
            VOCABURI + "Integer",
            VOCABURI + "Time"]

class OwlBuild():
    def __init__(self):
        self.typesCount = self.propsCount = self.namedCount = 0
        self.createDom()
        self.loadGraph()

    def getContent(self):
        #return ET.tostring(self.dom)
        return self.prettify(self.dom).decode()

    def prettify(self,elem):
        # log.info("doc: %s" % ET.tostring(elem))
        doc = minidom.parseString(ET.tostring(elem))
        return doc.toprettyxml(encoding='UTF-8')


    def createDom(self):
        self.dom = Element('rdf:RDF')
        for (k,v) in NAMESPACES.items():
            self.dom.set(k,v)
        
        self.dom.append(Comment("\n\tGenerated from Schema.org version: %s released: %s\n\t" % (getVersion(),getVersionDate(getVersion()))))
        self.ont = SubElement(self.dom,"owl:Ontology")
        self.ont.set("rdf:about",VOCABURI)
        info = SubElement(self.ont,"owl:versionInfo")
        info.set("rdf:datatype","http://www.w3.org/2001/XMLSchema#string")
        info.text = getVersion()
        x = SubElement(self.ont,"rdfs:label")
        x.text = "Schema.org Vocabulary"
        x = SubElement(self.ont,"dcterms:modified")
        x.set("rdf:datatype", "http://www.w3.org/2001/XMLSchema#dat")
        x.text = getVersionDate(getVersion())
        self.dom.append(Comment("\n\t/////////////////////\n\t/ Definitions\n\t/////////////////////\n\n\t"))

    def loadGraph(self):
        self.list(SdoTermSource.sourceGraph())

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
        self.outputNamedIndividuals(VOCABURI + "True",graph)    
        self.outputNamedIndividuals(VOCABURI + "False",graph)    

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
            elif p == URIRef(VOCABURI + "isPartOf"): #Defined in an extension
                ext = str(o)
            elif p == RDF.type and o == URIRef(VOCABURI + "DataType"): #A datatype
                s = SubElement(typ,"rdfs:subClassOf")
                s.set("rdf:resource",VOCABURI + "DataType")
        
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
            elif p == URIRef(VOCABURI + "isPartOf"):
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
            elif p == URIRef(VOCABURI + "isPartOf"):
                ext = str(o)

        typ.append(self.addDefined(idividual,ext))

        if parent:
            s = SubElement(typ,"rdfs:subClassOf")
            s.set("rdf:resource",parent)
 
