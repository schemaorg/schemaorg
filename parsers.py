#!/usr/bin/env python
#

import webapp2
import re
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import xml.etree.ElementTree as ET
import logging


def MakeParserOfType (format, webapp):
    if (format == 'mcf') :
        return MCFParser(webapp)
    elif (format == 'rdfa') :
        return RDFAParser(webapp) 
    else :
        return 0


class RDFAParser :

    def __init__ (self, webapp):
        self.webapp = webapp

    def parse (self, content, tripleSet):
        root = ET.fromstring(content)
        self.items = {}
        self.extractTriples(root, tripleSet, None)
        return self.items.keys()

    def stripID (self, str) :
        if (len(str) > 16 and (str[:17] == 'http://schema.org')) :
            return str[18:]
        else:
            return str
        
    def extractTriples(self, elem, tripleSet, currentNode):
        typeof = elem.get('typeof')
        resource = elem.get('resource')
        href = elem.get('href')
        property = elem.get('property')
        text = elem.text
        if (property != None):
            property = self.stripID(property)
            if (href != None) :
                href = self.stripID(href)
           #     self.webapp.write("<br>%s %s %s" % (currentNode, property, href))
                tripleSet.AddTriple(currentNode, property, href)
                self.items[currentNode] = 1
            elif (text != None):
             #   logging.info("<br>%s %s '%s'" % (currentNode, property, text))
                tripleSet.AddTripleText(currentNode, property, text)
                self.items[currentNode] = 1
        if (resource != None):
            currentNode = self.stripID(resource)
        for child in elem.findall('*'):
            self.extractTriples(child, tripleSet, currentNode)


                
class MCFParser:


    def __init__ (self, webapp):
        self.webapp = webapp

    def extractUnitName (self, line):
        parts = re.split(':', line)
        name = parts[1]
        return re.sub(' ', '', name)

    def extractPredicateName (self, line):
        parts = re.split(':', line)
        return parts[0]

    def cleanValue (self, value) :
        if (value.find('"') > -1):
            parts = re.split('"', value)
            return parts[1]
        else:
            return re.sub(' ', '', value)

    def extractValues (self, line):
        parts = re.split(':', line)
        raw_values = re.split(',', parts[1])
        values = []
        for rv in raw_values:
            values.append(self.cleanValue(rv))
        return values

    def parse (self, content, tripleSet):
        self.items = {}
        lines = re.split('\n|\r', content)
        unit = None
        for l in lines:
            #   self.webapp.write("Got line" + l)
            if (len(l) > 5 and (l[:5] == "Unit:")) :
                unit = self.extractUnitName(l)
                self.items[unit] = 1
                #  self.webapp.write("Got unit:" + unit)
            elif (len(l) > 1 and (l.find(':') > 1)) :
                predicate = self.extractPredicateName(l)
                values = self.extractValues(l)
                #   self.webapp.write("<br>Got predicate " + predicate)
                for v in values:
#                    self.webapp.write("<br> %s %s %s" % (unit, predicate, v))
                    tripleSet.AddTriple(unit, predicate, v)
        return self.items.keys()
