#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import with_statement

import logging
logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)


import os
import os.path
import urllib
import glob
import re
import threading
import parsers
import datetime, time

from google.appengine.ext import ndb
loader_instance = False


from testharness import *

import apirdflib
import apirdfterm
from apirdfterm import VTerm
from sdoutil import *

#from apirdflib import rdfGetTargets, rdfGetSources
from apimarkdown import Markdown

def getInstanceId(short=False):
    ret = ""
    if "INSTANCE_ID" in os.environ:
        ret =  os.environ["INSTANCE_ID"]
    if short:
        ret = ret[len(ret)-6:]
    return ret

TIMESTAMPSTOREMODE = "CLOUDSTORE"
if "TIMESTAMPSTOREMODE" in os.environ:
    TIMESTAMPSTOREMODE = os.environ["TIMESTAMPSTOREMODE"]
    log.info("TIMESTAMPSTOREMODE set to %s from .yaml file" % TIMESTAMPSTOREMODE)
log.info("Initialised with TIMESTAMPSTOREMODE set to %s" % TIMESTAMPSTOREMODE)

EXAMPLESTOREMODE = os.environ.get("EXAMPLESTOREMODE","INMEM")
schemasInitialized = False
extensionsLoaded = False
extensionLoadErrors = ""

#INTESTHARNESS used to flag we are in a test harness - not called by webApp so some things will work different!
#setInTestHarness(True) should be called from test suites.
    
log.info("IN TESTHARNESS %s" % getInTestHarness())
if not getInTestHarness():
    from google.appengine.api import memcache
    from sdocloudstore import SdoCloud

AllLayersList = []
def setAllLayersList(val):
    global AllLayersList
    AllLayersList = val
    #Copy it into apirdflib 
    apirdflib.allLayersList = val

def getAllLayersList():
    global AllLayersList
    return AllLayersList
    
VARSUBPATTERN = r'\[\[([\w0-9_ -]+)\]\]'

JSONLDCONTEXT = "jsonldcontext.json"
EVERYLAYER = "!EVERYLAYER!"
sitename = "schema.org"
sitemode = "mainsite" # whitespaced list for CSS tags,
            # e.g. "mainsite testsite", "extensionsite" when off expected domains

DYNALOAD = True # permits read_schemas to be re-invoked live.
#JINJA_ENVIRONMENT = jinja2.Environment(
#   loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')),
#    extensions=['jinja2.ext.autoescape'], autoescape=True)

PAGESTOREMODE = "CLOUDSTORE" #INMEM (In instance memory)
                            #NDBSHARED (NDB shared - accross instances)
                            #CLOUDSTORE - (Cloudstorage files)
if "PAGESTOREMODE" in os.environ:
    PAGESTOREMODE = os.environ["PAGESTOREMODE"]
    log.info("PAGESTOREMODE set to %s from .yaml file" % PAGESTOREMODE)
log.info("Initialised with PAGESTOREMODE set to %s" % PAGESTOREMODE)

debugging = False

def getMasterStore():
    return apirdflib.STORE

def getQueryGraph():
    return apirdflib.queryGraph()
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
namespaces = """        "schema": "http://schema.org/",
        "cat": "http://www.w3.org/ns/dcat#",
        "cc": "http://creativecommons.org/ns#",
        "cnt": "http://www.w3.org/2008/content#",
        "ctag": "http://commontag.org/ns#",
        "dc": "http://purl.org/dc/terms/",
        "dcat": "http://www.w3.org/ns/dcat#",
        "dcterms": "http://purl.org/dc/terms/",
        "describedby": "http://www.w3.org/2007/05/powder-s#describedby",
        "earl": "http://www.w3.org/ns/earl#",
        "foaf": "http://xmlns.com/foaf/0.1/",
        "gldp": "http://www.w3.org/ns/people#",
        "gr": "http://purl.org/goodrelations/v1#",
        "grddl": "http://www.w3.org/2003/g/data-view#",
        "ht": "http://www.w3.org/2006/http#",
        "ical": "http://www.w3.org/2002/12/cal/icaltzd#",
        "license": "http://www.w3.org/1999/xhtml/vocab#license",
        "ma": "http://www.w3.org/ns/ma-ont#",
        "og": "http://ogp.me/ns#",
        "org": "http://www.w3.org/ns/org#",
        "org": "http://www.w3.org/ns/org#",
        "owl": "http://www.w3.org/2002/07/owl#",
        "prov": "http://www.w3.org/ns/prov#",
        "ptr": "http://www.w3.org/2009/pointers#",
        "qb": "http://purl.org/linked-data/cube#",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfa": "http://www.w3.org/ns/rdfa#",
        "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
        "rev": "http://purl.org/stuff/rev#",
        "rif": "http://www.w3.org/2007/rif#",
        "role": "http://www.w3.org/1999/xhtml/vocab#role",
        "rr": "http://www.w3.org/ns/r2rml#",
        "sd": "http://www.w3.org/ns/sparql-service-description#",
        "sioc": "http://rdfs.org/sioc/ns#",
        "skos": "http://www.w3.org/2004/02/skos/core#",
        "skosxl": "http://www.w3.org/2008/05/skos-xl#",
        "v": "http://rdf.data-vocabulary.org/#",
        "vcard": "http://www.w3.org/2006/vcard/ns#",
        "void": "http://rdfs.org/ns/void#",
        "wdr": "http://www.w3.org/2007/05/powder#",
        "wdrs": "http://www.w3.org/2007/05/powder-s#",
        "xhv": "http://www.w3.org/1999/xhtml/vocab#",
        "xml": "http://www.w3.org/XML/1998/namespace",
        "xsd": "http://www.w3.org/2001/XMLSchema#",
"""


class DataCacheTool():

    def __init__ (self):
        self.tlocal = threading.local()
        self.tlocal.CurrentDataCache = "core"
        self.initialise()

    def initialise(self):
        self._DataCache = {}
        self._DataCache[self.tlocal.CurrentDataCache] = {}
        return
        
    def getCache(self,cache=None):
        if cache == None:
            cache = self.getCurrent()
        if cache in self._DataCache.keys():
            return self._DataCache[cache]
        else:
            self._DataCache[cache] = {}
            return self._DataCache[cache]

    def get(self,key,cache=None):
        return self.getCache(cache).get(key)

    def remove(self,key,cache=None):
        return self.getCache(cache).pop(key,None)

    def put(self,key,val,cache=None):
        self.getCache(cache)[key] = val

    def setCurrent(self,current):
        self.tlocal.CurrentDataCache = current
        if(self._DataCache.get(current) == None):
            self._DataCache[current] = {}
        log.debug("[%s] Setting _CurrentDataCache: %s" % (getInstanceId(short=True),current))

    def getCurrent(self):
        return self.tlocal.CurrentDataCache

    def keys(self):
        return self._DataCache.keys()


class PageEntity(ndb.Model):
    content = ndb.TextProperty()
    
