#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import sys
import os

if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(os.EX_CONFIG)

import glob
import re

for path in [os.getcwd(),"software/util","software/SchemaTerms","software/SchemaExamples"]:
  sys.path.insert( 1, path ) #Pickup libs from local  directories


import rdflib
from rdflib import Graph
from rdflib.term import URIRef, Literal
from rdflib.parser import Parser
from rdflib.serializer import Serializer
from rdflib.plugins.sparql import prepareQuery
from rdflib.compare import graph_diff
from rdflib.namespace import RDFS, RDF

from xml.etree import ElementTree
from xml.dom import minidom

from sdotermsource import SdoTermSource
from sdoterm import *
from localmarkdown import Markdown

import schemaversion

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
DEFAULTRANGES = frozenset([VOCABURI + "Text", VOCABURI + "URL", VOCABURI + "Role"])
DATATYPES = frozenset([VOCABURI + "Boolean",
            VOCABURI + "Date",
            VOCABURI + "DateTime",
            VOCABURI + "Number",
            VOCABURI + "Float",
            VOCABURI + "Integer",
            VOCABURI + "Time"])

def _MakePrettyComment(text):
  """Make a pretty comment with a box of slashes before and after."""
  inner_text = '/ ' + text
  bar = '/' * len(inner_text)
  comment = '\n\t' + bar + '\n\t' + inner_text + '\n\t' + bar + '\n\n\t'
  return ElementTree.Comment(comment)


