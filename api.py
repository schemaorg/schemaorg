#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import re
import webapp2
import jinja2
import logging

import parsers

from google.appengine.ext import ndb
from google.appengine.ext import blobstore
from google.appengine.api import users
from google.appengine.ext.webapp import blobstore_handlers


logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)

schemasInitialized = False
SCHEMA_VERSION=1.999999
sitename = "schema.org"
sitemode = "mainsite" # whitespaced list for CSS tags,
            # e.g. "mainsite testsite", "extensionsite" when off expected domains

DYNALOAD = True # permits read_schemas to be re-invoked live.
JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
    extensions=['jinja2.ext.autoescape'], autoescape=True)

debugging = False

# Core API: we have a single schema graph built from triples and units.

NodeIDMap = {}
DataCache = {}
ext_re = re.compile(r'([^\w,])+')
all_layers = {}
all_terms = {}

# Utility declaration of W3C Initial Context
# From http://www.w3.org/2011/rdfa-context/rdfa-1.1
# and http://www.w3.org/2013/json-ld-context/rdfa11
# Enables all these prefixes without explicit declaration when
# using schema.org's JSON-LD context file.
#
namespaces = """        "cat": "http://www.w3.org/ns/dcat#",
        "qb": "http://purl.org/linked-data/cube#",
        "org": "http://www.w3.org/ns/org#",
        "grddl": "http://www.w3.org/2003/g/data-view#",
        "ma": "http://www.w3.org/ns/ma-ont#",
        "owl": "http://www.w3.org/2002/07/owl#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfa": "http://www.w3.org/ns/rdfa#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "rif": "http://www.w3.org/2007/rif#",
        "rr": "http://www.w3.org/ns/r2rml#",
        "skos": "http://www.w3.org/2004/02/skos/core#",
        "skosxl": "http://www.w3.org/2008/05/skos-xl#",
        "wdr": "http://www.w3.org/2007/05/powder#",
        "void": "http://rdfs.org/ns/void#",
        "wdrs": "http://www.w3.org/2007/05/powder-s#",
        "xhv": "http://www.w3.org/1999/xhtml/vocab#",
        "xml": "http://www.w3.org/XML/1998/namespace",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
        "prov": "http://www.w3.org/ns/prov#",
        "sd": "http://www.w3.org/ns/sparql-service-description#",
        "org": "http://www.w3.org/ns/org#",
        "gldp": "http://www.w3.org/ns/people#",
        "cnt": "http://www.w3.org/2008/content#",
        "dcat": "http://www.w3.org/ns/dcat#",
        "earl": "http://www.w3.org/ns/earl#",
        "ht": "http://www.w3.org/2006/http#",
        "ptr": "http://www.w3.org/2009/pointers#",
        "cc": "http://creativecommons.org/ns#",
        "ctag": "http://commontag.org/ns#",
        "dc": "http://purl.org/dc/terms/",
        "dcterms": "http://purl.org/dc/terms/",
        "foaf": "http://xmlns.com/foaf/0.1/",
        "gr": "http://purl.org/goodrelations/v1#",
        "ical": "http://www.w3.org/2002/12/cal/icaltzd#",
        "og": "http://ogp.me/ns#",
        "rev": "http://purl.org/stuff/rev#",
        "sioc": "http://rdfs.org/sioc/ns#",
        "v": "http://rdf.data-vocabulary.org/#",
        "vcard": "http://www.w3.org/2006/vcard/ns#",
        "schema": "http://schema.org/",
        "describedby": "http://www.w3.org/2007/05/powder-s#describedby",
        "license": "http://www.w3.org/1999/xhtml/vocab#license",
        "role": "http://www.w3.org/1999/xhtml/vocab#role",
"""

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
        self.usage = 0
        self.subtypes = None

    def GetImmediateSubtypes(self, layers='core'):
      return GetImmediateSubtypes(self, layers=layers)

    def setUsage(self, count):
        self.usage = count

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

    def typeOf(self, type,  layers='core'):
        """Boolean, true if the unit has an rdf:type matching this type."""
        types = GetTargets( Unit.GetUnit("typeOf"), self, layers )
        return (type in types)


    def OLDsubClassOf(self, type, layers='core'):
        """Boolean, true if the unit has an rdfs:subClassOf matching this type."""
        if (self.id == type.id):
            return True
        for triple in self.arcsOut:
            if (triple.target != None and triple.arc.id == "rdfs:subClassOf"):
                val = triple.target.subClassOf(type)
                if (val):
                    return True
        return False


    # Function needs rewriting to use GetTargets(arc,src,layers) and recurse
    def subClassOf(self, type, layers='core'):
        """Boolean, true if the unit has an rdfs:subClassOf matching this type, direct or implied (in specified layer(s))."""
        if (self.id == type.id):
            return True
        parents = GetTargets( Unit.GetUnit("rdfs:subClassOf"), self, layers )
        if type in parents:
            return True
        else:
            for p in parents:
                if p.subClassOf(type, layers):
                     return True
        return False

    def directInstanceOf(self, type, layers='core'):
        """Boolean, true if the unit has a direct typeOf (aka rdf:type) property matching this type, direct or implied (in specified layer(s))."""
        mytypes = GetTargets( Unit.GetUnit("typeOf"), self, layers )
        if type in mytypes:
            return True
        return False # TODO: consider an API for implied types too?

    def isClass(self, layers='core'):
        """Does this unit represent a class/type?"""
        return self.typeOf(Unit.GetUnit("rdfs:Class"), layers=layers)

    def isAttribute(self, layers='core'):
        """Does this unit represent an attribute/property?"""
        return self.typeOf(Unit.GetUnit("rdf:Property"), layers=layers)

    def isEnumeration(self, layers='core'):
        """Does this unit represent an enumerated type?"""
        return self.subClassOf(Unit.GetUnit("Enumeration"), layers=layers)

    def isEnumerationValue(self, layers='core'):
        """Does this unit represent a member of an enumerated type?"""
        types = GetTargets(Unit.GetUnit("typeOf"), self , layers=layers)
        log.debug("isEnumerationValue() called on %s, found %s types. layers: %s" % (self.id, str( len( types ) ), layers ) )
        found_enum = False
        for t in types:
          if t.subClassOf(Unit.GetUnit("Enumeration"), layers=layers):
            found_enum = True
        return found_enum

    def isDataType(self, layers='core'):
      """
      Does this unit represent a DataType type or sub-type?

      DataType and its children do not descend from Thing, so we need to
      treat it specially.
      """
      return self.directInstanceOf(Unit.GetUnit("DataType"), layers=layers)

    @staticmethod
    def storePrefix(prefix):
        """Stores the prefix declaration for a given class or property"""
        # Currently defined just to let the tests pass
        pass

    # e.g. <http://schema.org/actors> <http://schema.org/supersededBy> <http://schema.org/actor> .

    def superseded(self, layers='core'):
        """Has this property been superseded? (i.e. deprecated/archaic), in any of these layers."""
        supersededBy_values = GetTargets( Unit.GetUnit("supersededBy"), self, layers )
        return ( len(supersededBy_values) > 0)

    def supersedes(self, layers='core'):
        """Returns a property (assume max 1) that is supersededBy this one, or nothing."""
        olderterms = GetSources( Unit.GetUnit("supersededBy"), self, layers )
        if len(olderterms) > 0:
            return olderterms[0]
        else:
            return None

    def supersedes_all(self, layers='core'):
        """Returns terms that is supersededBy by this later one, or nothing. (in this layer)"""
        return(GetSources( Unit.GetUnit("supersededBy"), self, layers ))
        # so we want sources of arcs pointing here with 'supersededBy'
        # e.g. vendor supersededBy seller ; returns newer 'seller' for earlier 'vendor'.

    def supersededBy(self, layers='core'):
        """Returns a property (assume max 1) that supersededs this one, or nothing."""
        newerterms = GetTargets( Unit.GetUnit("supersededBy"), self, layers )
        if len(newerterms)>0:
            return newerterms.pop()
        else:
            return None

    def OLDsupersededBy(self, layers='core'):
        """Returns a property (assume max 1) that supersededs this one, or nothing."""
        for p in sorted(GetSources(Unit.GetUnit("typeOf"), Unit.GetUnit("rdf:Property"), layers), key=lambda u: u.id):
            allnewers = GetTargets(Unit.GetUnit("supersededBy"), p, layers)
            for newerprop in allnewers:
                if self in newerprop.supersedes_all(layers=layers):
                    return newerprop # this is one of possibly many properties that supersedes self.
        return None

    def superproperties(self, layers='core'):
        """Returns super-properties of this one."""
        if not self.isAttribute():
          logging.debug("Non-property %s won't have subproperties." % self.id)
          return None
        superprops = GetTargets(Unit.GetUnit("rdfs:subPropertyOf"),self, layers=layers )
        return superprops

    def subproperties(self, layers='core'):
        """Returns direct subproperties of this property."""
        if not self.isAttribute():
          logging.debug("Non-property %s won't have subproperties." % self.id)
          return None
        subprops = GetSources(Unit.GetUnit("rdfs:subPropertyOf"),self, layers=layers )
        return subprops

    def inverseproperty(self, layers="core"):
        """A property that is an inverseOf this one, e.g. alumni vs alumniOf."""
        a = GetTargets(Unit.GetUnit("inverseOf"), self, layers=layers)
        b = GetSources(Unit.GetUnit("inverseOf"), self, layers=layers)
        if len(a)>0:
            return a.pop()
        else:
            if len(b) > 0:
                return b.pop()
            else:
                return None

        for triple in self.arcsOut:
            if (triple.target != None and triple.arc.id == "inverseOf"):
               return triple.target
        for triple in self.arcsIn:
            if (triple.source != None and triple.arc.id == "inverseOf"):
               return triple.source
        return None

    def UsageStr (self) :
        str = self.usage
        if (str == '1') :
            return "Between 10 and 100 domains"
        elif (str == '2'):
            return "Between 100 and 1000 domains"
        elif (str == '3'):
            return "Between 1000 and 10,000 domains"
        elif (str == '4'):
            return "Between 10,000 and 50,000 domains"
        elif (str == '5'):
            return "Between 50,000 and 100,000 domains"
        elif (str == '7'):
            return "Between 100,000 and 250,000 domains"
        elif (str == '8'):
            return "Between 250,000 and 500,000 domains"
        elif (str == '9'):
            return "Between 500,000 and 1,000,000 domains"
        elif (str == '10'):
            return "Over 1,000,000 domains"
        else:
            return "Fewer than 10 domains"