class NDBPageStoreTool():
    def __init__ (self):
        self.tlocal = threading.local()
        self.tlocal.CurrentStoreSet = "core"

    def initialise(self):
        import time
        log.info("[%s]PageStore initialising Data Store" % (getInstanceId(short=True)))
        loops = 0
        ret = 0
        while loops < 10:
            keys = PageEntity.query().fetch(keys_only=True)
            count = len(keys)
            if count == 0:
                break
            log.info("[%s]PageStore deleting %s keys" % (getInstanceId(short=True), count))
            ndb.delete_multi(keys,use_memcache=False,use_cache=False) 
            ret += count
            loops += 1
            time.sleep(0.01)
        return {"PageStore":ret}
            
    def getCurrent(self):
        return self.tlocal.CurrentStoreSet
        
    def setCurrent(self,current):
        self.tlocal.CurrentStoreSet = current
        log.debug("PageStore setting CurrentStoreSet: %s",current)
        
    def put(self, key, val,cache=None):
        ca = self.getCurrent()
        if cache != None:
            ca = cache
        fullKey = ca + ":" + key
        #log.info("[%s]PageStore storing %s" % (getInstanceId(),fullKey))
        ent = PageEntity(id = fullKey, content = val)
        ent.put()
        
    def get(self, key,cache=None):
        ca = self.getCurrent()
        if cache != None:
            ca = cache
        fullKey = ca + ":" + key
        ent = PageEntity.get_by_id(fullKey)
        if(ent):
            #log.info("[%s]PageStore returning %s" % (os.environ["INSTANCE_ID"],fullKey))
            return ent.content
        else:
            #log.info("PageStore '%s' not found" % fullKey)
            return None
    def remove(self, key,cache=None):
        ca = self.getCurrent()
        if cache != None:
            ca = cache
        fullKey = ca + ":" + key
        ent = PageEntity.get_by_id(fullKey)
        if(ent):
            return ent.key.delete()
        else:
            #log.info("PageStore '%s' not found" % fullKey)
            return None

class CloudPageStoreTool():
    def __init__ (self):
        self.init()
    
    def init(self):
        log.info("CloudPageStoreTool.init")
        self.tlocal = threading.local()
        self.tlocal.CurrentStoreSet = "core"
        log.info("CloudPageStoreTool.CurrentStoreSet: %s" % self.tlocal.CurrentStoreSet)
        
    def _getTypeFromKey(self,key):
        name = key
        typ = None
        split = key.split(':')
        if len(split) > 1:
            name = split[1]
            typ = split[0]
            if typ[0] == '.':
                typ = typ[1:]
        #log.info("%s > %s %s" % (key,name,typ))
        return name,typ

    def initialise(self):
        SdoCloud.cleanCache()
        return {"CloudPageStore":SdoCloud.delete_files_in_bucket(skip=["/.status"])}
            
    def getCurrent(self):
        try:
            if not self.tlocal.CurrentStoreSet:
                self.tlocal.CurrentStoreSet = "core"
        except Exception:
            self.tlocal.CurrentStoreSet = "core"
        ret = self.tlocal.CurrentStoreSet
        return ret
        
    def setCurrent(self,current):
        self.tlocal.CurrentStoreSet = current
        log.debug("CloudPageStore setting CurrentStoreSet: %s",current)
        
    def put(self, key, val,cache=None,extrameta=None):
        fname, ftype = self._getTypeFromKey(key)
        if not ftype:
            ftype = "html"
        SdoCloud.writeFormattedFile(fname,ftype=ftype,content=val,extrameta=extrameta)
        
    def get(self, key,cache=None):
        fname, ftype = self._getTypeFromKey(key)
        if not ftype:
            ftype = "html"
        return SdoCloud.readFormattedFile(fname,ftype=ftype)
            
    def remove(self, key,cache=None):
        SdoCloud.deleteFormattedFile(key)


class HeaderEntity(ndb.Model):
    content = ndb.PickleProperty()
    
class HeaderStoreTool():
    def __init__ (self):
        self.tlocal = threading.local()
        self.tlocal.CurrentStoreSet = "core"

    def initialise(self):
        import time
        log.info("[%s]HeaderStore initialising Data Store" % (getInstanceId(short=True)))
        loops = 0
        ret = 0
        while loops < 10:
            keys = HeaderEntity.query().fetch(keys_only=True)
            count = len(keys)
            if count == 0:
                break
            log.info("[%s]HeaderStore deleting %s keys" % (getInstanceId(short=True), count))
            ndb.delete_multi(keys,use_memcache=False,use_cache=False) 
            ret += count
            loops += 1
            time.sleep(0.01)
        return {"HeaderStore":ret}
            
    def getCurrent(self):
        return self.tlocal.CurrentStoreSet
        
    def setCurrent(self,current):
        self.tlocal.CurrentStoreSet = current
        log.debug("HeaderStore setting CurrentStoreSet: %s",current)

    def put(self, key, val,cache=None):
        ca = self.getCurrent()
        if cache != None:
            ca = cache
        fullKey = ca + ":" + key
        ent = HeaderEntity(id = fullKey, content = val)
        ent.put()

#    def putIfNewKey(self, key, val,cache=None):
        #gets are lightweight puts are not
#        if self.get(key,cache) == None:
#            self.put(key,val,cache)
        
    def get(self, key,cache=None):
        ca = self.getCurrent()
        if cache != None:
            ca = cache
        fullKey = ca + ":" + key
        ent = HeaderEntity.get_by_id(fullKey)
        if(ent):
            return ent.content
        else:
            return None

    def remove(self, key,cache=None):
        ca = self.getCurrent()
        if cache != None:
            ca = cache
        fullKey = ca + ":" + key
        ent = HeaderEntity.get_by_id(fullKey)
        if(ent):
            return ent.key.delete()
        else:
            return None

class DataEntity(ndb.Model):
    content = ndb.PickleProperty()
    
class DataStoreTool():
    def __init__ (self):
        self.tlocal = threading.local()
        self.tlocal.CurrentStoreSet = "core"

    def initialise(self):
        import time
        log.info("[%s]DataStore initialising Data Store" % (getInstanceId(short=True)))
        loops = 0
        ret = 0
        while loops < 10:
            keys = DataEntity.query().fetch(keys_only=True)
            count = len(keys)
            if count == 0:
                break
            log.info("[%s]DataStore deleting %s keys" % (getInstanceId(short=True), count))
            ndb.delete_multi(keys,use_memcache=False,use_cache=False) 
            ret += count
            loops += 1
            time.sleep(0.01)
        return {"DataStore":ret}
            
    def getCurrent(self):
        return self.tlocal.CurrentStoreSet
        
    def setCurrent(self,current):
        self.tlocal.CurrentStoreSet = current
        log.debug("DataStore setting CurrentStoreSet: %s",current)

    def put(self, key, val,cache=None):
        ca = self.getCurrent()
        if cache != None:
            ca = cache
        fullKey = ca + ":" + key
        ent = DataEntity(id = fullKey, content = val)
        ent.put()
        
    def get(self, key,cache=None):
        ca = self.getCurrent()
        if cache != None:
            ca = cache
        fullKey = ca + ":" + key
        ent = DataEntity.get_by_id(fullKey)
        if(ent):
            return ent.content
        else:
            return None

    def remove(self, key,cache=None):
        ca = self.getCurrent()
        if cache != None:
            ca = cache
        fullKey = ca + ":" + key
        ent = DataEntity.get_by_id(fullKey)
        if(ent):
            return ent.key.delete()
        else:
            return None
            
PageStore = None
HeaderStore = None
DataCache = None
#log.info("[%s] PageStore mode: %s" % (getInstanceId(short=True),PAGESTOREMODE))

