#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import webapp2
import jinja2
import re
from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.api import users
from google.appengine.ext.webapp import blobstore_handlers
import logging
import parsers
import headers
import os

logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)

SCHEMA_VERSION=1.91

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
    extensions=['jinja2.ext.autoescape'], autoescape=True)

ENABLE_JSONLD_CONTEXT = True

# Core API: we have a single schema graph built from triples and units.

NodeIDMap = {}
DataCache = {}

class Unit ():
    """
    Unit represents a node in our schema graph. IDs are local,
    e.g. "Person" or use simple prefixes, e.g. rdfs:Class.
    """

    def __init__ (self, id):
        self.id = id
        NodeIDMap[id] = self
        self.arcsIn = []
        self.arcsOut = []
        self.examples = []
        self.subtypes = None

    @staticmethod
    def GetUnit (id, createp=False):
        """Return a Unit representing a node in the schema graph.

        Argument:
        createp -- should we create node if we don't find it? (default: False)
        """
        if (id in NodeIDMap):
            return NodeIDMap[id]
        if (createp != False):
            return Unit(id)

    def typeOf(self, type):
        """Boolean, true if the unit has an rdf:type matching this type."""
        for triple in self.arcsOut:
            if (triple.target != None and triple.arc.id == "typeOf"):
                val = triple.target.subClassOf(type)
                if (val):
                    return True
        return False

    def subClassOf(self, type):
        """Boolean, true if the unit has an rdfs:subClassOf matching this type."""
        if (self.id == type.id):
            return True
        for triple in self.arcsOut:
            if (triple.target != None and triple.arc.id == "rdfs:subClassOf"):
                val = triple.target.subClassOf(type)
                if (val):
                    return True
        return False

    def isClass(self):
        """Does this unit represent a class/type?"""
        return self.typeOf(Unit.GetUnit("rdfs:Class"))

    def isAttribute(self):
        """Does this unit represent an attribute/property?"""
        return self.typeOf(Unit.GetUnit("rdf:Property"))

    def isEnumeration(self):
        """Does this unit represent an enumerated type?"""
        return self.subClassOf(Unit.GetUnit("Enumeration"))

    def isEnumerationValue(self):
        """Does this unit represent a member of an enumerated type?"""
        types = GetTargets(Unit.GetUnit("typeOf"), self  )
        log.debug("isEnumerationValue() called on %s, found %s types." % (self.id, str( len( types ) )) )
        found_enum = False
        for t in types:
          if t.subClassOf(Unit.GetUnit("Enumeration")):
            found_enum = True
        return found_enum

    def isDataType(self):
      """
      Does this unit represent a DataType type or sub-type?

      DataType and its children do not descend from Thing, so we need to
      treat it specially.
      """
      return self.subClassOf(Unit.GetUnit("DataType"))

    @staticmethod
    def storePrefix(prefix):
        """Stores the prefix declaration for a given class or property"""
        # Currently defined just to let the tests pass
        pass

    def superseded(self):
        """Has this property been superseded? (i.e. deprecated/archaic)"""
        for triple in self.arcsOut:
            if (triple.target != None and triple.arc.id == "supersededBy"):
                return True
        return False

    def supersedes(self):
        """Returns a property (assume max 1) that is supersededBy this one, or nothing."""
        for triple in self.arcsIn:
            if (triple.source != None and triple.arc.id == "supersededBy"):
                return triple.source
        return None
        # TODO: supersedes is a list, e.g. 'seller' supersedes 'vendor', 'merchant'

    def supersedes_all(self):
        """Returns a property (assume max 1) that is supersededBy this one, or nothing."""
        newer = []
        for triple in self.arcsIn:
            if (triple.source != None and triple.arc.id == "supersededBy"):
                newer.append(triple.source)
        return newer

    def supersededBy(self):
        """Returns a property (assume max 1) that supersededs this one, or nothing."""
        for p in sorted(GetSources(Unit.GetUnit("typeOf"), Unit.GetUnit("rdf:Property")), key=lambda u: u.id):
            allnewers = GetTargets(Unit.GetUnit("supersededBy"), p)
            for newerprop in allnewers:
                if self in newerprop.supersedes_all():
                    return newerprop # this is one of possibly many properties that supersedes self.
        return None

    def superproperties(self):
        """Returns super-properties of this one."""
        if not self.isAttribute():
          logging.debug("Non-property %s won't have superproperties." % self.id)
        superprops = []
        for triple in self.arcsOut:
            if (triple.target != None and triple.arc.id == "rdfs:subPropertyOf"):
                superprops.append(triple.target)
        return superprops

    def subproperties(self):
        """Returns direct subproperties of this property."""
        if not self.isAttribute():
          logging.debug("Non-property %s won't have subproperties." % self.id)
          return None
        subprops = []
        for triple in self.arcsIn:
            if (triple.source != None and triple.arc.id == "rdfs:subPropertyOf"):
              subprops.append(triple.source)
        return subprops

    def inverseproperty(self):
        """A property that is an inverseOf this one, e.g. alumni vs alumniOf."""
        for triple in self.arcsOut:
            if (triple.target != None and triple.arc.id == "inverseOf"):
               return triple.target
        for triple in self.arcsIn:
            if (triple.source != None and triple.arc.id == "inverseOf"):
               return triple.source
        return None