# NOTE: each Triple is in exactly one layer, by default 'core'. When we
# read_schemas() from data/ext/{x}/*.rdfa each schema triple is given a
# layer named "x". Access to triples can default to layer="core" or take
# a custom layer or layers, e.g. layers="bib", or layers=["bib", "foo"].
# This is verbose but at least explicit. If we move towards making better
# use of external templates for site generation we could reorganize.
# For now e.g. 'grep GetSources api.py| grep -v layer' and
# 'grep GetTargets api.py| grep -v layer' etc. can check for non-layered usage.
#
# Units, on the other hand, are layer-independent. For now we have only a
# crude inLayer(layerlist, unit) API to check which layers mention a term.

class Triple ():
    """Triple represents an edge in the graph: source, arc and target/text."""
    def __init__ (self, source, arc, target, text, layer='core'):
        """Triple constructor keeps state via source node's arcsOut."""
        self.source = source
        source.arcsOut.append(self)
        self.arc = arc
        self.layer = layer

        if (target != None):
            self.target = target
            self.text = None
            target.arcsIn.append(self)
        elif (text != None):
            self.text = text
            self.target = None

    @staticmethod
    def AddTriple(source, arc, target, layer='core'):
        """AddTriple stores a thing-valued new Triple within source Unit."""

        if (source == None or arc == None or target == None):
            return
        else:

            # for any term mentioned as subject or object, we register the layer
            # TODO: make this into a function
            x = all_terms.get(source.id) # subjects
            if x is None:
                x = []
            if layer not in x:
                x.append(layer)
            all_terms[source.id]= x

            x = all_terms.get(target.id) # objects
            if x is None:
                x = []
            if layer not in x:
                x.append(layer)
            all_terms[target.id]= x

            return Triple(source, arc, target, None, layer)

    @staticmethod
    def AddTripleText(source, arc, text, layer='core'):
        """AddTriple stores a string-valued new Triple within source Unit."""
        if (source == None or arc == None or text == None):
            return
        else:
            return Triple(source, arc, None, text, layer)