def enablePageStore(mode):
    global PageStore,HeaderStore,DataCache
    log.info("enablePageStore(%s)" % mode)
    if(mode == "NDBSHARED"):
        log.info("[%s] Enabling NDB" % getInstanceId(short=True))
        PageStore = NDBPageStoreTool()
        log.info("[%s] Created PageStore" % getInstanceId(short=True))
        HeaderStore = HeaderStoreTool()
        log.info("[%s] Created HeaderStore" % getInstanceId(short=True))
        DataCache = DataStoreTool()
        log.info("[%s] Created DataStore" % getInstanceId(short=True))
        
    elif(mode == "INMEM"):
        log.info("[%s] Disabling NDB" % getInstanceId(short=True))
        PageStore = DataCacheTool()
        HeaderStore = DataCacheTool()
        DataCache = DataCacheTool()
        
    elif(mode == "CLOUDSTORE"):
        log.info("[%s] Enabling CloudStore" % getInstanceId(short=True))
        PageStore = CloudPageStoreTool()
        log.info("[%s] Created PageStore" % getInstanceId(short=True))
        HeaderStore = HeaderStoreTool()
        log.info("[%s] Created HeaderStore" % getInstanceId(short=True))
        DataCache = DataStoreTool()
        log.info("[%s] Created DataStore" % getInstanceId(short=True))
    else:
        log.error("Invalid storage mode: %s" % mode)

if getInTestHarness(): #Override pagestore decision if in testharness
    enablePageStore("INMEM")
else:
    enablePageStore(PAGESTOREMODE)


def prepareCloudstoreDocs():
    #if  getInTestHarness() or "localhost" in os.environ['SERVER_NAME']: #Force new version logic for local versions and tests
    if  getInTestHarness(): #Force new version logic for local versions and tests
        log.info("Skipping static docs copy for local/test instance")
        return
        
    log.info("Preparing Cloudstorage - copying static docs..")
    count = 0
    filesToCopy = []
    copiedFiles = []
    if SdoConfig.isValid():
        log.info("... from config defined sources")
        for f in SdoConfig.docsFiles():
            ft = (f.get("location"),f.get("filePart"))
            filesToCopy.append(ft)
    else:
        log.info("... from local docs location")
        for root, dirs, files in os.walk("docs"):
            for f in files:
                count += 1
                fname = os.path.join(root, f)
                ft = ("docs",fname)
                filesToCopy.append(ft)
    
    for ft in filesToCopy:
        try:
            file = ft[0] + "/" + ft[1]
            fname = "docs/" + ft[1]
            if file.startswith("file://"):
                file = file[7:]
    
            if "://" in file:
                content = urllib.urlopen(file).read()
            else:
                fd = open(file, 'r')
                content = fd.read()
                fd.close()
                
            SdoCloud.writeFormattedFile(fname,content=content, location="html", raw=True)
            copiedFiles.append(fname)
        except Exception  as e:
            log.info("ERROR reading: %s" % e)
            pass
    info = "".join( ["%s\n" % fl for fl in copiedFiles] )
    storeTimestampedInfo("staticdocscopy-timestamp",info=info)
    return 
    #sdo_send_mail(to="rjw@dataliberate.com",subject="[SCHEMAINFO] from 'api'", msg="prepareCloudstoreDocs: %s" % (count))

def cloudstoreStoreContent(fname, content, location, raw=False, private=False):
    SdoCloud.writeFormattedFile(fname,content=content, ftype="", location=location, raw=raw, private=private)          
    
def cloudstoreGetContent(fname, location, raw=False):
    content = SdoCloud.readFormattedFile(fname, ftype="", location=location) 
    return content         
    
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
        self.examples = None
        self.home = None
        self.subtypes = None
        self.sourced = False
        self.category = " "
        self.typeFlags = {}

    def __str__(self):
        return self.id

    def GetImmediateSubtypes(self, layers='core'):
      return GetImmediateSubtypes(self, layers=layers)

    @staticmethod
    def GetUnit (id, createp=False):
        """Return a Unit representing a node in the schema graph.

        Argument:
        createp -- should we create node if we don't find it? (default: False)
        """
        ret = None
        if (id in NodeIDMap):
            return NodeIDMap[id]
        
        ret = apirdflib.rdfGetTriples(id)

        if (ret == None and createp != False):
            return Unit(id)
        
        return ret

    @staticmethod
    def GetUnitNoLoad(id, createp=False):
        if (id in NodeIDMap):
            return NodeIDMap[id]
        if (createp != False):
            return Unit(id)
        return None


    def typeOf(self, type,  layers='core'):
        """Boolean, true if the unit has an rdf:type matching this type."""
        types = GetTargets( Unit.GetUnit("rdf:type"), self, layers )
        return (type in types)

    def subClassOf(self, type, layers='core'):
        """Boolean, true if the unit has an rdfs:subClassOf matching this type, direct or implied (in specified layer(s))."""
        if not type:
            return False
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
        mytypes = GetTargets( Unit.GetUnit("rdf:type"), self, layers )
        if type in mytypes:
            return True
        return False # TODO: consider an API for implied types too?

    def isClass(self, layers='core'):
        """Does this unit represent a class/type?"""
        if self.typeFlags.has_key('c'):
            return self.typeFlags['c']
        isClass = self.typeOf(Unit.GetUnit("rdfs:Class"), layers=EVERYLAYER)
        self.typeFlags['c'] = isClass
        return isClass

    def isAttribute(self, layers='core'):
        """Does this unit represent an attribute/property?"""
        if self.typeFlags.has_key('p'):
            return self.typeFlags['p']
        isProp = self.typeOf(Unit.GetUnit("rdf:Property"), layers=EVERYLAYER)
        self.typeFlags['p'] = isProp
        return isProp

    def isEnumeration(self, layers='core'):
        """Does this unit represent an enumerated type?"""
        if self.typeFlags.has_key('e'):
            return self.typeFlags['e']
        isE = self.subClassOf(Unit.GetUnit("schema:Enumeration"), layers=EVERYLAYER)
        self.typeFlags['e'] = isE
        return isE

    def isEnumerationValue(self, layers='core'):
        """Does this unit represent a member of an enumerated type?"""
        if self.typeFlags.has_key('ev'):
            return self.typeFlags['ev']
        types = GetTargets(Unit.GetUnit("rdf:type"), self , layers=EVERYLAYER)
        #log.debug("isEnumerationValue() called on %s, found %s types. layers: %s" % (self.id, str( len( types ) ), layers ) )
        found_enum = False
        for t in types:
          if t.subClassOf(Unit.GetUnit("schema:Enumeration"), layers=EVERYLAYER):
            found_enum = True
            break
        self.typeFlags['ev'] = found_enum
        return found_enum

    def isDataType(self, layers='core'):
      """
      Does this unit represent a DataType type or sub-type?

      DataType and its children do not descend from Thing, so we need to
      treat it specially.
      """
      if self.typeFlags.has_key('d'):
          return self.typeFlags['d']
          
      ret = False
      if (self.directInstanceOf(Unit.GetUnit("DataType"), layers=layers) or
            self.id == "DataType"):
          ret = True
      else:
          subs = GetTargets(Unit.GetUnit("rdfs:subClassOf"), self, layers=layers)

          for p in subs:
              if p.isDataType(layers=layers):
                  ret = True
                  break
      self.typeFlags['d'] = ret
      return ret



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

    def category(self):
        return self.category
        
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
        return GetUsage(self.id)

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
        self.id = self

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
        if self.arc != None:
            ret += "%s " % self.arc
        if self.target != None:
            ret += "%s " % self.target
        if self.text != None:
            ret += "\"%s\" " % self.text
        return ret

    @staticmethod
    def AddTriple(source, arc, target, layer='core'):
        """AddTriple stores a thing-valued new Triple within source Unit."""
        if (source == None or arc == None or target == None):
            log.info("Bailing %s %s %s" % (source, arc, target))
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
    log.info("GetTargets checking in layer: %s for unit: %s arc: %s" % (layers, source, arc))
    targets = {}
    fred = False
    try:
        for triple in source.arcsOut:
            log.info("triple %s" % triple)
            if (triple.arc == arc):
                #if (triple.target != None and (layers == EVERYLAYER or triple.layer in layers)):
                if (triple.target != None ):
                    targets[triple.target] = 1
                #elif (triple.text != None and (layers == EVERYLAYER or triple.layer in layers)):
                elif (triple.text != None):
                    targets[triple.text] = 1
        return targets.keys()
    except Exception as e:
        log.debug("GetTargets caught exception %s" % e)
        return []

