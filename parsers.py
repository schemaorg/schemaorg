#!/usr/bin/env python
#

import webapp2
import re
from google.appengine.ext import db
from google.appengine.ext import blobstore
from google.appengine.ext.webapp import blobstore_handlers
import xml.etree.ElementTree as ET
import datetime, time
import logging
import api

def MakeParserOfType (format, webapp):
    if (format == 'mcf') :
        return MCFParser(webapp)
    elif (format == 'rdfa') :
        return RDFAParser(webapp)
    else :
        return 0

class ParseExampleFile :

    def __init__ (self, webapp, layer=""):
        logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
        self.webapp = webapp
        self.layer = layer
        self.file = ""
        self.initFields()

    def initFields(self):
        self.currentStr = []
        self.terms = []
        self.egmeta = {}
        self.egmeta["layer"] = self.layer
        self.egmeta["source"] = self.file
        self.preMarkupStr = ""
        self.microdataStr = ""
        self.rdfaStr = ""
        self.jsonStr = ""
        self.state= ""

    def nextPart(self, next):
        if (self.state == 'PRE-MARKUP:'):
            self.preMarkupStr = "".join(self.currentStr)
        elif (self.state ==  'MICRODATA:'):
            self.microdataStr = "".join(self.currentStr)
        elif (self.state == 'RDFA:'):
            self.rdfaStr = "".join(self.currentStr)
        elif (self.state == 'JSON:'):
            self.jsonStr = "".join(self.currentStr)
        self.state = next
        self.currentStr = []

    def process_example_id(self, m):
        self.egmeta["id"] = m.group(1)
        #logging.debug("Storing ID: %s" % self.egmeta["id"] )
        return ''

    def parse (self, file):
        import codecs
        self.file = file
        egid = re.compile("""#(\S+)\s+""")
        #logging.info("[%s] Reading file %s" % (api.getInstanceId(short=True),file))
        count = 0
        start = datetime.datetime.now()
        
        fd = codecs.open(file, 'r', encoding="utf8")
        content = fd.read()
        fd.close()
        lines = re.split('\n|\r', content)
        
        for line in lines:
            # Per-example sections begin with e.g.: 'TYPES: #music-2 Person, MusicComposition, Organization'
            line = line.rstrip()

            if line.startswith("TYPES:"):
                count += 1
                self.nextPart('TYPES:')
                #logging.debug("About to call api.Example.AddExample with terms: %s " % "".join( [" ; %s " % t.id for t in self.terms] ) )
                #Create example from what has neen previously collected
                #If 1st call there will be no terms which will be regected and no xample created.
                api.Example.AddExample(self.terms, self.preMarkupStr, self.microdataStr, self.rdfaStr, self.jsonStr, self.egmeta)
                self.initFields()
                typelist = re.split(':', line)
                #logging.debug("TYPE INFO: '%s' " % line );
                tdata = egid.sub(self.process_example_id, typelist[1]) # strips IDs, records them in egmeta["id"]
                ttl = tdata.split(',')
                for ttli in ttl:
                    ttli = re.sub(' ', '', ttli)
                    #logging.debug("TTLI: %s " % ttli); # danbri tmp
                    if len(ttli) and "@@" not in ttli:
                        self.terms.append(ttli)
            else:
                tokens = ["PRE-MARKUP:", "MICRODATA:", "RDFA:", "JSON:"]
                for tk in tokens:
                    ltk = len(tk)
                    if line.startswith(tk):
                        self.nextPart(tk)
                        line = line[ltk:]
                if (len(line) > 0):
                    self.currentStr.append(line + "\n")
        self.nextPart('TYPES:') # should flush on each block of examples
        count += 1
        api.Example.AddExample(self.terms, self.preMarkupStr, self.microdataStr, self.rdfaStr, self.jsonStr, self.egmeta) # should flush last one
        #logging.info ("%s [%s] examples in %s" % (count,datetime.datetime.now() - start, file))


class UsageFileParser:

    def __init__ (self, webapp):
        self.webapp = webapp

    def parse (self, contents):
        lines = contents.split('\n')
        for l in lines:
            parts = l.split('\t')
            if (len(parts) == 2):
                unitstr = parts[0].strip()
                count = parts[1]
                api.StoreUsage(unitstr, count)

class RDFAParser :

    def __init__ (self, webapp):
        self.webapp = webapp

    def parse (self, files, layer="core"):
        self.items = {}
        root = []
        for i in range(len(files)):
            logging.debug("RDFa parse schemas in %s " % files[i])
            parser = ET.XMLParser(encoding="utf-8")
            tree = ET.parse(files[i], parser=parser)
            root.append(tree.getroot())

            pre = root[i].findall(".//*[@prefix]")
            for e in range(len(pre)):
                api.Unit.storePrefix(pre[e].get('prefix'))

        for i in range(len(root)):
              self.extractTriples(root[i], None, layer)


        return self.items.keys()

    def stripID (self, str) :
        if (len(str) > 16 and (str[:17] == 'http://schema.org')) :
            return str[18:]
        else:
            return str

    def extractTriples(self, elem, currentNode, layer="core"):
        typeof = elem.get('typeof')
        resource = elem.get('resource')
        href = elem.get('href')
        property = elem.get('property')
        text = elem.text
        if (property != None):
#            if property == "rdf:type":
#              property = "typeOf" # some crude normalization, since we aren't a real rdfa parser.
#              logging.info("normalized rdf:type to typeOf internally. value is: %s" % href )
            property = api.Unit.GetUnit(self.stripID(property), True)
            if (href != None) :
                href = api.Unit.GetUnit(self.stripID(href), True)
           #     self.webapp.write("<br>%s %s %s" % (currentNode, property, href))
                api.Triple.AddTriple(currentNode, property, href, layer)
                self.items[currentNode] = 1
            elif (text != None):
             #   logging.info("<br>%s %s '%s'" % (currentNode, property, text))
                api.Triple.AddTripleText(currentNode, property, text, layer)
                self.items[currentNode] = 1
        if (resource != None):
            currentNode = api.Unit.GetUnit(self.stripID(resource), True)
            if (typeof != None):
                for some_type in typeof.split():
                  # logging.debug("rdfa typeOf: %s" % some_type)
                  api.Triple.AddTriple(currentNode, api.Unit.GetUnit("typeOf", True), api.Unit.GetUnit(self.stripID(some_type), True), layer)
        for child in elem.findall('*'):
            self.extractTriples(child,  currentNode, layer)



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

    def parse (self, content):
        self.items = {}
        lines = re.split('\n|\r', content)
        unit = None
        for l in lines:
            #   self.webapp.write("Got line" + l)
            if (len(l) > 5 and (l[:5] == "Unit:")) :
                unit = api.Unit.GetUnit(self.extractUnitName(l), True)
                self.items[unit] = 1
                #  self.webapp.write("Got unit:" + unit)
            elif (len(l) > 1 and (l.find(':') > 1)) :
                predicate = apiUnit.GetUnit(self.extractPredicateName(l), True)
                values = self.extractValues(l)
                #   self.webapp.write("<br>Got predicate " + predicate)
                for v in values:
                    api.Triple.AddTriple(unit, predicate, api.Unit.GetUnit(v, True))
        return self.items.keys()