class Triple ():
    """Triple represents an edge in the graph: source, arc and target/text."""
    def __init__ (self, source, arc, target, text):
        """Triple constructor keeps state via source node's arcsOut."""
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
        """AddTriple stores a thing-valued new Triple within source Unit."""
        if (source == None or arc == None or target == None):
            return
        else:
            return Triple(source, arc, target, None)

    @staticmethod
    def AddTripleText(source, arc, text):
        """AddTriple stores a string-valued new Triple within source Unit."""
        if (source == None or arc == None or text == None):
            return
        else:
            return Triple(source, arc, None, text)

def GetTargets(arc, source):
    """All values for a specified arc on specified graph node."""
    targets = {}
    for triple in source.arcsOut:
        if (triple.arc == arc):
            if (triple.target != None):
                targets[triple.target] = 1
            elif (triple.text != None):
                targets[triple.text] = 1
    return targets.keys()

def GetSources(arc, target):
    """All source nodes for a specified arc pointing to a specified node."""
    sources = {}
    for triple in target.arcsIn:
        if (triple.arc == arc):
            sources[triple.source] = 1
    return sources.keys()

def GetArcsIn(target):
    """All incoming arc types for this specified node."""
    arcs = {}
    for triple in target.arcsIn:
        arcs[triple.arc] = 1
    return arcs.keys()

def GetArcsOut(source):
    """All outgoing arc types for this specified node."""
    arcs = {}
    for triple in source.arcsOut:
        arcs[triple.arc] = 1
    return arcs.keys()

# Utility API

def GetComment(node) :
    """Get the first rdfs:comment we find on this node (or "No comment")."""
    for triple in node.arcsOut:
        if (triple.arc.id == 'rdfs:comment'):
            return triple.text
    return "No comment"

def GetImmediateSubtypes(n):
    """Get this type's immediate subtypes, i.e. that are subClassOf this."""
    if n==None:
        return None
    subs = GetSources( Unit.GetUnit("rdfs:subClassOf"), n)
    return subs

def GetImmediateSupertypes(n):
    """Get this type's immediate supertypes, i.e. that we are subClassOf."""
    if n==None:
        return None
    return GetTargets( Unit.GetUnit("rdfs:subClassOf"), n)

