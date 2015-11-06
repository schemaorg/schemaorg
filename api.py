#!/usr/bin/env python
# -*- coding: UTF-8 -*-

import os
import re
#import webapp2
#import jinja2 # used for templates
import logging

import parsers

#from google.appengine.ext import ndb
#from google.appengine.ext import blobstore
#from google.appengine.api import users
#from google.appengine.ext.webapp import blobstore_handlers


logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)

schemasInitialized = False
extensionsLoaded = False
extensionLoadErrors = ""

EVERYLAYER = "!EVERYLAYER!"
sitename = "schema.org"
sitemode = "mainsite" # whitespaced list for CSS tags,
            # e.g. "mainsite testsite", "extensionsite" when off expected domains

DYNALOAD = True # permits read_schemas to be re-invoked live.
#JINJA_ENVIRONMENT = jinja2.Environment(
#   loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
#    extensions=['jinja2.ext.autoescape'], autoescape=True)

debugging = False

# Core API: we have a single schema graph built from triples and units.

NodeIDMap = {}
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


class DataCacheTool():

    def __init__ (self):
        self._DataCache = {}
        self.setCurrent("core")

    def getCache(self,cache=None):
        if cache == None:
            cache = self._CurrentDataCache
        if cache in self._DataCache.keys():
            return self._DataCache[cache]
        else:
            log.debug("DataCache Invalid cache name '%s'" % cache)
            return None

    def get(self,key,cache=None):
        return self.getCache(cache).get(key)

    def put(self,key,val,cache=None):
        self.getCache(cache)[key] = val

    def setCurrent(self,current):
        self._CurrentDataCache = current
        if(self._DataCache.get(self._CurrentDataCache) == None):
            self._DataCache[self._CurrentDataCache] = {}
        log.debug("Setting _CurrentDataCache: %s",self._CurrentDataCache)

    def getCurrent(self):
        return self._CurrentDataCache

    def keys(self):
        return self._DataCache.keys()

DataCache = DataCacheTool()


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
        self.home = None
        self.subtypes = None

    def __str__(self):
        return self.id

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
      if (self.directInstanceOf(Unit.GetUnit("DataType"), layers=layers)):
          return True

      subs = GetTargets(Unit.GetUnit("typeOf"), self, layers=layers)
      subs += GetTargets(Unit.GetUnit("rdfs:subClassOf"), self, layers=layers)

      for p in subs:
          if p.isDataType(layers=layers):
              return True

      return False



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

        return ret

    def getHomeLayer(self,defaultToCore=False):
        ret = self.home
        if ret == None:
            if defaultToCore:
                ret = 'core'
            else:
                log.info("WARNING %s has no home extension defined!!" % self.id)
                ret = ""
        return ret


    def superproperties(self, layers='core'):
        """Returns super-properties of this one."""
        if not self.isAttribute(layers=layers):
          logging.debug("Non-property %s won't have subproperties." % self.id)
          return None
        superprops = GetTargets(Unit.GetUnit("rdfs:subPropertyOf"),self, layers=layers )
        return superprops

    def subproperties(self, layers='core'):
        """Returns direct subproperties of this property."""
        if not self.isAttribute(layers=layers):
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

    def __str__ (self):
        ret = ""
        if self.source != None:
            ret +=  "%s " % self.source
        if self.target != None:
            ret += "%s " % self.target
        if self.arc != None:
            ret += "%s " % self.arc
        return ret

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
            if (triple.target != None and (layers == EVERYLAYER or triple.layer in layers)):
                targets[triple.target] = 1
            elif (triple.text != None and (layers == EVERYLAYER or triple.layer in layers)):
                targets[triple.text] = 1
    return targets.keys()

def GetSources(arc, target, layers='core'):
    """All source nodes for a specified arc pointing to a specified node (within any of the specified layers)."""
#    log.debug("GetSources checking in layer: %s for unit: %s arc: %s" % (layers, target.id, arc.id))
    sources = {}
    for triple in target.arcsIn:
        if (triple.arc == arc and (layers == EVERYLAYER or triple.layer in layers)):
            sources[triple.source] = 1
    return sources.keys()