def GetTargets(arc, source, layers='core'):
    """All values for a specified arc on specified graph node (within any of the specified layers)."""
    # log.debug("GetTargets checking in layer: %s for unit: %s arc: %s" % (layers, source.id, arc.id))
    targets = {}
    for triple in source.arcsOut:
        if (triple.arc == arc):
            if (triple.target != None and triple.layer in layers):
                targets[triple.target] = 1
            elif (triple.text != None and triple.layer in layers):
                targets[triple.text] = 1
    return targets.keys()

def GetSources(arc, target, layers='core'):
    """All source nodes for a specified arc pointing to a specified node (within any of the specified layers)."""
    log.debug("GetSources checking in layer: %s for unit: %s arc: %s" % (layers, target.id, arc.id))
    sources = {}
    for triple in target.arcsIn:
        if (triple.arc == arc and triple.layer in layers):
            sources[triple.source] = 1
    return sources.keys()

def GetArcsIn(target, layers='core'):
    """All incoming arc types for this specified node (within any of the specified layers)."""
    arcs = {}
    for triple in target.arcsIn:
        if triple.layer in layers:
            arcs[triple.arc] = 1
    return arcs.keys()

def GetArcsOut(source,  layers='core'):
    """All outgoing arc types for this specified node."""
    arcs = {}
    for triple in source.arcsOut:
        if triple.layer in layers:
            arcs[triple.arc] = 1
    return arcs.keys()