class OwlBuild():
    def __init__(self):
        self.typesCount = self.propsCount = self.namedCount = 0
        self._createDom()
        self._loadGraph()

    def _createDom(self):
        self.dom = ElementTree.Element('rdf:RDF')
        for (k,v) in NAMESPACES.items():
            self.dom.set(k,v)

        version = schemaversion.getVersion()
        version_date = schemaversion.getCurrentVersionDate()
        comment_text = "Generated from Schema.org version: %s released: %s" % (version, version_date)
        self.dom.append(_MakePrettyComment(text=comment_text))
        self.ont = ElementTree.SubElement(self.dom,"owl:Ontology")
        self.ont.set("rdf:about",VOCABURI)
        info = ElementTree.SubElement(self.ont,"owl:versionInfo")
        info.set("rdf:datatype","http://www.w3.org/2001/XMLSchema#string")
        info.text = version
        x = ElementTree.SubElement(self.ont,"rdfs:label")
        x.text = "Schema.org Vocabulary"
        x = ElementTree.SubElement(self.ont,"dcterms:modified")
        x.set("rdf:datatype", "http://www.w3.org/2001/XMLSchema#date")
        x.text = version_date
        self.dom.append(_MakePrettyComment(text='Definitions'))

    def _loadGraph(self):
        self.list(SdoTermSource.sourceGraph())

    def getContent(self):
        return self.prettify(self.dom).decode()

    def prettify(self,elem):
        doc = minidom.parseString(ElementTree.tostring(elem))
        return doc.toprettyxml(encoding='UTF-8')

    def list(self, graph):
        types = {}
        props = {}
        exts = []
        self.dom.append(_MakePrettyComment(text='Class Definitions'))

        for s, p, o in graph.triples((None,RDF.type,RDFS.Class)):
            if s.startswith("https://schema.org"):
                types.update({s:graph.identifier})

        for t in sorted(types.keys()):
            self.outputType(t,graph)

        self.dom.append(_MakePrettyComment(text='Property Definitions'))
        for s, p, o in graph.triples((None,RDF.type,RDF.Property)):
            if s.startswith("https://schema.org"):
                props.update({s:graph.identifier})

        for p in sorted(props.keys()):
            self.outputProp(p,graph)

        self.dom.append(_MakePrettyComment(text='Named Individuals Definitions'))

        self.outputEnums(graph)
        self.outputNamedIndividuals(VOCABURI + "True",graph)
        self.outputNamedIndividuals(VOCABURI + "False",graph)

    def outputType(self, uri, graph):
        self.typesCount += 1

        typ = ElementTree.SubElement(self.dom,"owl:Class")
        typ.set("rdf:about",uri)
        ext = None
        for (p,o) in graph.predicate_objects(uri):
            if p == RDFS.label:
                l = ElementTree.SubElement(typ,"rdfs:label")
                l.set("xml:lang","en")
                l.text = o
            elif p == RDFS.comment:
                c = ElementTree.SubElement(typ,"rdfs:comment")
                c.set("xml:lang","en")
                c.text = Markdown.parse(o)
            elif p == RDFS.subClassOf:
                s = ElementTree.SubElement(typ,"rdfs:subClassOf")
                s.set("rdf:resource",o)
            elif p == URIRef(VOCABURI + "isPartOf"): #Defined in an extension
                ext = str(o)
            elif p == RDF.type and o == URIRef(VOCABURI + "DataType"): #A datatype
                s = ElementTree.SubElement(typ,"rdfs:subClassOf")
                s.set("rdf:resource",VOCABURI + "DataType")

        typ.append(self.addDefined(uri,ext))

    def outputProp(self,uri, graph):
        self.propsCount += 1
        children = []
        domains = {}
        ranges = []
        datatypeonly = True
        ext = None
        for p, o in graph.predicate_objects(uri):
            if p == RDFS.label:
                l = ElementTree.Element("rdfs:label")
                l.set("xml:lang","en")
                l.text = o
                children.append(l)
            elif p == RDFS.comment:
                c = ElementTree.Element("rdfs:comment")
                c.set("xml:lang","en")
                c.text = Markdown.parse(o)
                children.append(c)
            elif p == RDFS.subPropertyOf:
                sub = ElementTree.Element("rdfs:subPropertyOf")
                subval = str(o)
                if subval == "rdf:type":  #Fixes a special case with schema:additionalType
                    subval = "http://www.w3.org/1999/02/22-rdf-syntax-ns#type"

                sub.set("rdf:resource",subval)
                children.append(sub)
            elif p == INVERSEOF:
                sub = ElementTree.Element("owl:inverseOf")
                sub.set("rdf:resource",o)
                children.append(sub)
            elif p == SUPERSEDEDBY:
                sub = ElementTree.Element("schema:supersededBy")
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
            d = ElementTree.Element("rdfs:domain")
            children.append(d)
            cl = ElementTree.SubElement(d,"owl:Class")
            u = ElementTree.SubElement(cl,"owl:unionOf")
            u.set("rdf:parseType","Collection")
            for target in domains.keys():
                targ = ElementTree.SubElement(u,"owl:Class")
                targ.set("rdf:about",target)

        if len(ranges):
            r = ElementTree.Element("rdfs:range")
            children.append(r)
            cl = ElementTree.SubElement(r,"owl:Class")
            u = ElementTree.SubElement(cl,"owl:unionOf")
            u.set("rdf:parseType","Collection")
            for target in ranges:
                targ = ElementTree.SubElement(u,"owl:Class")
                targ.set("rdf:about",target)


        if datatypeonly:
            prop = ElementTree.SubElement(self.dom,"owl:DatatypeProperty")
        else:
            prop = ElementTree.SubElement(self.dom,"owl:ObjectProperty")
        prop.set("rdf:about",uri)
        for sub in children:
            prop.append(sub)

    def addDefined(self,uri,ext=None):
        if not ext:
            ext = "https://schema.org"
        ext = ext.replace("http://", "https://")
        defn = ElementTree.Element("rdfs:isDefinedBy")
        path = os.path.join(ext, os.path.basename(uri))
        defn.set("rdf:resource", path)
        return defn

    def outputEnums(self,graph):
        q = """ prefix schema: <https://schema.org/>
        select Distinct ?enum ?parent where{
        ?parent rdfs:subClassOf schema:Enumeration.
            ?enum rdfs:subClassOf ?parent.
        }
        """
        enums = list(graph.query(q))
        for row in enums:
            self.outputNamedIndividuals(row.enum,graph,parent=row.parent)

    def outputNamedIndividuals(self,individual,graph,parent=None):
        self.namedCount += 1

        typ = ElementTree.SubElement(self.dom,"owl:NamedIndividual")
        typ.set("rdf:about",individual)
        ext = None
        for (p,o) in graph.predicate_objects(URIRef(individual)):
            if p == RDFS.label:
                l = ElementTree.SubElement(typ,"rdfs:label")
                l.set("xml:lang","en")
                l.text = o
            elif p == RDFS.comment:
                c = ElementTree.SubElement(typ,"rdfs:comment")
                c.set("xml:lang","en")
                c.text = Markdown.parse(o)
            elif p == URIRef(VOCABURI + "isPartOf"):
                ext = str(o)

        typ.append(self.addDefined(individual,ext))

        if parent:
            s = ElementTree.SubElement(typ,"rdfs:subClassOf")
            s.set("rdf:resource",parent)