def GetArcsIn(target, layers='core'):
    """All incoming arc types for this specified node (within any of the specified layers)."""
    arcs = {}
    for triple in target.arcsIn:
        if (layers == EVERYLAYER or triple.layer in layers):
            arcs[triple.arc] = 1
    return arcs.keys()

def GetArcsOut(source,  layers='core'):
    """All outgoing arc types for this specified node."""
    arcs = {}
    for triple in source.arcsOut:
        if (layers == EVERYLAYER or triple.layer in layers):
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
    if (n.isDataType() or n.id == "DataType"):
        subs += GetSources( Unit.GetUnit("typeOf"), n, layers=layers)
    subs.sort(key=lambda x: x.id)
    return subs

def GetImmediateSupertypes(n, layers='core'):
    """Get this type's immediate supertypes, i.e. that we are subClassOf."""
    if n==None:
        return None
    sups = GetTargets( Unit.GetUnit("rdfs:subClassOf"), n, layers=layers)
    if (n.isDataType() or n.id == "DataType"):
        sups += GetTargets( Unit.GetUnit("typeOf"), n, layers=layers)
    sups.sort(key=lambda x: x.id)
    return sups

def GetAllTypes(layers='core'):
    """Return all types in the graph."""
    KEY = "AllTypes:%s" % layers
    if DataCache.get(KEY):
        logging.debug("DataCache HIT: %s" % KEY)
        return DataCache.get(KEY)
    else:
        logging.debug("DataCache MISS: %s" % KEY)
        mynode = Unit.GetUnit("Thing")
        subbed = {}
        todo = [mynode]
        while todo:
            current = todo.pop()
            subs = GetImmediateSubtypes(current, EVERYLAYER)
            if inLayer(layers,current):
                subbed[current] = 1
            for sc in subs:
                if subbed.get(sc.id) == None:
                    todo.append(sc)
        DataCache.put(KEY,subbed.keys())
        return subbed.keys()

def GetAllEnumerationValues(layers='core'):
    KEY = "AllEnums:%s" % layers
    if DataCache.get(KEY):
        logging.debug("DataCache HIT: %s" % KEY)
        return DataCache.get(KEY)
    else:
        logging.debug("DataCache MISS: %s" % KEY)
        mynode = Unit.GetUnit("Enumeration")
        log.info("Enum %s" % mynode)
        enums = {}
        subbed = {}
        todo = [mynode]
        while todo:
            current = todo.pop()
            subs = GetImmediateSubtypes(current, EVERYLAYER)
            subbed[current] = 1
            for sc in subs:
                vals = GetSources( Unit.GetUnit("typeOf"), sc, layers=EVERYLAYER)
                for val in vals:
                    if inLayer(layers,val):
                        enums[val] = 1
                if subbed.get(sc.id) == None:
                    todo.append(sc)
        DataCache.put(KEY,enums.keys())
        return enums.keys()


def GetAllProperties(layers='core'):
    """Return all properties in the graph."""
    KEY = "AllProperties:%s" % layers
    if DataCache.get(KEY):
        logging.debug("DataCache HIT: %s" % KEY)
        return DataCache.get(KEY)
    else:
        logging.debug("DataCache MISS: %s" % KEY)
        mynode = Unit.GetUnit("Thing")
        props = GetSources(Unit.GetUnit("typeOf"), Unit.GetUnit("rdf:Property"), layers=EVERYLAYER)
        res = []
        for prop in props:
            if inLayer(layers,prop):
                res.append(prop)
        sorted_all_properties = sorted(res, key=lambda u: u.id)
        DataCache.put(KEY,sorted_all_properties)
        return sorted_all_properties

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