# Utility API

def GetComment(node, layers='core') :
    """Get the first rdfs:comment we find on this node (or "No comment"), within any of the specified layers."""
    tx = GetTargets(Unit.GetUnit("rdfs:comment"), node, layers=layers )
    if len(tx) > 0:
            return tx[0]
    else:
        return "No comment"

def GetImmediateSubtypes(n, layers='core'):
    """Get this type's immediate subtypes, i.e. that are subClassOf this."""
    if n==None:
        return None
    subs = GetSources( Unit.GetUnit("rdfs:subClassOf"), n, layers=layers)
    subs.sort(key=lambda x: x.id)
    return subs

def GetImmediateSupertypes(n, layers='core'):
    """Get this type's immediate supertypes, i.e. that we are subClassOf."""
    if n==None:
        return None
    return GetTargets( Unit.GetUnit("rdfs:subClassOf"), n, layers=layer)

def GetAllTypes(layers='core'):
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
            subs = GetImmediateSubtypes(current, layers=layers)
            subbed[current] = 1
            for sc in subs:
                if subbed.get(sc.id) == None:
                    todo.append(sc)
        DataCache['AllTypes'] = subbed.keys()
        return subbed.keys()

def GetParentList(start_unit, end_unit=None, path=[], layers='core'):

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
        for node in GetTargets(arc, start_unit, layers=layers):
            if node not in path:
                newpaths = GetParentList(node, end_unit, path, layers=layers)
                for newpath in newpaths:
                    paths.append(newpath)
        return paths