def GetSources(arc, target, layers='core'):
    """All source nodes for a specified arc pointing to a specified node (within any of the specified layers)."""
    log.info("GetSources checking in layer: %s for unit: %s arc: %s" % (layers, target, arc))
    if(target.sourced == False):
        apirdflib.rdfGetSourceTriples(target)

    sources = {}
    for triple in target.arcsIn:
        #if (triple.arc == arc and (layers == EVERYLAYER or triple.layer in layers)):
        log.info("arc %s triplearc: %s" %(arc,triple.arc))
        if (triple.arc == arc ):
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
    tx = GetComments(node, layers)
    if len(tx) > 0:
            return Markdown.parse(tx[0])
    else:
        return "-"

def GetComments(node, layers='core') : 
    """Get the rdfs:comment(s) we find on this node within any of the specified layers."""
    return GetTargets(Unit.GetUnit("rdfs:comment", True), node, layers=layers )

def GetsoftwareVersions(node, layers='core') : 
    """Get the schema:softwareVersion(s) we find on this node (or [] ), within any of the specified layers."""
    return GetTargets(Unit.GetUnit("softwareVersion", True), node, layers=layers )

def GetImmediateSubtypes(n, layers='core'):
    """Get this type's immediate subtypes, i.e. that are subClassOf this."""
    if n==None:
        return None
    subs = GetSources( Unit.GetUnit("rdfs:subClassOf", True), n, layers=layers)
    if (n.isDataType() or n.id == "DataType"):
        subs += GetSources( Unit.GetUnit("rdf:type", True), n, layers=layers)
    subs.sort(key=lambda x: x.id)
    return subs

def GetImmediateSupertypes(n, layers='core'):
    """Get this type's immediate supertypes, i.e. that we are subClassOf."""
    if n==None:
        return None
    sups = GetTargets( Unit.GetUnit("rdfs:subClassOf", True), n, layers=layers)
    if (n.isDataType() or n.id == "DataType"):
        sups += GetTargets( Unit.GetUnit("rdf:type", True), n, layers=layers)
    sups.sort(key=lambda x: x.id)
    return sups

Utc = "util_cache"
UtilCache = DataCacheTool()
def GetAllTypes(layers='core'):
    global Utc
    """Return all types in the graph."""
    KEY = "AllTypes:%s" % layers
    if UtilCache.get(KEY+'x',Utc):
        #logging.debug("DataCache HIT: %s" % KEY)
        return UtilCache.get(KEY,Utc)
    else:
        sorted_all_types = []
        types = VTerm.getAllProperties()
        for t in types:
            sorted_all_types.append(t.getId())
        sorted_all_types.sort()
        UtilCache.put(KEY,sorted_all_types,Utc)
        return sorted_all_types


def GetAllDataTypes(layers='core'):
    global Utc
    """Return all types in the graph."""
    KEY = "AllDataTypes:%s" % layers
    if UtilCache.get(KEY+'x',Utc):
        #logging.debug("DataCache HIT: %s" % KEY)
        return UtilCache.get(KEY,Utc)
    else:
        #logging.debug("DataCache MISS: %s" % KEY)
        mynode = apirdfterm.VTerm.getTerm("Datatype")
        subbed = {}
        todo = [mynode]
        while todo:
            current = todo.pop()
            subs = current.getSubs()
            subbed[current] = 1
            for sc in subs:
                if subbed.get(sc.getId()) == None:
                    todo.append(sc)
        UtilCache.put(KEY,subbed.keys(),Utc)
        return subbed.keys()

def GetAllEnumerationValues(layers='core'):
    global Utc
    KEY = "AllEnums:%s" % layers
    if UtilCache.get(KEY,Utc):
        #logging.debug("DataCache HIT: %s" % KEY)
        return UtilCache.get(KEY,Utc)
    else:
        #logging.debug("DataCache MISS: %s" % KEY)
        mynode = apirdfterm.VTerm.getTerm("schema:Enumeration")
        enums = {}
        subbed = {}
        todo = [mynode]
        while todo:
            current = todo.pop()
            subs = current.getSubs()
            subbed[current] = 1
            for sc in subs:
                if sc.isEnumerationValue():
                    enums[sc.getId()] = 1
                if subbed.get(sc.getId()) == None:
                    todo.append(sc)
        UtilCache.put(KEY,enums.keys(),Utc)
        return enums.keys()


def GetAllProperties(layers='core'):
    """Return all properties in the graph."""
    global Utc
    KEY = "AllProperties:%s" % layers
    if UtilCache.get(KEY,Utc):
        #logging.debug("DataCache HIT: %s" % KEY)
        return UtilCache.get(KEY,Utc)
    else:
        sorted_all_properties = []
        props = VTerm.getAllProperties()
        for p in props:
            sorted_all_properties.append(p.getId())
        sorted_all_properties.sort()
        UtilCache.put(KEY,sorted_all_properties,Utc)
        return sorted_all_properties

def GetAllTerms(layers='core',includeDataTypes=False):
    ret = GetAllTypes(layers)
    ret.extend(GetAllEnumerationValues(layers))
    ret.extend(GetAllProperties(layers))
    if includeDataTypes:
        ret.extend(GetAllDataTypes(layers))
    return sorted(ret,key=lambda u: u.id)
    
    
def GetParentPathTo(start_term,end_term=None):
    #Output paths from start_term to only if end_term in path
    if not end_term:
        end_term = VTerm.getTerm("Thing")
    
    parentsList = start_term.getParentPaths()
    outList = []
    for l in parentsList:
        if end_term in l:
            path = []
            for t in l:
                path.append(t)
                if t == end_term:
                    break
            outList.append(path)
    return outList
        
def HasMultipleBaseTypes(term, layers='core'):
    """True if this unit represents a type with more than one immediate supertype."""
    t = VTerm.getTerm(term)
    parents = t.getSupers()
    return len(parents) > 1

EXAMPLESMAP = {}
EXAMPLES = {}
ExamplesCount = 0