class Example ():

    @staticmethod
    def AddExample(terms, original_html, microdata, rdfa, jsonld, egmeta, layer='core'):
       """
       Add an Example (via constructor registering it with the terms that it
       mentions, i.e. stored in term.examples).
       """
       # todo: fix partial examples: if (len(terms) > 0 and len(original_html) > 0 and (len(microdata) > 0 or len(rdfa) > 0 or len(jsonld) > 0)):
       typeinfo = "".join( [" %s " % t.id for t in terms] )
       if "FakeEntryNeeded" in typeinfo or terms==[]:
           return
       if (len(terms) > 0 and len(original_html) > 0 and len(microdata) > 0 and len(rdfa) > 0 and len(jsonld) > 0):
            return Example(terms, original_html, microdata, rdfa, jsonld, egmeta, layer='core')
       else:
           log.info("API AddExample skipped a case due to missing value(s) in example. Target terms: %s ORIG: %s MICRODATA: %s RDFA: %s JSON: %s EGMETA: %s " % ( typeinfo, original_html, microdata, rdfa, jsonld, egmeta ) )


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

    # Caching assumes the context is neutral w.r.t. our hostname.
    if DataCache.get('JSONLDCONTEXT'):
        log.debug("DataCache: recycled JSONLDCONTEXT")
        return DataCache.get('JSONLDCONTEXT')
    else:
        global namespaces
        jsonldcontext = "{\"@context\":    {\n"
        jsonldcontext += "        \"type\": \"@type\",\n"
        jsonldcontext += "        \"id\": \"@id\",\n"
        jsonldcontext += namespaces
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
        DataCache.put('JSONLDCONTEXT',jsonldcontext)
        log.debug("DataCache: added JSONLDCONTEXT")
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


def setHomeValues(items,layer='core',defaultToCore=False):
    global extensionLoadErrors

    for node in items:
        if(node == None):
            continue
        home = GetTargets( Unit.GetUnit("isPartOf"), node, layer )
        if(len(home) > 0):
            if(node.home != None):
                msg = "ERROR: %s trying to overwite home from %s to %s" % (node.id,node.home,home[0].id)
                log.info(msg)
                extensionLoadErrors += msg + '\n'
            else:
                h = home[0].id.strip()
                if h.startswith("http://"):
                    h = h[7:]
                node.home = re.match( r'([\w\-_]+)[\.:]?', h).group(1)
            if(node.home == 'schema'):
                node.home = 'core'
        elif node.home == None:
            if defaultToCore:
                node.home = "core"
            else:
                msg = "ERROR: %s has no home defined" % (node.id)
                log.info(msg)
                extensionLoadErrors += msg + '\n'

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

#set default home for those in core that do not have one
        setHomeValues(items,"core",True)

        files = glob.glob("data/*examples.txt")

        read_examples(files)

        files = glob.glob("data/2015-04-vocab_counts.txt")

        for file in files:
            usage_data = read_file(file)
            parser = parsers.UsageFileParser(None)
            parser.parse(usage_data)

    schemasInitialized = True


def read_extensions(extensions):
    import os.path
    import glob
    import re
    global extensionsLoaded
    extfiles = []
    expfiles = []
    if not extensionsLoaded: #2nd load will throw up errors and duplicate terms
        log.info("(re)scanning for extensions.")
        for i in extensions:
            extfiles += glob.glob("data/ext/%s/*.rdfa" % i)
            expfiles += glob.glob("data/ext/%s/*examples.txt" % i)

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
            setHomeValues(extitems,extid,False)

        read_examples(expfiles)

    extensionsLoaded = True

def read_examples(files):
        example_contents = []
        for f in files:
            example_content = read_file(f)
            example_contents.append(example_content)
            log.debug("examples loaded from: %s" % f)

        parser = parsers.ParseExampleFile(None)
        parser.parse(example_contents)

def StripHtmlTags(source):
    return re.sub('<[^<]+?>', '', source)

def ShortenOnSentence(source,lengthHint=250):
    if len(source) > lengthHint:
        sentEnd = re.compile('[.!?]')
        sentList = sentEnd.split(source)
        com=""
        for sent in sentList:
            com += sent
            com += source[len(com)]
            if len(com) > lengthHint:
                break
        if len(source) > len(com):
            com += ".."
        source = com
    return source