def GetAllTypes():
    """Return all types in the graph."""
    if DataCache.get('AllTypes'):
        logging.debug("DataCache HIT: Alltypes")
        return DataCache.get('AllTypes')
    else:
        logging.debug("DataCache MISS: Alltypes")
        mynode = Unit.GetUnit("Thing")
        subbed = {}
        todo = [mynode]
        while todo:
            current = todo.pop()
            subs = GetImmediateSubtypes(current)
            subbed[current] = 1
            for sc in subs:
                if subbed.get(sc.id) == None:
                    todo.append(sc)
        DataCache['AllTypes'] = subbed.keys()
        return subbed.keys()

def GetParentList(start_unit, end_unit=None, path=[]):

        """
        Returns one or more lists, each giving a path from a start unit to a supertype parent unit.

        example:

        for path in GetParentList( Unit.GetUnit("Restaurant") ):
            pprint.pprint(', '.join([str(x.id) for x in path ]))

        'Restaurant, FoodEstablishment, LocalBusiness, Organization, Thing'
        'Restaurant, FoodEstablishment, LocalBusiness, Place, Thing'
        """

        if not end_unit:
          end_unit = Unit.GetUnit("Thing")

        arc=Unit.GetUnit("rdfs:subClassOf")
        logging.debug("from %s to %s - path length %d" % (start_unit.id, end_unit.id, len(path) ) )
        path = path + [start_unit]
        if start_unit == end_unit:
            return [path]
        if not Unit.GetUnit(start_unit.id):
            return []
        paths = []
        for node in GetTargets(arc, start_unit):
            if node not in path:
                newpaths = GetParentList(node, end_unit, path)
                for newpath in newpaths:
                    paths.append(newpath)
        return paths

def HasMultipleBaseTypes(typenode):
    """True if this unit represents a type with more than one immediate supertype."""
    return len( GetTargets( Unit.GetUnit("rdfs:subClassOf"), typenode ) ) > 1

class Example ():

    @staticmethod
    def AddExample(terms, original_html, microdata, rdfa, jsonld):
       """
       Add an Example (via constructor registering it with the terms that it
       mentions, i.e. stored in term.examples).
       """
       # todo: fix partial examples: if (len(terms) > 0 and len(original_html) > 0 and (len(microdata) > 0 or len(rdfa) > 0 or len(jsonld) > 0)):
       if (len(terms) > 0 and len(original_html) > 0 and len(microdata) > 0 and len(rdfa) > 0 and len(jsonld) > 0):
            return Example(terms, original_html, microdata, rdfa, jsonld)

    def get(self, name) :
        """Exposes original_content, microdata, rdfa and jsonld versions."""
        if name == 'original_html':
           return self.original_html
        if name == 'microdata':
           return self.microdata
        if name == 'rdfa':
           return self.rdfa
        if name == 'jsonld':
           return self.jsonld

    def __init__ (self, terms, original_html, microdata, rdfa, jsonld):
        """Example constructor, registers itself with the relevant Unit(s)."""
        self.terms = terms
        self.original_html = original_html
        self.microdata = microdata
        self.rdfa = rdfa
        self.jsonld = jsonld
        for term in terms:
            term.examples.append(self)



def GetExamples(node):
    """Returns the examples (if any) for some Unit node."""
    return node.examples

def GetExtMappingsRDFa(node):
    """Self-contained chunk of RDFa HTML markup with mappings for this term."""
    if (node.isClass()):
        equivs = GetTargets(Unit.GetUnit("owl:equivalentClass"), node)
        if len(equivs) > 0:
            markup = ''
            for c in equivs:

                if (c.id.startswith('http')):
                  markup = markup + "<link property=\"owl:equivalentClass\" href=\"%s\"/>\n" % c.id
                else:
                  markup = markup + "<link property=\"owl:equivalentClass\" resource=\"%s\"/>\n" % c.id

            return markup
    if (node.isAttribute()):
        equivs = GetTargets(Unit.GetUnit("owl:equivalentProperty"), node)
        if len(equivs) > 0:
            markup = ''
            for c in equivs:
                markup = markup + "<link property=\"owl:equivalentProperty\" href=\"%s\"/>\n" % c.id
            return markup
    return "<!-- no external mappings noted for this term. -->"

