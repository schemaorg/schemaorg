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

import logging
logging.basicConfig(level=logging.INFO)
log = logging.getLogger(__name__)

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

    def isEnumerationValue(self):
        types = GetTargets(Unit.GetUnit("typeOf"), self  )
        log.debug("isEnumerationValue() called on %s, found %s types." % (self.id, str( len( types ) )) )
        found_enum = False
        for t in types:
          if t.subClassOf(Unit.GetUnit("Enumeration")):
            found_enum = True
        return found_enum

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

    def superproperty(self):
        for triple in self.arcsOut:
            if (triple.target != None and triple.arc.id == "rdfs:subPropertyOf"):
                return triple.target
        return None

    # For rarer case of a property with multiple superproperties.
    def superproperties(self):
        superprops = []
        for triple in self.arcsOut:
            if (triple.target != None and triple.arc.id == "rdfs:subPropertyOf"):
                superprops.append(triple.target)
        return superprops

    # less generally useful, as a property may have several specializations
    def subproperty(self):
        for triple in self.arcsIn:
            if (triple.source != None and triple.arc.id == "rdfs:subPropertyOf"):
               return triple.source
        return None

    # all subproperties of this property
    def subproperties(self):
        subprops = []
        for triple in self.arcsIn:
            if (triple.source != None and triple.arc.id == "rdfs:subPropertyOf"):
              subprops.append(triple.source)
        return subprops

    # For property inverses, e.g. alumni inverseOf alumniOf.
    # Assuming here that they come in simple pairs only.
    def inverseproperty(self):
        for triple in self.arcsOut:
            if (triple.target != None and triple.arc.id == "inverseOf"):
               return triple.target
        for triple in self.arcsIn:
            if (triple.source != None and triple.arc.id == "inverseOf"):
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

    def ml(self, node, label='', title='', prop=''):
        """
        Returns an HTML-formatted link to the class or property URL

        * prop = an optional property value to apply to the A element
        """

        if label=='':
          label = node.id
        if title != '':
          title = " title=\"%s\"" % (title)
        if prop:
            prop = " property=\"%s\"" % (prop)
        return "<a href=\"%s\"%s%s>%s</a>" % (node.id, prop, title, label)

    def makeLinksFromArray(self, nodearray, tooltip=''):
        hyperlinks = []
        for f in nodearray:
           hyperlinks.append(self.ml(f, f.id, tooltip))
        return (", ".join(hyperlinks))

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
                if ind == 1:
                    self.write("<span property=\"rdfs:label\">")
                if ind == 0:
                    self.write("</span>")
        self.write("</h1>")
        comment = GetComment(node)
        self.write(" <div property=\"rdfs:comment\">%s</div>\n\n" % (comment) + "\n")
        if (node.isClass()):
            self.write("<table class=\"definition-table\">\n        <thead>\n  <tr><th>Property</th><th>Expected Type</th><th>Description</th>               \n  </tr>\n  </thead>\n\n")

    def ClassProperties (self, cl, subclass=False):
        headerPrinted = False 
        di = Unit.GetUnit("domainIncludes")
        ri = Unit.GetUnit("rangeIncludes")
        for prop in sorted(GetSources(di, cl), key=lambda u: u.id):
            if (prop.superceded()):
                continue
            supercedes = prop.supercedes()
            inverseprop = prop.inverseproperty()
            subprops = prop.subproperties()
            superprops = prop.superproperties()
            ranges = GetTargets(ri, prop)
            comment = GetComment(prop)
            if (not headerPrinted):
                class_head = self.ml(cl)
                if subclass:
                    class_head = self.ml(cl, prop="rdfs:subClassOf")
                self.write("<thead class=\"supertype\">\n  <tr>\n    <th class=\"supertype-name\" colspan=\"3\">Properties from %s</th>\n  </tr>\n</thead>\n\n<tbody class=\"supertype\">\n  " % (class_head))
                headerPrinted = True

            self.write("<tr typeof=\"rdfs:Property\" resource=\"http://schema.org/%s\">\n    \n      <th class=\"prop-nam\" scope=\"row\">\n\n<code property=\"rdfs:label\">%s</code>\n    </th>\n " % (prop.id, self.ml(prop)))
            self.write("<td class=\"prop-ect\">\n")
            first_range = True
            for r in ranges:
                if (not first_range):
                    self.write(" or <br/> ")
                first_range = False
                self.write(self.ml(r, prop='rangeIncludes'))
                self.write("&nbsp;")
            self.write("</td>")
            self.write("<td class=\"prop-desc\" property=\"rdfs:comment\">%s" % (comment))
            if (supercedes != None):
                self.write(" Supercedes %s." % (self.ml(supercedes)))
            if (inverseprop != None):
                self.write("<br/> Inverse property: %s." % (self.ml(inverseprop)))

            self.write("</td></tr>")
            subclass = False

        if subclass: # in case the superclass has no defined attributes
            self.write("<meta property=\"rdfs:subClassOf\" content=\"%s\">" % (cl.id)) 

    def ClassIncomingProperties (self, cl):
        headerPrinted = False
        di = Unit.GetUnit("domainIncludes")
        ri = Unit.GetUnit("rangeIncludes")
        for prop in sorted(GetSources(ri, cl), key=lambda u: u.id):
            if (prop.superceded()):
                continue
            supercedes = prop.supercedes()
            inverseprop = prop.inverseproperty()
            subprops = prop.subproperties()
            superprops = prop.superproperties()
            ranges = GetTargets(di, prop)
            comment = GetComment(prop)

            if (not headerPrinted):
                self.write("<br/><br/>Instances of %s may appear as values for the following properties<br/>" % (self.ml(cl)))
                self.write("<table class=\"definition-table\">\n        \n  \n<thead>\n  <tr><th>Property</th><th>On Types</th><th>Description</th>               \n  </tr>\n</thead>\n\n")

                headerPrinted = True

            self.write("<tr>\n<th class=\"prop-nam\" scope=\"row\">\n <code>%s</code>\n</th>\n " % (self.ml(prop)) + "\n")
            self.write("<td class=\"prop-ect\">\n")
            first_range = True
            for r in ranges:
                if (not first_range):
                    self.write(" or<br/> ")
                first_range = False
                self.write(self.ml(r))
                self.write("&nbsp;")
            self.write("</td>")
            self.write("<td class=\"prop-desc\">%s " % (comment))
            if (supercedes != None):
                self.write(" Supercedes %s." % (self.ml(supercedes)))
            if (inverseprop != None):
                self.write("<br/> inverse property: %s." % (self.ml(inverseprop)) )

            self.write("</td></tr>")
        if (headerPrinted):
            self.write("</table>\n")


    def AttributeProperties (self, node):
        di = Unit.GetUnit("domainIncludes")
        ri = Unit.GetUnit("rangeIncludes")
        ranges = sorted(GetTargets(ri, node), key=lambda u: u.id)
        domains = sorted(GetTargets(di, node), key=lambda u: u.id)
        first_range = True

        supercedes = node.supercedes()
        inverseprop = node.inverseproperty()
        subprops = node.subproperties()
        superprops = node.superproperties()

        if (inverseprop != None):
            tt = "This means the same thing, but with the relationship direction reversed."
            self.write("<p>Inverse-property: %s.</p>" % (self.ml(inverseprop, inverseprop.id,tt)) )

        self.write("<table class=\"definition-table\">\n")
        self.write("<thead>\n  <tr>\n    <th>Values expected to be one of these types</th>\n  </tr>\n</thead>\n\n  <tr>\n    <td>\n      ")

        for r in ranges:
            if (not first_range):
                self.write("<br/>")
            first_range = False
            tt = "The '%s' property has values that include instances of the '%s' type." % (node.id, r.id)
            self.write(" <code>%s</code> " % (self.ml(r, r.id, tt))+"\n")
        self.write("    </td>\n  </tr>\n</table>\n\n")
        first_domain = True

        self.write("<table class=\"definition-table\">\n")
        self.write("  <thead>\n    <tr>\n      <th>Used on these types</th>\n    </tr>\n</thead>\n<tr>\n  <td>")
        for d in domains:
            if (not first_domain):
                self.write("<br/>")
            first_domain = False
            tt = "The '%s' property is used on the '%s' type." % (node.id, d.id)
            self.write("\n    <code>%s</code> " % (self.ml(d, d.id, tt, prop="domainIncludes"))+"\n")
        self.write("      </td>\n    </tr>\n</table>\n\n")

        if (len(subprops) > 0):
          self.write("<table class=\"definition-table\">\n")
          self.write("  <thead>\n    <tr>\n      <th>Sub-properties</th>\n    </tr>\n</thead>\n")
          for sbp in subprops:
              c = GetComment(sbp)
              tt = "%s: ''%s''" % ( sbp.id, c)
              self.write("\n    <tr><td><code>%s</code></td></tr>\n" % (self.ml(sbp, sbp.id, tt)))
          self.write("\n</table>\n\n")

        if (len(superprops) > 0):
          self.write("<table class=\"definition-table\">\n")
          self.write("  <thead>\n    <tr>\n      <th>Super-properties</th>\n    </tr>\n</thead>\n")
          for spp in superprops:
              c = GetComment(spp)
              tt = "%s: ''%s''" % ( spp.id, c)
              self.write("\n    <tr><td><code>%s</code></td></tr>\n" % (self.ml(spp, spp.id, tt)))
          self.write("\n</table>\n\n")

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

        headers.OutputSchemaorgHeaders(self, node.id, node.isClass())
        cached = self.GetCachedText(node)
        if (cached != None):
            self.response.write(cached)
            return

        self.parentStack = []
        self.GetParentStack(node)

        self.UnitHeaders(node)

        if (node.isClass()):
            subclass = True
            for p in self.parentStack:
                self.ClassProperties(p, p==self.parentStack[0])
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

        if (node.isEnumeration()):
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

        self.write("<p class=\"version\"><b>Schema Version 1.6</b></p>\n\n")
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
