#!/usr/bin/env python
#

import webapp2
import re
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.api import users
from google.appengine.ext.webapp import blobstore_handlers
import logging
import parsers
import headers


# This is the triple store api.
# We have a number of triple sets. Each is from a user / tag combination


# models

NodeIDMap = {}

class Unit ():

    def __init__ (self, id):
        self.id = id
        NodeIDMap[id] = self
        self.arcsIn = []
        self.arcsOut = []
        self.examples = []

    @staticmethod
    def GetUnit (id, createp=False):
        if (id in NodeIDMap):
            return NodeIDMap[id]
        if (createp != False):
            return Unit(id)

    def typeOf(self, type):
        for triple in self.arcsOut:
            if (triple.target != None and triple.arc.id == "typeOf"):
                val = triple.target.subClassOf(type)
                if (val):
                    return True
        return False
            
    def subClassOf(self, type):
        if (self.id == type.id):
            return True
        for triple in self.arcsOut:
            if (triple.target != None and triple.arc.id == "rdfs:subClassOf"):
                val = triple.target.subClassOf(type)
                if (val):
                    return True
        return False

    def isClass(self):
        return self.typeOf(Unit.GetUnit("rdfs:Class"))

    def isAttribute(self):
        return self.typeOf(Unit.GetUnit("rdf:Property"))

    def isEnumeration(self):
        return self.subClassOf(Unit.GetUnit("Enumeration"))

    def isMedicalEnumeration(self):
        return self.subClassOf(Unit.GetUnit("MedicalEnumeration"))

    def superceded(self):
        for triple in self.arcsOut:
            if (triple.target != None and triple.arc.id == "supercededBy"):
                return True
        return False

    def supercedes(self):
        for triple in self.arcsIn:
            if (triple.source != None and triple.arc.id == "supercededBy"):
                return triple.source
        return None


class Triple () :
    
    def __init__ (self, source, arc, target, text):
        self.source = source
        source.arcsOut.append(self)
        self.arc = arc

        if (target != None):
            self.target = target
            self.text = None
            target.arcsIn.append(self)
        elif (text != None):
            self.text = text
            self.target = None

    @staticmethod
    def AddTriple(source, arc, target):
        if (source == None or arc == None or target == None):
            return
        else:
            return Triple(source, arc, target, None)

    @staticmethod
    def AddTripleText(source, arc, text):
        if (source == None or arc == None or text == None):
            return
        else:
            return Triple(source, arc, None, text)

        
class Example ():

    @staticmethod
    def AddExample(terms, original_html, microdata, rdfa, jsonld):
       # todo: fix partial examples: if (len(terms) > 0 and len(original_html) > 0 and (len(microdata) > 0 or len(rdfa) > 0 or len(jsonld) > 0)):
       if (len(terms) > 0 and len(original_html) > 0 and len(microdata) > 0 and len(rdfa) > 0 and len(jsonld) > 0):
            return Example(terms, original_html, microdata, rdfa, jsonld)

    def get(self, name) :
        if name == 'original_html':
           return self.original_html
        if name == 'microdata':
           return self.microdata
        if name == 'rdfa':
           return self.rdfa
        if name == 'jsonld':
           return self.jsonld
    
    def __init__ (self, terms, original_html, microdata, rdfa, jsonld):
        self.terms = terms
        self.original_html = original_html
        self.microdata = microdata
        self.rdfa = rdfa
        self.jsonld = jsonld
        for term in terms:
            term.examples.append(self)



def GetExamples(node):
    return node.examples

def GetTargets(arc, source):
    targets = {}
    for triple in source.arcsOut:
        if (triple.arc == arc):
            if (triple.target != None):
                targets[triple.target] = 1
            elif (triple.text != None):
                targets[triple.text] = 1
    return targets.keys()

def GetSources(arc, target):
    sources = {}
    for triple in target.arcsIn:
        if (triple.arc == arc):
            sources[triple.source] = 1
    return sources.keys()

def GetArcsIn(target):
    arcs = {}
    for triple in target.arcsIn:
        arcs[triple.arc] = 1
    return arcs.keys()

def GetArcsOut(source):
    arcs = {}
    for triple in source.arcsOut:
        arcs[triple.arc] = 1
    return arcs.keys()

def GetComment(node) :    
    for triple in node.arcsOut:
        if (triple.arc.id == 'rdfs:comment'):
            return triple.text
    return "No comment"


PageCache = {}