def GetJsonLdContext():
    """Generates a basic JSON-LD context file for schema.org."""
    jsonldcontext = "{\n    \"@context\":    {\n"
    jsonldcontext += "        \"@vocab\": \"http://schema.org/\",\n"

    url = Unit.GetUnit("URL")
    date = Unit.GetUnit("Date")
    datetime = Unit.GetUnit("DateTime")

    properties = sorted(GetSources(Unit.GetUnit("typeOf"), Unit.GetUnit("rdf:Property")), key=lambda u: u.id)
    for p in properties:
        range = GetTargets(Unit.GetUnit("rangeIncludes"), p)
        type = None

        if url in range:
            type = "@id"
        elif date in range:
            type = "Date"
        elif datetime in range:
            type = "DateTime"

        if type:
            jsonldcontext += "        \"" + p.id + "\": { \"@type\": \"" + type + "\" },"

    jsonldcontext += "}}\n"
    jsonldcontext = jsonldcontext.replace("},}}","}\n    }\n}")
    jsonldcontext = jsonldcontext.replace("},","},\n")

    return jsonldcontext

PageCache = {}

class ShowUnit (webapp2.RequestHandler):
    """ShowUnit exposes schema.org terms via Web RequestHandler
    (HTML/HTTP etc.).
    """
    def emitCacheHeaders(self):
        """Send cache-related headers via HTTP."""
        self.response.headers['Cache-Control'] = "public, max-age=43200" # 12h
        self.response.headers['Vary'] = "Accept, Accept-Encoding"

    def GetCachedText(self, node):
        """Return page text from node.id cache (if found, otherwise None)."""
        global PageCache
        if (node.id in PageCache):
            return PageCache[node.id]
        else:
            return None

    def AddCachedText(self, node, textStrings):
        """Cache text of our page for this node via its node.id.

        We can be passed a text string or an array of text strings.
        """
        global PageCache
        outputText = "".join(textStrings)
        log.debug("CACHING: %s" % node.id)
        PageCache[node.id] = outputText
        return outputText

    def write(self, str):
        """Write some text to Web server's output stream."""
        self.outputStrings.append(str)

    def GetParentStack(self, node):
        """Returns a hiearchical structured used for site breadcrumbs."""
        if (node not in self.parentStack):
            self.parentStack.append(node)

        if (Unit.isAttribute(node)):
            self.parentStack.append(Unit.GetUnit("Property"))
            self.parentStack.append(Unit.GetUnit("Thing"))

        sc = Unit.GetUnit("rdfs:subClassOf")
        if GetTargets(sc, node):
            for p in GetTargets(sc, node):
                self.GetParentStack(p)
        else:
            # Enumerations are classes that have no declared subclasses
            sc = Unit.GetUnit("typeOf")
            for p in GetTargets(sc, node):
                self.GetParentStack(p)

    def ml(self, node, label='', title='', prop=''):
        """ml ('make link')
        Returns an HTML-formatted link to the class or property URL

        * label = optional anchor text label for the link
        * title = optional title attribute on the link
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
        """Make a comma separate list of links via ml() function.

        * tooltip - optional text to use as title of all links
        """
        hyperlinks = []
        for f in nodearray:
           hyperlinks.append(self.ml(f, f.id, tooltip))
        return (", ".join(hyperlinks))

    def UnitHeaders(self, node):
        """Write out the HTML page headers for this node."""
        self.write("<h1 class=\"page-title\">\n")
        ind = len(self.parentStack)
        thing_seen = False
        while (ind > 0) :
            ind = ind -1
            nn = self.parentStack[ind]
            if (nn.id == "Thing" or thing_seen or nn.isDataType()):
                thing_seen = True
                self.write(self.ml(nn) )
                if ind == 1 and node.isEnumerationValue():
                    self.write(" :: ")
                elif ind > 0:
                    self.write(" &gt; ")
                if ind == 1:
                    self.write("<span property=\"rdfs:label\">")
                if ind == 0:
                    self.write("</span>")
        self.write("</h1>")
        comment = GetComment(node)
        self.write(" <div property=\"rdfs:comment\">%s</div>\n\n" % (comment) + "\n")
        if (node.isClass() and not node.isDataType()):
            self.write("<table class=\"definition-table\">\n        <thead>\n  <tr><th>Property</th><th>Expected Type</th><th>Description</th>               \n  </tr>\n  </thead>\n\n")

    def ClassProperties (self, cl, subclass=False):
        """Write out a table of properties for a per-type page."""
        headerPrinted = False
        di = Unit.GetUnit("domainIncludes")
        ri = Unit.GetUnit("rangeIncludes")
        for prop in sorted(GetSources(di, cl), key=lambda u: u.id):
            if (prop.superseded()):
                continue
            supersedes = prop.supersedes()
            olderprops = prop.supersedes_all()
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
            if (len(olderprops) > 0):
                olderlinks = ", ".join([self.ml(o) for o in olderprops])
                self.write(" Supersedes %s." % olderlinks )
            if (inverseprop != None):
                self.write("<br/> Inverse property: %s." % (self.ml(inverseprop)))

            self.write("</td></tr>")
            subclass = False

        if subclass: # in case the superclass has no defined attributes
            self.write("<meta property=\"rdfs:subClassOf\" content=\"%s\">" % (cl.id))

    def ClassIncomingProperties (self, cl):
        """Write out a table of incoming properties for a per-type page."""
        headerPrinted = False
        di = Unit.GetUnit("domainIncludes")
        ri = Unit.GetUnit("rangeIncludes")
        for prop in sorted(GetSources(ri, cl), key=lambda u: u.id):
            if (prop.superseded()):
                continue
            supersedes = prop.supersedes()
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
            if (supersedes != None):
                self.write(" Supersedes %s." % (self.ml(supersedes)))
            if (inverseprop != None):
                self.write("<br/> inverse property: %s." % (self.ml(inverseprop)) )

            self.write("</td></tr>")
        if (headerPrinted):
            self.write("</table>\n")


    def AttributeProperties (self, node):
        """Write out properties of this property, for a per-property page."""
        di = Unit.GetUnit("domainIncludes")
        ri = Unit.GetUnit("rangeIncludes")
        ranges = sorted(GetTargets(ri, node), key=lambda u: u.id)
        domains = sorted(GetTargets(di, node), key=lambda u: u.id)
        first_range = True

        newerprop = node.supersededBy() # None of one. e.g. we're on 'seller'(new) page, we get 'vendor'(old)
        olderprop = node.supersedes() # None or one
        olderprops = node.supersedes_all() # list, e.g. 'seller' has 'vendor', 'merchant'.

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

        # Super-properties
        if (len(superprops) > 0):
            self.write("<table class=\"definition-table\">\n")
            self.write("  <thead>\n    <tr>\n      <th>Super-properties</th>\n    </tr>\n</thead>\n")
            for spp in superprops:
                c = GetComment(spp)           # markup needs to be stripped from c, e.g. see 'logo', 'photo'
                c = re.sub(r'<[^>]*>', '', c) # This is not a sanitizer, we trust our input.
                tt = "%s: ''%s''" % ( spp.id, c) 
                self.write("\n    <tr><td><code>%s</code></td></tr>\n" % (self.ml(spp, spp.id, tt)))
            self.write("\n</table>\n\n")

        # Supersedes
        if (len(olderprops) > 0):
            self.write("<table class=\"definition-table\">\n")
            self.write("  <thead>\n    <tr>\n      <th>Supersedes</th>\n    </tr>\n</thead>\n")

            for o in olderprops:
                c = GetComment(o)
                tt = "%s: ''%s''" % ( o.id, c)
                self.write("\n    <tr><td><code>%s</code></td></tr>\n" % (self.ml(o, o.id, tt)))
            self.write("\n</table>\n\n")

        # supersededBy (at most one direct successor)
        if (newerprop != None):
            self.write("<table class=\"definition-table\">\n")
            self.write("  <thead>\n    <tr>\n      <th><a href=\"/supersededBy\">supersededBy</a></th>\n    </tr>\n</thead>\n")
            self.write("\n    <tr><td><code>%s</code></td></tr>\n" % (self.ml(newerprop, newerprop.id, tt)))
            self.write("\n</table>\n\n")

    def rep(self, markup):
        """Replace < and > with HTML escape chars."""
        m1 = re.sub("<", "&lt;", markup)
        m2 = re.sub(">", "&gt;", m1)
        # TODO: Ampersand? Check usage with examples.
        return m2

    def getHomepage(self, node):
        """Send the homepage, or if no HTML accept header received and JSON-LD was requested, send JSON-LD context file.

        typical browser accept list: ('Accept', 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8')
        # e.g. curl -H "Accept: application/ld+json" http://localhost:8080/
        see also http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html
        https://github.com/rvguha/schemaorg/issues/5
        https://github.com/rvguha/schemaorg/wiki/JsonLd
        """
        accept_header = self.request.headers.get('Accept').split(',')
        logging.info("accepts: %s" % self.request.headers.get('Accept'))
        if ENABLE_JSONLD_CONTEXT:
            jsonldcontext = GetJsonLdContext() # consider memcached?

        mimereq = {}
        for ah in accept_header:
            ah = re.sub( r";q=\d?\.\d+", '', ah).rstrip()
            mimereq[ah] = 1

        html_score = mimereq.get('text/html', 5)
        xhtml_score = mimereq.get('application/xhtml+xml', 5)
        jsonld_score = mimereq.get('application/ld+json', 10)
        # print "accept_header: " + str(accept_header) + " mimereq: "+str(mimereq) + "Scores H:{0} XH:{1} J:{2} ".format(html_score,xhtml_score,jsonld_score)

        if (ENABLE_JSONLD_CONTEXT and (jsonld_score < html_score and jsonld_score < xhtml_score)):
            self.response.headers['Content-Type'] = "application/ld+json"
            self.emitCacheHeaders()
            self.response.out.write( jsonldcontext )
            return
        else:
            self.response.out.write( open("static/index.html", 'r').read() )
            return

    def getExactTermPage(self, node):
        """Emit a Web page that exactly matches this node."""
        self.outputStrings = []

        ext_mappings = GetExtMappingsRDFa(node)

        headers.OutputSchemaorgHeaders(self, node.id, node.isClass(), ext_mappings)
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

        self.write("<p class=\"version\"><b>Schema Version %s</b></p>\n\n" % SCHEMA_VERSION)


        # Analytics
	self.write("""<script>(function(i,s,o,g,r,a,m){i['GoogleAnalyticsObject']=r;i[r]=i[r]||function(){
	  (i[r].q=i[r].q||[]).push(arguments)},i[r].l=1*new Date();a=s.createElement(o),
	  m=s.getElementsByTagName(o)[0];a.async=1;a.src=g;m.parentNode.insertBefore(a,m)
	  })(window,document,'script','//www.google-analytics.com/analytics.js','ga');
	  ga('create', 'UA-52672119-1', 'auto');ga('send', 'pageview');</script>""")

        self.write(" \n\n</div>\n</body>\n</html>")

        self.response.write(self.AddCachedText(node, self.outputStrings))

    def get(self, node):
        """Get a schema.org site page generated for this node/term.

        Web content is written directly via self.response.

        CORS enabled all URLs - we assume site entirely public.
        See http://en.wikipedia.org/wiki/Cross-origin_resource_sharing

        These should give a JSON version of schema.org:

            curl --verbose -H "Accept: application/ld+json" http://localhost:8080/docs/jsonldcontext.json
            curl --verbose -H "Accept: application/ld+json" http://localhost:8080/docs/jsonldcontext.json.txt
            curl --verbose -H "Accept: application/ld+json" http://localhost:8080/

        Per-term pages vary for type, property and enumeration.

        Last resort is a 404 error if we do not exactly match a term's id.


        See also https://webapp-improved.appspot.com/guide/request.html#guide-request
        """

        self.response.headers.add_header("Access-Control-Allow-Origin", "*") # entire site is public.

#        TODO: redirections - https://github.com/rvguha/schemaorg/issues/4
#        or https://webapp-improved.appspot.com/guide/routing.html?highlight=redirection
#
#        if str(self.request.host).startswith("www.schema.org"):
#            log.debug("www.schema.org requested. We should redirect to use schema.org as hostname, not " + self.request.host)
#            origURL = self.request.url
#            origURL.replace("https://", "http://")
#            origURL.replace("//www.schema.org", "//schema.org")
#            self.redirect(newURL, permanent=True)

        # First: fixed paths: homepage, favicon.ico and generated JSON-LD files.
        #
        if (node == "" or node=="/"):
            self.getHomepage(node)
            return

        if ENABLE_JSONLD_CONTEXT:
            if (node=="docs/jsonldcontext.json.txt"):
                jsonldcontext = GetJsonLdContext()
                self.response.headers['Content-Type'] = "text/plain"
                self.emitCacheHeaders()
                self.response.out.write( jsonldcontext )
                return
            if (node=="docs/jsonldcontext.json"):
                jsonldcontext = GetJsonLdContext()
                self.response.headers['Content-Type'] = "application/ld+json"
                self.emitCacheHeaders()
                self.response.out.write( jsonldcontext )
                return

        if (node == "favicon.ico"):
            return

        # Next: pages based on request path matching a Unit in the term graph.
        node = Unit.GetUnit(node) # e.g. "Person", "CreativeWork".

        # TODO:
        # - handle http vs https; www.schema.org vs schema.org
        # - handle foo-input Action pseudo-properties
        # - handle /Person/Minister -style extensions

        if (node != None):
            self.getExactTermPage(node)
            return
        else:
          self.error(404)
          self.response.out.write('<title>404 Not Found.</title><a href="/">404 Not Found.</a><br/><br/>')
          return

def read_file (filename):
    """Read a file from disk, return it as a single string."""
    strs = []

    file_path = full_path(filename)

    import codecs
    log.info("READING FILE: filename=%s file_path=%s " % (filename, file_path ) )
    for line in codecs.open(file_path, 'r', encoding="utf8").readlines():
        strs.append(line)
    return "".join(strs)

def full_path(filename):
    """convert local file name to full path."""
    import os.path
    folder = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(folder, filename)


schemasInitialized = False

def read_schemas():
    """Read/parse/ingest schemas from data/*.rdfa. Also alsodata/*examples.txt"""
    import os.path
    import glob
    global schemasInitialized
    if (not schemasInitialized):
        files = glob.glob("data/*.rdfa")
        file_paths = []
        for f in files:
            file_paths.append(full_path(f))

        parser = parsers.MakeParserOfType('rdfa', None)
        items = parser.parse(file_paths)

        files = glob.glob("data/*examples.txt")
        example_contents = []
        for f in files:
            example_content = read_file(f)
            example_contents.append(example_content)
        parser = parsers.ParseExampleFile(None)
        parser.parse(example_contents)
        schemasInitialized = True

read_schemas()

app = ndb.toplevel(webapp2.WSGIApplication([("/(.*)", ShowUnit)]))