exlock = threading.RLock()
class Example ():

    @staticmethod
    def AddExample(terms, original_html, microdata, rdfa, jsonld, egmeta, layer='core'):
       """
       Add an Example (via constructor registering it with the terms that it
       mentions, i.e. stored in term.examples).
       """
       # todo: fix partial examples: if (len(terms) > 0 and len(original_html) > 0 and (len(microdata) > 0 or len(rdfa) > 0 or len(jsonld) > 0)):
       typeinfo = "".join( [" %s " % t for t in terms] )
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
        """Example constructor, registers itself with the ExampleMap of terms to examples."""
        global EXAMPLES, EXAMPLESMAP, ExamplesCount
        ExamplesCount += 1
        self.orderId = ExamplesCount #Used to maintain consistancy of display order
        self.terms = terms
        self.original_html = original_html
        self.microdata = microdata
        self.rdfa = rdfa
        self.jsonld = jsonld
        self.egmeta = egmeta
        self.layer = layer
        if 'id' in self.egmeta:
            self.keyvalue = self.egmeta['id']
        else:
            self.keyvalue = "%s-gen-%s"% (terms[0],ExamplesCount)
            self.egmeta['id'] = self.keyvalue
            
        with exlock:
            for term in terms:
                
                if(EXAMPLESMAP.get(term, None) == None):
                    EXAMPLESMAP[term] = []
                if not self.keyvalue in EXAMPLESMAP.get(term):
                    EXAMPLESMAP.get(term).append(self.keyvalue)
                
            if not EXAMPLES.get(self.keyvalue):
                EXAMPLES[self.keyvalue] = self

def LoadTermExamples(term, layers='core'):
    """Returns the examples (if any) for some Unit node."""
    #log.info("Getting examples for: %s %s" % (node.id,node.examples))
    if(term.examples == None):
        term.examples = []
        if getInTestHarness() or EXAMPLESTOREMODE != "NDBSHARED": #Get from local storage
            with exlock:
                examples = EXAMPLESMAP.get(term.id)
                if examples:
                    for e in examples:
                        ex = EXAMPLES.get(e)
                        if ex:
                            term.examples.append(ex)

        else:                  #Get from NDB shared storage
            ids = ExampleMap.get(term.id)
            if not ids:
                ids = []
            for i in ids:
                term.examples.append(ExampleStore.get_by_id(i))
    return term.examples

USAGECOUNTS = {}

def StoreUsage(id,count):
	USAGECOUNTS[id] = count

def GetUsage(id):
    str = USAGECOUNTS.get(id,0)
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
        return ""
    

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
    jsonldcontext = ""
    jsonldcontext += "{\n  \"@context\": {\n"
    jsonldcontext += "        \"type\": \"@type\",\n"
    jsonldcontext += "        \"id\": \"@id\",\n"
    jsonldcontext += "        \"HTML\": { \"@id\": \"rdf:HTML\" },\n"
    jsonldcontext += "        \"@vocab\": \"%s\",\n" % SdoConfig.vocabUri()
    ns = apirdflib.getNamespaces()
    done = []
    for n in ns:
        for n in ns:
            pref, pth = n
            pref = str(pref)
            if not pref in done:
                done.append(pref)
                jsonldcontext += "        \"%s\": \"%s\",\n" % (pref,pth)

    datatypepre = ""    
    if SdoConfig.vocabUri() != "http://schema.org/":
        datatypepre = "schema:"
        
    vocablines = ""
    externalines = ""
    typins = ""
    url = apirdfterm.VTerm.getTerm("schema:URL")
    date = apirdfterm.VTerm.getTerm("schema:Date")
    datetime = apirdfterm.VTerm.getTerm("schema:DateTime")
    for t in apirdfterm.VTerm.getAllTerms(supressSourceLinks=True):
        if t.isClass() or t.isEnumeration() or t.isEnumerationValue() or t.isDataType():
            line =  "        \"" + t.getId() + "\": {\"@id\": \"" + t.getPrefixedId() + "\"},"
        elif t.isProperty():
            range = t.getRanges()
            
            type = None

            if url in range:
                type = "@id"
            elif date in range:
                type = "Date"
            elif datetime in range:
                type = "DateTime"

            typins = ""
            if type:
                typins = ", \"@type\": \"" + type + "\""
                
            line = "        \"" + t.getId() + "\": { \"@id\": \"" + t.getPrefixedId() + "\"" + typins + "},"
        
        if t.getId().startswith("http"):
            externalines += line
        else:
            vocablines += line

    jsonldcontext += vocablines
    jsonldcontext += externalines
    jsonldcontext += "}}\n"
    jsonldcontext = jsonldcontext.replace("},}}","}\n    }\n}")
    jsonldcontext = jsonldcontext.replace("},","},\n") 
    return str(jsonldcontext)

#### UTILITIES


def inLayer(layerlist, node):
    """Does a unit get its type mentioned in a layer?"""
    if (node is None):
        return False
    if len(GetTargets(Unit.GetUnit("rdf:type"), node, layers=layerlist) ) > 0:
        #log.debug("Found typeOf for node %s in layers: %s"  % (node.id, layerlist ))
        return True
    if len(GetTargets(Unit.GetUnit("rdfs:subClassOf"), node, layers=layerlist) ) > 0:
    # TODO: should we really test for any mention of a term, not just typing?
        return True
    return False

def read_file (filename):
    """Read a file from disk, return it as a single string."""
    strs = []
    
    if filename.startswith("file://"):
        filename = filename[7:]
        
    if "://" in filename:
        import urllib2
        log.info("URL: %s" % filename)
        try:
            fd = urllib2.urlopen(filename)
            return fd.read()
        except urllib2.URLError as e:
            log.info("read_file URLError %s: %s" % (e,e.message))
            return None
        except Exception as e:
            log.info("read_file Exception %s: %s" % (e,e.message))
            return None
    else:
        file_path = full_path(filename)
        import codecs
        try:
            #log.debug("READING FILE: filename=%s file_path=%s " % (filename, file_path ) )
            for line in codecs.open(file_path, 'r', encoding="utf8").readlines():
                strs.append(line)
            ret = "".join(strs)
        except Exception as e:
            log.info("read_file Exception %s: %s" % (e,e.message))
            return None
    return ret

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

def read_schemas(files):
    """Read/parse/ingest schemas from files from config"""
    load_start = datetime.datetime.now()
    log.debug("[%s] (re)loading core and annotations." % getInstanceId(short=True))

    for f in files:
        try:
            log.info("read_schema '%s' '%s'" %(f.get("ext"),f.get("file")))
            apirdflib.load_graph(f.get("ext"),f.get("file"),prefix=f.get("prefix"),vocab=f.get("vocaburi"))
        except Exception as e:
            log.error("exception loading schema file %s %s: %s" % (f.get("file"),e,e.message))
            pass
        
        
    log.info("[%s] Loaded  graphs in %s" % (getInstanceId(short=True),(datetime.datetime.now() - load_start)))

def load_usage_data(files):
    load_start = datetime.datetime.now()
    for f in files:
        try:
            usage_data = read_file(f.get("file"))
            parser = parsers.UsageFileParser(None)
            parser.parse(usage_data)
        except Exception as e:
            log.error("exception loading usage data file %s %s: %s" % (f,e,e.message))
            pass
        
    log.debug("[%s]Loaded usage data in %s" % (getInstanceId(short=True),(datetime.datetime.now() - load_start)))
    