def HasMultipleBaseTypes(typenode, layers='core'):
    """True if this unit represents a type with more than one immediate supertype."""
    return len( GetTargets( Unit.GetUnit("rdfs:subClassOf"), typenode, layers ) ) > 1

class TypeHierarchyTree:

    def __init__(self):
        self.txt = ""
        self.visited = {}

    def emit(self, s):
        self.txt += s + "\n"

    def toHTML(self):
        return '<ul>%s</ul>' % self.txt

    def toJSON(self):
        return self.txt

    def traverseForHTML(self, node, depth = 1, layers='core'):

        # we are a supertype of some kind
        if len(node.GetImmediateSubtypes(layers=layers)) > 0:

            # and we haven't been here before
            if node.id not in self.visited:
                self.visited[node.id] = True # remember our visit
                self.emit( ' %s<li class="tbranch" id="%s"><a href="/%s">%s</a>' % (" " * 4 * depth, node.id, node.id, node.id) )
                self.emit(' %s<ul>' % (" " * 4 * depth))

                # handle our subtypes
                for item in node.GetImmediateSubtypes(layers=layers):
                    self.traverseForHTML(item, depth + 1, layers=layers)
                self.emit( ' %s</ul>' % (" " * 4 * depth))
            else:
                # we are a supertype but we visited this type before, e.g. saw Restaurant via Place then via Organization
                seen = '  <a href="#%s">*</a> ' % node.id
                self.emit( ' %s<li class="tbranch" id="%s"><a href="/%s">%s</a>%s' % (" " * 4 * depth, node.id, node.id, node.id, seen) )

        # leaf nodes
        if len(node.GetImmediateSubtypes(layers=layers)) == 0:
            if node.id not in self.visited:
                self.emit( '%s<li class="tleaf" id="%s"><a href="/%s">%s</a>%s' % (" " * depth, node.id, node.id, node.id, "" ))
            #else:
                #self.visited[node.id] = True # never...
                # we tolerate "VideoGame" appearing under both Game and SoftwareApplication
                # and would only suppress it if it had its own subtypes. Seems legit.

        self.emit( ' %s</li>' % (" " * 4 * depth) )

    # based on http://danbri.org/2013/SchemaD3/examples/4063550/hackathon-schema.js  - thanks @gregg, @sandro
    def traverseForJSONLD(self, node, depth = 0, last_at_this_level = True, supertype="None", layers='core'):
        emit_debug = False
        if node.id in self.visited:
            # self.emit("skipping %s - already visited" % node.id)
            return
        self.visited[node.id] = True
        p1 = " " * 4 * depth
        if emit_debug:
            self.emit("%s# @id: %s last_at_this_level: %s" % (p1, node.id, last_at_this_level))
        global namespaces;
        ctx = "{}".format(""""@context": {
    "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
    "schema": "http://schema.org/",
    "rdfs:subClassOf": { "@type": "@id" },
    "name": "rdfs:label",
    "description": "rdfs:comment",
    "children": { "@reverse": "rdfs:subClassOf" }
  },\n""" if last_at_this_level and depth==0 else '' )

        unseen_subtypes = []
        for st in node.GetImmediateSubtypes(layers=layers):
            if not st.id in self.visited:
                unseen_subtypes.append(st)
        unvisited_subtype_count = len(unseen_subtypes)
        subtype_count = len( node.GetImmediateSubtypes(layers=layers) )

        supertx = "{}".format( '"rdfs:subClassOf": "schema:%s", ' % supertype.id if supertype != "None" else '' )
        maybe_comma = "{}".format("," if unvisited_subtype_count > 0 else "")
        comment = GetComment(node, layers).strip()
        comment = comment.replace('"',"'")
        comment = re.sub('<[^<]+?>', '', comment)[:60]

        self.emit('\n%s{\n%s\n%s"@type": "rdfs:Class", %s "description": "%s...",\n%s"name": "%s",\n%s"@id": "schema:%s"%s'
                  % (p1, ctx, p1,                 supertx,            comment,     p1,   node.id, p1,        node.id,  maybe_comma))

        i = 1
        if unvisited_subtype_count > 0:
            self.emit('%s"children": ' % p1 )
            self.emit("  %s["  % p1 )
            inner_lastness = False
            for t in unseen_subtypes:
                if emit_debug:
                    self.emit("%s  # In %s > %s i: %s unvisited_subtype_count: %s" %(p1, node.id, t.id, i, unvisited_subtype_count))
                if i == unvisited_subtype_count:
                    inner_lastness = True
                i = i + 1
                self.traverseForJSONLD(t, depth + 1, inner_lastness, supertype=node, layers=layers)

            self.emit("%s  ]%s" % (p1,  "{}".format( "" if not last_at_this_level else '' ) ) )

        maybe_comma = "{}".format( ',' if not last_at_this_level else '' )
        self.emit('\n%s}%s\n' % (p1, maybe_comma))