class ShowUnit (webapp2.RequestHandler) :

    def GetCachedText(self, node):
        global PageCache
        if (node.id in PageCache):
            return PageCache[node.id]
        else:
            return None

    def AddCachedText(self, node, textStrings):
        global PageCache
        outputText = "".join(textStrings)
        PageCache[node.id] = outputText
        return outputText

    def write(self, str):
        self.outputStrings.append(str)

    def GetParentStack(self, node):
        if (node not in self.parentStack):
            self.parentStack.append(node)
        if (Unit.isAttribute(node)):
            self.parentStack.append(Unit.GetUnit("Property"))
            self.parentStack.append(Unit.GetUnit("Thing"))
        else:
            sc = Unit.GetUnit("rdfs:subClassOf")
            for p in GetTargets(sc, node):
                self.GetParentStack(p)

    def ml(self, node):
        return "<a href=\"%s\">%s</a>" % (node.id, node.id)

    def UnitHeaders(self, node):
        self.write("<h1 class=\"page-title\">\n")
        ind = len(self.parentStack)
        thing_seen = False
        while (ind > 0) :
            ind = ind -1
            nn = self.parentStack[ind]
            if (nn.id == "Thing" or thing_seen):
                thing_seen = True
                self.write(self.ml(nn) )
                if (ind > 0):
                    self.write(" &gt; ")
        self.write("</h1>")
        comment = GetComment(node)
        self.write(" <div>%s</div>\n\n" % (comment) + "\n")
        if (node.isClass()):
            self.write("<table class=\"definition-table\">\n        <thead>\n  <tr><th>Property</th><th>Expected Type</th><th>Description</th>               \n  </tr>\n  </thead>\n\n")
			#        elif (node.isAttribute()):

    
    def ClassProperties (self, cl):
        headerPrinted = False 
        di = Unit.GetUnit("domainIncludes")
        ri = Unit.GetUnit("rangeIncludes")
        for prop in sorted(GetSources(di, cl), key=lambda u: u.id):
            if (prop.superceded()):
                continue
            supercedes = prop.supercedes()
            ranges = GetTargets(ri, prop)
            comment = GetComment(prop)
            if (not headerPrinted):
                self.write("<thead class=\"supertype\">\n  <tr>\n    <th class=\"supertype-name\" colspan=\"3\">Properties from %s</th>\n  </tr>\n</thead>\n\n<tbody class=\"supertype\">\n  " % (self.ml(cl)))
                headerPrinted = True

            self.write("<tr>\n    \n      <th class=\"prop-nam\" scope=\"row\">\n\n<code>%s</code>\n    </th>\n " % (self.ml(prop)))
            self.write("<td class=\"prop-ect\">\n")
            first_range = True
            for r in ranges:
                if (not first_range):
                    self.write(" <br/>or ")
                first_range = False
                self.write(self.ml(r))
                self.write("&nbsp;")
            self.write("</td>")
            self.write("<td class=prop-desc>%s" % (comment))
            if (supercedes != None):
                self.write(" Supercedes %s." % (self.ml(supercedes)))

            self.write("</td></tr>")


    def ClassIncomingProperties (self, cl):
        headerPrinted = False 
        di = Unit.GetUnit("domainIncludes")
        ri = Unit.GetUnit("rangeIncludes")
        for prop in sorted(GetSources(ri, cl), key=lambda u: u.id):
            if (prop.superceded()):
                continue
            supercedes = prop.supercedes()
            ranges = GetTargets(di, prop)
            comment = GetComment(prop)
            if (not headerPrinted):
                self.write("<br/><br/>Instances of %s may appear as values for the following properties<br/>" % (self.ml(cl)))
                self.write("<table class=\"definition-table\">\n        \n  \n<thead>\n  <tr><th>Property</th><th>On Types</th><th>Description</th>               \n  </tr>\n</thead>\n\n")

                headerPrinted = True