def read_local_schemas(loadExtensions=False):
    """Read/parse/ingest schemas from data/*.rdfa. Also data/*examples.txt"""
    load_start = datetime.datetime.now()

    global schemasInitialized
    schemasInitialized = True
    if (not schemasInitialized or DYNALOAD):
        log.debug("[%s] (re)loading core and annotations." % getInstanceId(short=True))
        files = glob_from_dir("data","*.rdfa")
        jfiles = glob_from_dir("data","*.jsonld")
        for jf in jfiles: 
            rdfequiv = jf[:-7]+".rdfa"
            if not rdfequiv in files: #Only add .jsonld files if no equivalent .rdfa
                files.append(jf)
        file_paths = []
        for f in files:
            file_paths.append(full_path(f))
        apirdflib.load_graph('core',file_paths)
        log.info("[%s] Loaded core graphs in %s" % (getInstanceId(short=True),(datetime.datetime.now() - load_start)))

        load_start = datetime.datetime.now()

        files = glob_from_dir("data","2015-04-vocab_counts.txt")
        for file in files:
            usage_data = read_file(file)
            parser = parsers.UsageFileParser(None)
            parser.parse(usage_data)
        log.debug("[%s]Loaded usage data in %s" % (getInstanceId(short=True),(datetime.datetime.now() - load_start)))

    schemasInitialized = True


def read_extensions(extensions):
    global extensionsLoaded
    extfiles = []
    expfiles = []
    load_start = datetime.datetime.now()

    if not extensionsLoaded: #2nd load will throw up errors and duplicate terms
        log.info("[%s] extensions %s " % (getInstanceId(short=True),extensions))
        for i in extensions:
            all_layers[i] = "1"
            extfiles = glob_from_dir("data/ext/%s/" % i,"*.rdfa")
            jextfiles = glob_from_dir("data/ext/%s/" % i,"*.jsonld")
            for jf in jextfiles: 
                rdfequiv = jf[:-7]+".rdfa"
                if not rdfequiv in extfiles: #Only add .jsonld files if no equivalent .rdfa
                    extfiles.append(jf)

            file_paths = []
            for f in extfiles:
                file_paths.append(full_path(f))
            apirdflib.load_graph(i,file_paths)
    log.info("[%s]Loaded extension graphs in %s" % (getInstanceId(short=True),(datetime.datetime.now() - load_start)))
    extensionsLoaded = True

def load_examples_data(extensions):
    if SdoConfig.isValid():
        load_example_sources(SdoConfig.exampleFiles())
        if not getInTestHarness() and EXAMPLESTOREMODE == "NDBSHARED": #Use NDB Storage
            ExampleStore.store(EXAMPLES)
            ExampleMap.store(EXAMPLESMAP)
            memcache.set("ExmplesLoaded",value=True)
        else:
            load_local_examples_data(extensions)
        
def load_example_sources(files):
    if files:
        work = []
        for f in files:
            #log.info("FILE: %s" % f)
            work.append(f.get("file"))
        
        read_examples(work,f.get("extension"))
    

def load_local_examples_data(extensions):
    log.info("Loading Local Examples")
    load = False
    if getInTestHarness():
        load = True
    elif not memcache.get("ExmplesLoaded"):#Useing NDB Storage and not loaded
        load = True

    if load:
        load_start = datetime.datetime.now()
        files = glob_from_dir("data","*examples.txt")
        read_examples(files,'core')
        for i in extensions:
            expfiles = glob_from_dir("data/ext/%s" % i,"*examples.txt")
            read_examples(expfiles,i)

        if not getInTestHarness() and EXAMPLESTOREMODE == "NDBSHARED": #Use NDB Storage
            ExampleStore.store(EXAMPLES)
            ExampleMap.store(EXAMPLESMAP)
            memcache.set("ExmplesLoaded",value=True)

        log.info("Loaded %s examples mapped to %s terms in %s" % (len(EXAMPLES),len(EXAMPLESMAP),(datetime.datetime.now() - load_start)))
    else:
        log.info("Examples already loaded")
        
def read_examples(files, layer):
    first = True
    for f in files:
        try:
            parser = parsers.ParseExampleFile(None,layer=layer)
            #log.info("[%s] Reading: %s" % (getInstanceId(short=True),f))
            if first:
                #log.info("[%s] Loading examples from %s" % (getInstanceId(short=True),layer))
                first = False
            parser.parse(f)
        except Exception as e:
            log.error("exception loading examples file %s %s: %s" % (f,e,e.message))
            pass
        

EXAMPLESTORECACHE = []
class ExampleStore(ndb.Model):
    original_html = ndb.TextProperty('h',indexed=False)
    microdata = ndb.TextProperty('m',indexed=False)
    rdfa = ndb.TextProperty('r',indexed=False)
    jsonld = ndb.TextProperty('j',indexed=False)
    egmeta = ndb.PickleProperty('e',indexed=False)
    keyvalue = ndb.StringProperty('o',indexed=True)
    layer = ndb.StringProperty('l',indexed=False)

    @staticmethod
    def initialise():
        EXAMPLESTORECACHE = []
        import time
        log.info("[%s]ExampleStore initialising Data Store" % (getInstanceId(short=True)))
        loops = 0
        ret = 0
        while loops < 10:
            keys = ExampleStore.query().fetch(keys_only=True,use_memcache=False,use_cache=False)
            count = len(keys)
            if count == 0:
                break
            log.info("[%s]ExampleStore deleting %s keys" % (getInstanceId(short=True), count))
            ndb.delete_multi(keys,use_memcache=False,use_cache=False) 
            ret += count
            loops += 1
            time.sleep(0.01)
        return {"ExampleStore":ret}

    @staticmethod
    def add(example):
        e = ExampleStore(id=example.keyvalue,
                original_html=example.original_html,
                microdata=example.microdata,
                rdfa=example.rdfa,
                jsonld=example.jsonld,
                egmeta=example.egmeta,
                keyvalue=example.keyvalue,
                layer=example.layer)
        EXAMPLESTORECACHE.append(e)

    @staticmethod
    def store(examples):
        for e in examples:
            ExampleStore.add(e)
        
        if len(EXAMPLESTORECACHE):
            ndb.put_multi(EXAMPLESTORECACHE,use_cache=False)

    def get(self,name):
        if name == 'original_html':
           return self.original_html
        if name == 'microdata':
           return self.microdata
        if name == 'rdfa':
           return self.rdfa
        if name == 'jsonld':
           return self.jsonld
        return ""

    @staticmethod
    def getEgmeta(id):
        em = ExampleStore.get_by_id(id)
        ret = em.emeta
        if ret:
            return ret
        return {}

EXAMPLESMAPCACHE = []
class ExampleMap(ndb.Model):
    examples = ndb.StringProperty('e',repeated=True,indexed=False)
    
    @staticmethod
    def initialise():
        EXAMPLESMAPCACHE = []
        log.info("[%s]ExampleMap initialising Data Store" % (getInstanceId(short=True)))
        loops = 0
        ret = 0
        while loops < 10:
            keys = ExampleMap.query().fetch(keys_only=True,use_memcache=False,use_cache=False)
            count = len(keys)
            if count == 0:
                break
            log.info("[%s]ExampleMap deleting %s keys" % (getInstanceId(short=True), count))
            ndb.delete_multi(keys,use_memcache=False,use_cache=False) 
            ret += count
            loops += 1
            time.sleep(0.01)
        return {"ExampleMap":ret}

    @staticmethod
    def store(map):
        for term, examples in map.items():
            ids = []
            for e in examples:
                ids.append(e.keyvalue)
            EXAMPLESMAPCACHE.append(ExampleMap(id=term,examples=ids))

        if len(EXAMPLESMAPCACHE):
            ndb.put_multi(EXAMPLESMAPCACHE,use_cache=False)

    @staticmethod
    def get(term):
        em = ExampleMap.get_by_id(term)
        if em:
            return em.examples
        return []
    
       