class Example ():

    @staticmethod
    def AddExample(terms, original_html, microdata, rdfa, jsonld, egmeta, layer='core'):
       """
       Add an Example (via constructor registering it with the terms that it
       mentions, i.e. stored in term.examples).
       """
       # todo: fix partial examples: if (len(terms) > 0 and len(original_html) > 0 and (len(microdata) > 0 or len(rdfa) > 0 or len(jsonld) > 0)):
       if (len(terms) > 0 and len(original_html) > 0 and len(microdata) > 0 and len(rdfa) > 0 and len(jsonld) > 0):
            return Example(terms, original_html, microdata, rdfa, jsonld, egmeta, layer='core')

    def get(self, name, layers='core') :
        """Exposes original_content, microdata, rdfa and jsonld versions (in the layer(s) specified)."""
        if name == 'original_html':
           return self.original_html
        if name == 'microdata':
           return self.microdata
        if name == 'rdfa':
           return self.rdfa
        if name == 'jsonld':
           return self.jsonld

    def __init__ (self, terms, original_html, microdata, rdfa, jsonld, egmeta, layer='core'):
        """Example constructor, registers itself with the relevant Unit(s)."""
        self.terms = terms
        self.original_html = original_html
        self.microdata = microdata
        self.rdfa = rdfa
        self.jsonld = jsonld
        self.egmeta = egmeta
        self.layer = layer
        for term in terms:
            if "id" in egmeta:
              logging.debug("Created Example with ID %s and type %s" % ( egmeta["id"], term.id ))
            term.examples.append(self)



def GetExamples(node, layers='core'):
    """Returns the examples (if any) for some Unit node."""
    return node.examples

def GetExtMappingsRDFa(node, layers='core'):
    """Self-contained chunk of RDFa HTML markup with mappings for this term."""
    if (node.isClass()):
        equivs = GetTargets(Unit.GetUnit("owl:equivalentClass"), node, layers=layers)
        if len(equivs) > 0:
            markup = ''
            for c in equivs:

                if (c.id.startswith('http')):
                  markup = markup + "<link property=\"owl:equivalentClass\" href=\"%s\"/>\n" % c.id
                else:
                  markup = markup + "<link property=\"owl:equivalentClass\" resource=\"%s\"/>\n" % c.id

            return markup
    if (node.isAttribute()):
        equivs = GetTargets(Unit.GetUnit("owl:equivalentProperty"), node, layers)
        if len(equivs) > 0:
            markup = ''
            for c in equivs:
                markup = markup + "<link property=\"owl:equivalentProperty\" href=\"%s\"/>\n" % c.id
            return markup
    return "<!-- no external mappings noted for this term. -->"