#            logging.info("Property found %s" % (prop.id))
            self.write("<tr>\n<th class=\"prop-nam\" scope=\"row\">\n <code>%s</code>\n</th>\n " % (self.ml(prop)) + "\n")
            self.write("<td class=\"prop-ect\">\n")
            first_range = True
            for r in ranges:
                if (not first_range):
                    self.write(" <br/>or ")
                first_range = False
                self.write(self.ml(r))
                self.write("&nbsp;")
            self.write("</td>")
            self.write("<td class=prop-desc>%s " % (comment))
            if (supercedes != None):
                self.write(" Supercedes %s." % (self.ml(supercedes)))                
            self.write("</td></tr>")
        if (headerPrinted):
            self.write("</table>\n")


    def AttributeProperties (self, node):
        di = Unit.GetUnit("domainIncludes")
        ri = Unit.GetUnit("rangeIncludes")
        ranges = sorted(GetTargets(ri, node), key=lambda u: u.id)
        domains = sorted(GetTargets(di, node), key=lambda u: u.id)
        first_range = True

        self.write("<table class=\"definition-table\">\n")
        self.write("<thead>\n  <tr>\n    <th>Values expected to be one of these types</th>\n  </tr>\n</thead>\n\n  <tr>\n    <td>\n      ")

        for r in ranges:
            if (not first_range):
                self.write("<br/>")
            first_range = False
            self.write(" <code>%s</code> " % (self.ml(r))+"\n")
        self.write("    </td>\n  </tr>\n</table>\n\n")
        first_domain = True

        self.write("<table class=\"definition-table\">\n")
        self.write("  <thead>\n    <tr>\n      <th>Used on these types</th>\n    </tr>\n</thead>\n<tr>\n  <td>")
        for d in domains:
            if (not first_domain):
                self.write("<br/>")
            first_domain = False
            self.write("\n    <code>%s</code> " % (self.ml(d))+"\n")
        self.write("      </td>\n    </tr>\n</table>\n\n")


    def rep(self, markup):
        m1 = re.sub("<", "&lt;", markup)
        m2 = re.sub(">", "&gt;", m1)
        return m2

    def get(self, node):

        if (node == "favicon.ico"):
            return

        node = Unit.GetUnit(node)

        self.outputStrings = []

        if (node==None):
          self.error(404)
          self.response.out.write('<title>404 Not Found.</title><a href="/">404 Not Found.</a>')
          return

        headers.OutputSchemaorgHeaders(self, entry=node.id)
        cached = self.GetCachedText(node)
        if (cached != None):
            self.response.write(cached)
            return

        self.parentStack = []
        self.GetParentStack(node)

        self.UnitHeaders(node)

        if (Unit.isClass(node)):
            for p in self.parentStack:
                self.ClassProperties(p)
            self.write("</table>\n")
            self.ClassIncomingProperties(node)
        elif (Unit.isAttribute(node)):
            self.AttributeProperties(node)

        if (not Unit.isAttribute(node)):
            self.write("\n\n</table>\n\n") # no supertype table for properties

        if (node.isClass()):
            children = sorted(GetSources(Unit.GetUnit("rdfs:subClassOf"), node), key=lambda u: u.id)
            if (len(children) > 0):
                self.write("<br/><b>More specific Types</b>");
                for c in children:
                    self.write("<li> %s" % (self.ml(c)))
                        
        if (node.isEnumeration() or node.isMedicalEnumeration()):
            children = sorted(GetSources(Unit.GetUnit("typeOf"), node), key=lambda u: u.id)
            if (len(children) > 0):
                self.write("<br/><br/>Enumeration members");
                for c in children:
                    self.write("<li> %s" % (self.ml(c)))

        ackorgs = GetTargets(Unit.GetUnit("dc:source"), node)
        if (len(ackorgs) > 0):
            self.write("<h4  id=\"acks\">Acknowledgements</h4>\n")
            for ao in ackorgs:
                acks = sorted(GetTargets(Unit.GetUnit("rdfs:comment"), ao))
                for ack in acks:
                    self.write(str(ack+"<br/>"))

        examples = GetExamples(node)
        if (len(examples) > 0):
            example_labels = [
              ('Without Markup', 'original_html', 'selected'),
              ('Microdata', 'microdata', ''),
              ('RDFa', 'rdfa', ''),
              ('JSON-LD', 'jsonld', ''),
            ]
            self.write("<br/><br/><b>Examples</b><br/><br/>\n\n")
            for ex in examples:
                self.write("<div class='ds-selector-tabs ds-selector'>\n")
                self.write("  <div class='selectors'>\n")
                for label, example_type, selected in example_labels:
                    self.write("    <a value='%s' data-selects='%s' class='%s'>%s</a>\n"
                               % (example_type, example_type, selected, label))
                self.write("</div>\n\n")
                for label, example_type, selected in example_labels:
                    self.write("<pre class=\"prettyprint lang-html linenums %s %s\">%s</pre>\n\n"
                               % (example_type, selected, self.rep(ex.get(example_type))))
                self.write("</div>\n\n")

        self.write("<p class=\"version\"><b>Schema Version 1.4</b></p>\n\n")
        self.write(" \n\n</div>\n</body>\n</html>")
        
        self.response.write(self.AddCachedText(node, self.outputStrings))


def read_file (filename):
    import os.path    
    folder = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(folder, filename)
    strs = []
    for line in open(file_path, 'r').readlines():
        strs.append(line)
    return "".join(strs)

schemasInitialized = False

def read_schemas():
    import os.path
    global schemasInitialized
    if (not schemasInitialized):
        schema_content = read_file('data/schema.rdfa')
        example_content = read_file('data/examples.txt')
        ft = 'rdfa'
        parser = parsers.MakeParserOfType(ft, None)
        items = parser.parse(schema_content)
        parser = parsers.ParseExampleFile(None)
        parser.parse(example_content)
        schemasInitialized = True

read_schemas()

app = ndb.toplevel(webapp2.WSGIApplication([("/(.*)", ShowUnit)]))