######################################
PageCaches = [PageStore,HeaderStore]
ExampleCaches = [ExampleStore,ExampleMap]
class CacheControl():

    @staticmethod
    def clean(pagesonly=False):
        ret = {}

        if PAGESTOREMODE == "INMEM":
            ret["PageStore"] = PageStore.initialise()
            ret["HeaderStore"] = HeaderStore.initialise()
            ret["DataCache"] = DataCache.initialise()

        ndbret = CacheControl.ndbClean()
        ret.update(ndbret)
        
        if PAGESTOREMODE == "CLOUDSTORE":
            prepareCloudstoreDocs()
        
        return ret
        
    @staticmethod
    def ndbClean():
        NdbCaches = PageCaches
        NdbCaches += ExampleCaches
    
        ret = {}
        if getInTestHarness():
            return ret
        for c in NdbCaches:
            r =  c.initialise()
            if r:
                ret.update(r)
        return ret

###############################

def StripHtmlTags(source):
    if source and len(source) > 0:
        return re.sub('<[^<]+?>', '', source)
    return ""

def ShortenOnSentence(source,lengthHint=250):
    if source and len(source) > lengthHint:
        source = source.strip()
        sentEnd = re.compile('[.!?]')
        sentList = sentEnd.split(source)
        com=""
        count = 0
        while count < len(sentList):
            if(count > 0 ):
                if len(com) < len(source):
                    com += source[len(com)]
            com += sentList[count]
            count += 1
            if count == len(sentList):
                if len(com) < len(source):
                    com += source[len(source) - 1]
            if len(com) > lengthHint:
                if len(com) < len(source):
                    com += source[len(com)]
                break
                
        if len(source) > len(com) + 1:
            com += ".."
        source = com
    return source

log.info("[%s]api loaded" % (getInstanceId(short=True)))
###############################
class TimestampEntity(ndb.Model):
    content = ndb.TextProperty()
    info = ndb.TextProperty()


def storeTimestampedInfo(tag,stamp=None,info=None):
    if not stamp:
        stamp = datetime.datetime.utcnow().strftime("%a %d %b %Y %H:%M:%S UTC")

    if TIMESTAMPSTOREMODE == "INMEM":
        log.info("Storing %s stamp: '%s'" % (tag,stamp))
        if info:
            stamp = "%s\n%s" %(stamp,info)
        memcache.set(key=tag,value=stamp)

    elif TIMESTAMPSTOREMODE == "NDBSHARED":
        log.info("Storing ndbshared %s stamp: '%s'" % (tag,stamp))
        ent = TimestampEntity(id = tag, content = stamp, info = info)
        ent.put()

    elif TIMESTAMPSTOREMODE == "CLOUDSTORE":
        log.info("Storing cloudstore %s stamp: '%s' info: %s" % (tag,stamp,info))
        if info:
            stamp = "%s\n%s" %(stamp,info)
        val = cloudstoreStoreContent("%s.txt" % tag, stamp, ".status", private=True)
        
def getTimestampedInfo(tag):
    info = ""
    val = ""
    if TIMESTAMPSTOREMODE == "INMEM":
        data =  memcache.get(tag)
        val = data.split('\n',1)[0]
        info = data[len(val):]
        log.info("%s mem version: '%s'" % (tag, val))

    elif TIMESTAMPSTOREMODE == "NDBSHARED":
        ent = TimestampEntity.get_by_id(tag)
        if ent:
            val = ent.content
            info = ent.info
        log.info("%s: ndbshared version: '%s'" % (tag, val))

    elif TIMESTAMPSTOREMODE == "CLOUDSTORE":
        tag += ".txt"
        data = cloudstoreGetContent(tag, ".status")
        if data:
            val = data.split('\n',1)[0]
            info = data[len(val):]
        else:
            val="-1"
        log.info("%s: cloudstore version: '%s'" % (tag, val))
        
    return val, info
    