def GetJsonLdContext(layers='core'):
    """Generates a basic JSON-LD context file for schema.org."""
    global namespaces;
    jsonldcontext = "{\"@context\":    {\n"
    jsonldcontext += namespaces ;
    jsonldcontext += "        \"@vocab\": \"http://schema.org/\",\n"

    url = Unit.GetUnit("URL")
    date = Unit.GetUnit("Date")
    datetime = Unit.GetUnit("DateTime")

    properties = sorted(GetSources(Unit.GetUnit("typeOf"), Unit.GetUnit("rdf:Property"), layers=layers), key=lambda u: u.id)
    for p in properties:
        range = GetTargets(Unit.GetUnit("rangeIncludes"), p, layers=layers)
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






#### UTILITIES


def inLayer(layerlist, node):
    """Does a unit get its type mentioned in a layer?"""
    if (node is None):
        return False
    log.debug("Looking in %s for %s" % (layerlist, node.id ))
    if len(GetTargets(Unit.GetUnit("typeOf"), node, layers=layerlist) ) > 0:
        log.debug("Found typeOf for node %s in layers: %s"  % (node.id, layerlist ))
        return True
    if len(GetTargets(Unit.GetUnit("rdfs:subClassOf"), node, layers=layerlist) ) > 0:
        log.info("Found rdfs:subClassOf")
    # TODO: should we really test for any mention of a term, not just typing?
        return True
    log.debug("inLayer: Failed to find in %s for %s" % (layerlist, node.id))
    return False

def read_file (filename):
    """Read a file from disk, return it as a single string."""
    strs = []

    file_path = full_path(filename)

    import codecs
    log.debug("READING FILE: filename=%s file_path=%s " % (filename, file_path ) )
    for line in codecs.open(file_path, 'r', encoding="utf8").readlines():
        strs.append(line)
    return "".join(strs)

def full_path(filename):
    """convert local file name to full path."""
    import os.path
    folder = os.path.dirname(os.path.realpath(__file__))
    return os.path.join(folder, filename)



def read_schemas(loadExtensions=False):
    """Read/parse/ingest schemas from data/*.rdfa. Also data/*examples.txt"""
    import os.path
    import glob
    import re

    global schemasInitialized
    if (not schemasInitialized or DYNALOAD):
        log.info("(re)loading core and annotations.")
        files = glob.glob("data/*.rdfa")
        file_paths = []
        for f in files:
            file_paths.append(full_path(f))
        parser = parsers.MakeParserOfType('rdfa', None)
        items = parser.parse(file_paths, "core")

        if loadExtensions:
            log.info("(re)scanning for extensions.")
            extfiles = glob.glob("data/ext/*/*.rdfa")
            log.info("Extensions found: %s ." % " , ".join(extfiles) )
            fnstrip_re = re.compile("\/.*")
            for ext in extfiles:
                ext_file_path = full_path(ext)
                extid = ext.replace('data/ext/', '')
                extid = re.sub(fnstrip_re,'',extid)
                log.info("Preparing to parse extension data: %s as '%s'" % (ext_file_path, "%s" % extid))
                parser = parsers.MakeParserOfType('rdfa', None)
                all_layers[extid] = "1"
                extitems = parser.parse([ext_file_path], layer="%s" % extid) # put schema triples in a layer
                # log.debug("Results: %s " % len( extitems) )
                for x in extitems:
                    if x is not None:
                        log.debug("%s:%s" % ( extid, str(x.id) ))
                # e.g. see 'data/ext/bib/bibdemo.rdfa'

        files = glob.glob("data/*examples.txt")
        example_contents = []
        for f in files:
            example_content = read_file(f)
            example_contents.append(example_content)
        parser = parsers.ParseExampleFile(None)
        parser.parse(example_contents)

        files = glob.glob("data/2015-04-vocab_counts.txt")

        for file in files:
            usage_data = read_file(file)
            parser = parsers.UsageFileParser(None)
            parser.parse(usage_data)
        schemasInitialized = True