###############################
class SdoConfig():
    configFile = ""
    nested = 0
    valid = False
    loaded = False
    myconf = None
    name = None
    attic = None
    varslist = None
    descs = {}
    
    @classmethod
    def clear(cls):
        if cls.myconf:
            cls.myconf.close()
        cls.valid = False
        cls.loaded = False
        cls.myconf = None
        cls.name = None
        cls.attic = None
        cls.varslist = None
        cls.descs = {}
    
    
    @classmethod
    def load(cls, conffile):
        log.info("Loading config file from %s" % conffile)
        if cls.myconf:
            log.info("Found previous config load graph - closing it!")
            cls.myconf.close()
            cls.myconf = None
            
        config = conffile
        while config:
            try:
                SdoConfig.myconf = apirdflib.graphFromFiles(config,prefix="scc",path="http://configfiles.schema.org/")
                config = cls.loadData(configFile=config)#Returns new config file if a redirect
            except Exception as e:
                log.info("Configuration file (%s) read/load Exception %s: %s" % (config,e,e.message))
                pass
            
            if config:
                log.info("Found previous config load graph - closing it!")
                cls.myconf.close() #dump previous graphs to start next on clean.

        cls.configFile = config

        if len(cls.myconf) > 0:
            cls.valid = True
            log.info("SdoConfig.myconf valid:%s %s triple count: %s" % (cls.valid, cls.myconf, len(cls.myconf)))
            
        else:
            cls.valid = False
            log.info("No config detected!!!")
    
    @classmethod
    def isValid(cls):
        return cls.valid
        
    @classmethod
    def getConfigFile(cls):
        return cls.configFile

    @classmethod
    def getname(cls):
        return cls.name

    @classmethod
    def prefix(cls):
        return cls.pre
        
    @classmethod
    def loadData(cls,configFile=None):
        redirectq= """SELECT ?loc WHERE {
            ?s a scc:ConfigurationRedirect;
                scc:configurationLocation ?loc
        }"""
        
        q = """SELECT ?name ?url ?voc ?pre ?attic ?include WHERE { 
                                ?s a scc:DataFeed;
                                    scc:siteurl ?url;
                                    scc:vocaburl ?voc;
                                    scc:prefix ?pre;
                                    scc:name ?name. 
                                OPTIONAL {
                                    ?s scc:atticurl ?attic.
                                  }
                                }"""
                            
        if cls.nested > 5:
            log.error("Too many nested redirects (%s) - aborting" % cls.nested + 1)
            return False
        newconfig = None
        if not cls.loaded:
            res = apirdflib.rdfQueryStore(redirectq,cls.myconf)
            if len(res):
                for row in res:
                    loc = row.loc
                    log.info("Found Redirect to config file: %s" % loc)
                    cls.nested += 1
                    newconfig = str(loc)
                    
            if not newconfig:
                res = apirdflib.rdfQueryStore(q,cls.myconf)
                if len(res) >  1:
                    log.error("More than one DataFeed in config file!!")
                    cls.valid = False
                for row in res:
                    cls.name = row.name
                    cls.pre = row.pre
                    cls.url = str(row.url)
                    cls.voc = str(row.voc)
                    cls.attic = str(row.attic)
                    cls.loaded = True
                    break
                if cls.loaded:
                    cls.loadIncludes(configFile)
                
        return newconfig

    @classmethod
    def loadIncludes(cls,configFile):
        if not configFile:
            return
        q = """SELECT DISTINCT ?inc WHERE { 
                                ?s a scc:DataFeed;
                                    scc:name "%s";
                                    scc:include ?inc.
                                  } 
                                 """ % (cls.name)
        nameq = """SELECT DISTINCT ?obj WHERE { 
                                ?s a scc:DataFeed;
                                    scc:name "%s";
                                    ?p ?obj.
                                  } 
                                 """ % (cls.name)
        res = apirdflib.rdfQueryStore(q,cls.myconf)
        inc = ""
        if len(res):
            try:
                for row in list(res):
                    inc = str(row.inc)
                    #Include files are placed in same location as main config
                    if os.path.basename(inc) != inc:
                        log.error("No path allowed in include file names! %s" % inc)
                        inc = None 
                    elif os.path.basename(configFile) != configFile:
                        inc = os.path.dirname(configFile) + "/" + inc
                    
                    if inc:
                        log.info("Loading Include file: %s" % inc)
                        graph = apirdflib.graphFromFiles(inc,prefix="scc",path="http://configfiles.schema.org/")
                        objs = apirdflib.rdfQueryStore(nameq,graph)
                        if not len(objs):
                            log.error("No triples for DataFeed '%s' in include file: %s" % (cls.name,inc))
                        else:
                            log.info("Include triple count: %s" % len(graph))
                            cls.myconf += graph
            except Exception as e:
                log.info("Configuration include file (%s) read/load Exception %s: %s" % (inc,e,e.message))
                cls.valid = False
                pass
                            
    @classmethod
    def templateDir(cls):
        ret = None
        temps = cls.files("templates")
        if temps and len(temps):
            ret = temps[0].get("location")
        log.info("Templates dir: %s " % ret)
        return ret
        
    @classmethod
    def baseUri(cls):
        return cls.url

    @classmethod
    def siteUri(cls):
        ret =  cls.baseUri()
        if ret.endswith("/"):
            ret = ret[:len(ret)-1]
        return ret
        
    @classmethod
    def siteUriRoot(cls):
        m = re.search("^(http[s]*:\/\/)(.*)",cls.siteUri)
        root = None
        if m:
            prto = m.group(1)
            root = m.group(2)
        return root

    @classmethod
    def vocabUri(cls):
        return cls.voc

    @classmethod
    def atticUri(cls):
        return cls.attic
        
        
    @classmethod
    def termFiles(cls):
        return cls.files(filetype="TERMS")
        
    @classmethod
    def exampleFiles(cls):
        return cls.files(filetype="EXAMPLES")
        
    @classmethod
    def countsFiles(cls):
        return cls.files(filetype="COUNTS")
        
    @classmethod
    def docsFiles(cls):
        return cls.files(filetype="DOCS")
        
    @classmethod
    def loadVars(cls):
        q = """SELECT ?var ?val WHERE {
            ?s scc:dataFeedVar ?o.
            ?o ?var ?val.
            }"""

        cls.varslist = {}
        res = apirdflib.rdfQueryStore(q,cls.myconf)
        for row in res:
            #log.info(">>> %s ==== %s <<<<<"% (row.var,row.val))
            cls.varslist[os.path.basename(row.var)] = row.val #the var value will come back as a URI
 
    @classmethod
    def varsub(cls,s):
        if not cls.varslist:
            cls.loadVars()
        return re.sub(VARSUBPATTERN, cls.varsubReplace, s)
            
    @classmethod
    def varsubReplace(cls,match):
        ret = ""
        var = match.group(1)
        val = cls.varslist.get(var,None)
        if val:
            ret = val
        return ret
        
    @classmethod
    def descriptor(cls,extension=None):
        ret = cls.descs.get(extension,None)
        if ret:
            return ret
            
        ex=""
        fil=""
        if extension and len(extension):
            ex='?v scc:extension "%s".' % extension
        else:
            fil="""FILTER ( strlen(?ext) < 1 || NOT EXISTS {?v scc:extension ?ext. } ) """
                
            
        q = """SELECT ?id ?name ?ver ?disam ?com ?ex ?linktext WHERE {
                                ?s a scc:DataFeed;
                                    scc:name "%s";
                                    scc:extensiondescription ?v.
                                %s
                                ?v scc:id ?id;
                                   scc:name ?name;
                                   scc:comment ?com.
                                 OPTIONAL {
                                   ?v scc:extension ?ex.                  
                                 }OPTIONAL {
                                   ?v scc:linktext ?linktext.                  
                                 } OPTIONAL {
                                   ?v scc:disambiguatingDescription ?disam.                  
                                 } OPTIONAL {
                                   ?v scc:softwareVersion ?ver.                  
                                 } 
                                 %s                                  
        }
        """ % (cls.name,ex,fil)
        #log.info("%s" % q)
        res = apirdflib.rdfQueryStore(q,cls.myconf)
        #log.info("%s" % len(res))
        
        ret = []
        for row in res:
            r = {
                "id": str(row.id),
                "name": str(row.name),
                "version": str(row.ver),
                "brief": str(row.disam),
                "comment": str(row.com),
                "linktext": str(row.linktext),
                "extension": str(row.ex),
                "disambiguatingDescription": str(row.disam)
            }
            ret.append(r)
        cls.descs[extension] = ret
        return ret
        
    @classmethod
    def getDescriptor(cls,ext,var=""):
        descriptor = cls.descriptor(extension=ext)
        if len(descriptor):
            return descriptor[0].get(var,None)
        return None
        
        
    @classmethod
    def stripLocalPathPrefix(cls,path):
        ret = path
        if ret and len(ret):
            if ret.startswith('./'):
                ret = ret[2:]
            elif ret.startswith('.'):
                ret = ret[1:]
        return ret
        
    @classmethod
    def files(cls,filetype=None):
        filter = ""
        if filetype:
            filter ='FILTER regex(?type, "%s", "i")' % filetype
            
        q = """SELECT DISTINCT ?file ?dir ?ext ?type ?addpre ?addvoc WHERE { 
                                ?s a scc:DataFeed;
                                    scc:name "%s";
                                    scc:dataFeedElement ?d.
                                    
                                ?d scc:fileContent ?type.
                                
                                 OPTIONAL {
                                   ?d scc:extension ?ext.                  
                                 } OPTIONAL {
                                   ?d scc:contentLocation ?dir.                  
                                 }OPTIONAL {
                                   ?d scc:contentFile ?file.
                                 }OPTIONAL {
                                     ?d scc:addPrefix ?addpre;
                                        scc:addVocaburl ?addvoc.
                                 }
                                 %s
                                }
                ORDER BY ?ext ?type ?file
                                """ % (cls.name,filter)
                                
        res = apirdflib.rdfQueryStore(q,cls.myconf)
        ret = []
        for row in res:
            d = row.dir
            if d:
                d = cls.stripLocalPathPrefix(str(cls.varsub(d)))
            loc = d
            f = row.file
            if f:
                f = cls.stripLocalPathPrefix(str(cls.varsub(f)))
            fpath = f
            if d and f:
                if not d.endswith('/'):
                    d += '/'
                f = d + f
            if f and "://" not in f:
                if f.startswith('./'):
                    f = f[2:]
                elif f.startswith('/'):
                    f = f[1:]
                f = "file://%s" % full_path(f)
            t = str(row.type)
            t = t.upper()
            e = row.ext
            if e:
                e = str(e)
            else:
                e = ""
                
            
            p = row.addpre
            if not p or not len(p):
                p = None
            v = row.addvoc
            if not v or not len(v):
                v = None
            
            
            
            r = {
                "ext": e,
                "type": t,
                "file": f,
                "location": loc,
                "filePart": fpath,
                "prefix": p,
                "vocaburi": v
            }
            ret.append(r)
        return ret


