#!/usr/bin/env python
# -*- coding: UTF-8 -*-

from __future__ import with_statement

import logging
logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
log = logging.getLogger(__name__)

from testharness import *

import threading
import re
import api
import apirdflib
import rdflib
from rdflib import URIRef
from sdoutil import *

#from apirdflib import rdfGetTargets, rdfGetSources
from apimarkdown import Markdown

CORELAYER = "core"
VTERMS={}
TERMSLOCK = threading.Lock()
from apirdflib import RDFLIBLOCK

DATATYPEURI = URIRef("http://schema.org/DataType")
ENUMERATIONURI = URIRef("http://schema.org/Enumeration")
class VTerm():
    
    CLASS = "Class"
    PROPERTY = "Property"
    DATATYPE = "Datatype"
    ENUMERATION = "Enumeration"
    ENUMERATIONVALUE = "Enumerationvalue"
    REFERENCE = "Reference"
    
    
    def __init__(self,uri,ttype=None,label='',layer=None,cat=None):
        #log.info('%s %s "%s" %s %s' % (uri,ttype,label, layer, cat))
        uri = str(uri)
        self.uri = uri
        self.id = uri
        if uri.startswith(api.SdoConfig.vocabUri()):
            self.id = uri[len(api.SdoConfig.vocabUri()):]
        self.label = label
        self.layer = CORELAYER
        if  layer:
            self.layer = layer
        self.category = cat
        if not cat:
              self.category = ""
        self.parent = None
        self.checkedDataTypeParents = False    
        self.supersededBy = None
        self.supersedes = None
        self.supers = None
        self.termStack = None
        self.subs = None
        self.props = None
        self.propUsedOn = None
        self.ranges = None
        self.domains = None
        self.targetOf = None
        self.equivalents = None
        self.inverseOf = None
        self.comments = None
        self.comment = None
        self.srcaks = None
        self.sources = None
        self.aks = None
        self.examples = None

        VTERMS[self.uri] = self
        
        if ttype == rdflib.RDFS.Class:
            self.ttype = VTerm.CLASS
            if self.uri == str(DATATYPEURI): #The base DataType is defined as a Class
                self.ttype = VTerm.DATATYPE
            if self.uri == str(ENUMERATIONURI): #The base Enumeration Type is defined as a Class
                self.ttype = VTerm.ENUMERATION
        elif ttype == rdflib.RDF.Property:
            self.ttype = VTerm.PROPERTY
        elif ttype == ENUMERATIONURI:
            self.ttype = VTerm.ENUMERATION
        elif ttype == DATATYPEURI:
            self.ttype = VTerm.DATATYPE
        elif not ttype:
            self.ttype = VTerm.REFERENCE
            self.label = id
        else:
            #log.info("checking parent %s" % ttype)
            self.parent = str(ttype)
            p = VTerm._getTerm(self.parent)
            if p.isEnumeration():
                self.ttype = VTerm.ENUMERATIONVALUE
            else:
                self.ttype = p.getType()
                        
        #log.info("VTerm %s %s" %(self.ttype,self.id))
        
    def __str__(self):
        return ("<%s: '%s'>") % (self.ttype,self.id)
    def getType(self):
        return self.ttype
    def isClass(self):
        return self.ttype == VTerm.CLASS
    def isProperty(self):
        return self.ttype == VTerm.PROPERTY
    def isDataType(self):
        if self.ttype == VTerm.DATATYPE:
            return True
        if self.isClass() and not self.checkedDataTypeParents:
            self.checkedDataTypeParents = True
            for super in self.getSupers():
                if super.isDataType():
                   self.ttype = VTerm.DATATYPE
                   return True
        return False
        
    def isEnumeration(self):
        return self.ttype == VTerm.ENUMERATION
    def isEnumerationValue(self):
        return self.ttype == VTerm.ENUMERATIONVALUE
    def isReference(self):
        return self.ttype == VTerm.REFERENCE
    def getId(self):
        return self.id
    def getPrefixedId(self):
        return prefixedIdFromUri(self.uri)
    def getUri(self):
        return self.uri
    def getLabel(self):
        return self.label
    def getComments(self):
        if not self.comments:
            self.comments = []
            comms = self.loadObjects(rdflib.RDFS.comment)
            for c in comms:
                self.comments.append(c)
        return self.comments
    def getComment(self):
        if not self.comment:
            self.loadComment()
        return self.comment
    def getSupersededBy(self):
        if not self.supersededBy:
            tmp = []
            ss = self.loadObjects("schema:supersededBy")
            for s in ss:
                t = VTerm._getTerm(str(s))
                if t:
                    tmp.append(t)
                    
            if len(tmp) > 1:
                log.debug("Warning '%s' supersededBy more than 1 term ()%s" % (self.id,len(tmp)))
            if len(tmp):
                self.supersededBy = tmp[0]
        return self.supersededBy
    def superseded(self):
        return self.getSupersededBy() != None
    def getSupersedes(self):
        if not self.supersedes:
            self.supersedes = []
            subs = self.loadSubjects("schema:supersededBy")
            for sub in subs:
                term = VTerm._getTerm(sub,createReference=True)
                sortedAddUnique(self.supersedes,term)
        return self.supersedes
    def getSourcesAndAcks(self):
        if not self.srcaks:
            self.srcaks = []
            objs = self.loadObjects("dc:source")
            for obj in objs:
                term = VTerm._getTerm(obj,createReference=True)
                sortedAddUnique(self.srcaks,term)
                
            self.sources = []
            self.aks = []
            #An aknowledgement is a 'source' with a comment
            #A source is a source without a comment
            if len(self.srcaks):
                for ao in self.srcaks:
                    acks = ao.getComments()
                    if len(acks):
                        for ack in acks:
                            self.aks.append(ack)
                    else:
                        self.sources.append(ao.getUri())
            
        return self.srcaks
    def getSources(self):
        if not self.sources:
            self.getSourcesAndAcks()
        return self.sources
    def getAcknowledgements(self):
        if not self.aks:
            self.getSourcesAndAcks()
        return self.aks
    def getCategory(self):
        return self.category
    def getLayer(self):
        return self.layer
    def getInverseOf(self):
        if not self.inverseOf:
            self.inverseOf = VTerm._getTerm(self.loadValue("schema:inverseOf"))
        return self.inverseOf
    def getSupers(self):
        if not self.supers:
            self.loadsupers()
        return self.supers
    def getTermStack(self):
        if not self.termStack:
            self.termStack = [self]
            for s in self.getSupers():
                self.termStack.extend(s.getTermStack())
        return self.termStack
    def getSubs(self):
        if not self.subs:
            self.loadsubs()
        return self.subs
    def getProperties(self):
        if not self.props:
            self.props = []
            subs = self.loadSubjects("schema:domainIncludes")
            for sub in subs:
                term = VTerm._getTerm(sub,createReference=True)
                sortedAddUnique(self.props,term)
        return self.props
    def getPropUsedOn(self):
        raise Exception("Not implemented yet")
        return self.propUsedOn
    def getRanges(self):
        if not self.ranges:
            self.ranges = []
            objs = self.loadObjects("schema:rangeIncludes")
            for obj in objs:
                term = VTerm._getTerm(obj,createReference=True)
                sortedAddUnique(self.ranges,term)
        return self.ranges
    def getDomains(self):
        if not self.domains:
            self.domains = []
            objs = self.loadObjects("schema:domainIncludes")
            for obj in objs:
                term = VTerm._getTerm(obj,createReference=True)
                sortedAddUnique(self.domains,term)
        return self.domains
    def getTargetOf(self):
        if not self.targetOf:
            self.targetOf = []
            subs = self.loadSubjects("schema:rangeIncludes")
            for sub in subs:
                term = VTerm._getTerm(sub,createReference=True)
                sortedAddUnique(self.targetOf,term)
        return self.targetOf
    def getEquivalents(self):
        if not self.equivalents:
            self.equivalents = self.loadObjects("owl:equivalentClass")
            self.equivalents.extend(self.loadObjects("owl:equivalentProperty"))
        log.info("equivalents: %s" % self.equivalents)
        return self.equivalents
    def inLayers(self,layers):
        return self.layer in layers

    def subClassOf(self,parent):
        if self == parent:
            return True
        parents = self.getSupers()
        if parent in parents:
            return True
        else:
            for p in parents:
                if p.subClassOf(parent):
                    return True
        return False
        
    
                    
    def loadComment(self):
        comments = self.getComments()
        wpre = None
        name = self.getId()
        if name.startswith("http"): #Wikilinks in markdown default to current site - extermals need overriding
            val = os.path.basename(name)
            wpre = name[:len(name) - len(val)]
        
        first = True
        buf = sdoStringIO()
        for com in comments:
            if not first:
                buf.write(" ")
            else:
                first = False
            buf.write(Markdown.parse(com,wpre=wpre))
        ret = buf.getvalue()
        if not len(ret):
            ret = "-"
        self.comment = ret
        
        
    def loadValue(self,valType):
        ret = self.loadObjects(valType)
        if not ret or len(ret) == 0:
            return None
        return ret[0]
        
    def loadObjects(self,pred):
        query = """ 
        SELECT ?val WHERE {
                %s %s ?val.
         }""" % (uriWrap(toFullId(self.id)),uriWrap(pred))
        ret = [] 
        #log.info("query %s" % query)
        res = VTerm.query(query)
        #log.info("res %d" % len(res))
        for row in res:
            #log.info(">%s<" % row.val)
            ret.append(row.val)
        return ret

    def loadSubjects(self,pred):
        query = """ 
        SELECT ?sub WHERE {
                ?sub %s %s.
         }""" % (uriWrap(pred),uriWrap(toFullId(self.id)))
        ret = [] 
        #log.info("query %s" % query)
        res = VTerm.query(query)
        #log.info("res %d" % len(res))
        for row in res:
            #log.info(">%s<" % row.sub)
            ret.append(row.sub)
        return ret
        
    def loadsupers(self):
        fullId = toFullId(self.id)
        log.info("loadsupers(%s)" % self.id)
        query = """ 
        SELECT ?sup WHERE {
             {
                 %s rdfs:subClassOf ?sup .
             }UNION{
                 %s rdfs:subPropertyOf ?sup .
             }
         }""" % (uriWrap(fullId),uriWrap(fullId))
         
        #log.info("query %s" % query)
        res = VTerm.query(query)
        #log.info("res %d" % len(res))
        self.supers = []
        for row in res:
            super = VTerm._getTerm(row.sup,createReference=True)
            if not super:
                log.debug("Failed to get term for %s" % row.sup)
                continue
            sortedAddUnique(self.supers,super)
        if self.isEnumerationValue():
            sortedAddUnique(self.supers,VTerm._getTerm(self.parent))
            


    def loadsubs(self):
        fullId = toFullId(self.id)
        #log.info("checksupers(%s)" % self.id)
        if self.ttype == VTerm.CLASS or self.ttype == VTerm.DATATYPE or self.ttype == VTerm.ENUMERATION:
            sel = "rdfs:subClassOf"
        else:
            sel = "rdfs:subPropertyOf"
        query = """ 
        SELECT ?sub WHERE {
                ?sub %s %s.
         }""" % (uriWrap(sel),uriWrap(fullId))
        #log.info("query %s" % query)
        res = VTerm.query(query)
        #log.info("res %d" % len(res))
        self.subs = []
        for row in res:
            sub = VTerm._getTerm(row.sub,createReference=True)
            if not sub:
                log.debug("Failed to get term for %s" % row.sub)
                continue
            sortedAddUnique(self.subs,sub)
            
        if self.ttype == VTerm.ENUMERATION or self.ttype == VTerm.DATATYPE:
            subjects = self.loadSubjects("a") #Enumerationvalues have an Enumeration as a type
            for child in subjects:
                sub = VTerm._getTerm(str(child))
                sortedAddUnique(self.subs,sub)
            
        
    def checkEnumerations(self):
        for t in self.supers: #Is parent a schema:Enumeration
            if t.id == "http://schema.org/Enumeration":
                self.ttype = VTerm.ENUMERATION
                return
                
        if VTerm.checkForEnumVal(self):
            self.ttype = VTerm.ENUMERATIONVALUE
                            
    def getParentPaths(self, cstack=None):
        with TERMSLOCK:
            self._pstacks = []
            if cstack == None:
                cstack = []
            self._pstacks.append(cstack)
            self._getParentPaths(self,cstack)
            return self._pstacks
        
    def _getParentPaths(self, term, cstack):
        if ":" in term.getId():  #Suppress external class references
            return

        cstack.append(term)
        tmpStacks = []
        tmpStacks.append(cstack)
        supers = term.getSupers()
    
        for i in range(len(supers)):
            if(i > 0):
                t = cstack[:]
                tmpStacks.append(t)
                self._pstacks.append(t)
        x = 0

        for p in supers:
            self._getParentPaths(p,tmpStacks[x])
            x += 1

            
    @staticmethod
    def checkForEnumVal(term):
        if term.ttype ==  VTerm.ENUMERATION:
            return True
            
        for t in term.supers:
            if VTerm.checkForEnumVal(t):
                return True
        return False   
        
        
    @staticmethod
    def getTerm(termId,refresh=False,createReference=False):
        #log.info("getTerm(%s,%s,%s)" % (termId,refresh,createReference))
        with TERMSLOCK:
            return VTerm._getTerm(termId,refresh=refresh,createReference=createReference)

    @staticmethod
    def _getTerm(termId,refresh=False,createReference=False):

        if not termId:
            return None
        termId = str(termId)
        fullId = toFullId(termId)
        #log.info("_GETTERM termId %s full %s" % (termId,fullId))
        term = VTERMS.get(fullId,None)
        #if term:
            #log.info("GOT %s" % fullId)
            
        if term and refresh:
            del VTERMS[termId]
            log.info("Term '%s' found and removed" % termId)
            term = None

        query = """ 
        SELECT ?term ?type ?label ?layer ?sup ?cat WHERE {
             %s a ?type;
                rdfs:label ?label.
            OPTIONAL {
                %s schema:isPartOf ?layer.
            }
            OPTIONAL {
                %s rdfs:subClassOf ?sup.
            }
            OPTIONAL {
                %s rdfs:subPropertyOf ?sup.
            }
            OPTIONAL {
                %s schema:category ?cat.
            }
        
        }""" % (uriWrap(fullId),uriWrap(fullId),uriWrap(fullId),uriWrap(fullId),uriWrap(fullId))
        
        if not term:
            #log.info("query %s" % query)
            res = VTerm.query(query)
            if len(res):
                term = VTerm.termsFromResults(res,termId=fullId)
            elif createReference:
                term = VTerm(fullId)
            else:
                log.debug("No definition of term %s" % fullId)
        return term

    @staticmethod
    def termsFromResults(res,termId=None):
        ret = []
        single = False
        if termId:
            single = True
        tmp = VTerm.TmpTerm(termId)
        count = 0
        for row in res: #Assumes termdefinition rows are ordered by termId
            if not single:
                termId = str(row.term)
            if tmp.id != termId: #New term definition starts on this row
                if tmp.id:
                    term = VTerm.createTerm(tmp)
                    if term:
                        ret.append(term)
                        count += 1
                tmp = VTerm.TmpTerm(termId)
            tmp.types.append(row.type)
            tmp.sups.append(row.sup)
            tmp.tt = row.type
            tmp.lab = row.label
            tmp.cat = row.cat
            tmp.layer = layerFromUri(row.layer)
            
        term = VTerm.createTerm(tmp)
        if term:
            ret.append(term)
            count += 1
            
        if single:
            return ret[0]
        else:
            return ret
        
    @staticmethod
    def createTerm(tmp):
        if not tmp or not tmp.id:
            return None
        
        if DATATYPEURI in tmp.types:
            tmp.tt = DATATYPEURI
        elif ENUMERATIONURI in tmp.sups:
            tmp.tt = ENUMERATIONURI
            
        term = VTERMS.get(tmp.id,None) 
        if not term:  #Already created this term ?     
            term =  VTerm(tmp.id,ttype=tmp.tt,label=tmp.lab,layer=tmp.layer,cat=tmp.cat)
        return term

    class TmpTerm:
        def __init__(self, id):
            self.id = id
            self.types = []
            self.sups = []
            self.lab = None
            self.layer = None
            self.cat = None
            self.tt = ""
        
        
    @staticmethod
    def getAllTypes(layer=None):
        return VTerm.getAllTerms(ttype = VTerm.CLASS,layer=layer)
        
    @staticmethod
    def getAllProperties(layer=None):
        return VTerm.getAllTerms(ttype = VTerm.PROPERTY,layer=layer)

    @staticmethod
    def getAllEnumerations(layer=None):
        return VTerm.getAllTerms(ttype = VTerm.ENUMERATION,layer=layer)

    @staticmethod
    def getAllTerms(ttype=None,layer=None,supressSourceLinks=False):
        typsel = ""
        if ttype == VTerm.CLASS:
            typsel = "a <%s>;" % rdflib.RDFS.Class
        elif ttype == VTerm.PROPERTY:
            typsel = "a <%s>;" % rdflib.RDF.Property
        elif ttype == VTerm.DATATYPE:
            typsel = "a <%s>;" % DATATYPEURI
        elif ttype == VTerm.ENUMERATION:
            typsel = "a <%s>;" % ENUMERATIONURI
        #elif ttype == VTerm.ENUMERATIONVALUE:
            #typsel = "?type <%s>;" % ENUMERATIONURI
        elif not ttype:
            typesel = ""
        else:
            log.debug("Invalid type value '%s'" % ttype)
            
        laysel = ""
        fil = ""
        supress = ""
        if layer:
            if layer == "core":
                fil = "FILTER NOT EXISTS { ?term schema:isPartOf ?x. }"
            else:
                laysel = "schema:isPartOf <%s>;" % uriFromLayer(layer)

        if supressSourceLinks:
            supress = "FILTER NOT EXISTS { ?s dc:source ?term. }"
            
            
        query = """SELECT ?term ?type ?label ?layer ?sup ?cat WHERE {
             ?term a ?type;
                %s
                %s
                rdfs:label ?label.
            OPTIONAL {
                ?term schema:isPartOf ?layer.
            }
            OPTIONAL {
                ?term rdfs:subClassOf ?sup.
            }
            OPTIONAL {
                ?term rdfs:subPropertyOf ?sup.
            }
            OPTIONAL {
                ?term schema:category ?cat.
            }
            %s
            %s
        }
        ORDER BY ?term
        """ % (typsel,laysel,fil,supress)
        
        #log.info("query %s" % query)
        res = VTerm.query(query)
        #log.info("res %d" % len(res))
        terms = VTerm.termsFromResults(res,termId=None)
        log.info("count %s VTERMS %s" % (len(terms),len(VTERMS)))
        return terms
        
    @staticmethod
    def query(q):
       graph = apirdflib.queryGraph()
       with RDFLIBLOCK:
           ret = list(graph.query(q))
       return ret

    @staticmethod
    def term2str(t):
        terms = t
        if not isinstance(t, list):
            terms = [t]
        ret = []
        for term in terms:
            ret.append(str(term))
        return ret

    @staticmethod
    def term2id(t):
        terms = t
        if not isinstance(t, list):
            terms = [t]
        ret = []
        for term in terms:
            ret.append(term.getId())
        return ret

def toFullId(termId):

    if not	':' in termId: #Includes full path or namespaces
    	fullId = api.SdoConfig.vocabUri() + termId
    elif termId.startswith("http"):
    	fullId = termId
    else:
        sp = termId.split(':')
        pre = sp[0]
        id = sp[1]
        fullId = "%s%s" % (uriForPrefix(pre),id)
    return fullId

def uriWrap(id):
    if id.startswith('http://') or id.startswith('https://'):
    	id = "<%s>" % id
    return id
        
def sortedAddUnique(lst,term):
    if term not in lst:
        lst.append(term)
    lst.sort(key=lambda u: u.getId(),reverse=False)
    
LAYERPATTERN = None
def layerFromUri(uri):
    global LAYERPATTERN
    if uri:
        if not LAYERPATTERN:
            voc = api.SdoConfig.vocabUri()
            if voc.endswith("/") or voc.endswith('#'):
                voc = voc[:len(voc) - 1]
            prto,root = getProtoAndRoot(voc)
            LAYERPATTERN = "^%s([\w]*)\.%s" % (prto,root)

        if LAYERPATTERN:
            m = re.search(LAYERPATTERN,str(uri))
            if m:
                return m.group(1)
    return None

def uriFromLayer(layer=None):
    voc = api.SdoConfig.vocabUri()
    if voc.endswith("/") or voc.endswith('#'):
        voc = voc[:len(voc) - 1]
    if not layer:
        return voc
    prto,root = getProtoAndRoot(voc)
    return "%s%s.%s" % (prto,layer,root)
        
def getProtoAndRoot(uri):
       m = re.search("^(http[s]*:\/\/)(.*)",uri)
       if m:
           prto = m.group(1)
           root = m.group(2)
           return prto,root
       return None,None
         


def prefixFromUri(uri):
    uri = str(uri)
    ns = apirdflib.getNamespaces()
    for n in ns:
        pref, pth = n
        if uri.startswith(str(pth)):
            return pref
    log.error("Requested unknown namespace uri %s" % uri)
    return None
    
def uriForPrefix(pre):
    pre = str(pre)
    ns = apirdflib.getNamespaces()
    for n in ns:
        pref, pth = n
        if pre == pref:
            return pth
    log.error("Requested unknown prefix %s:" % pre)
    return None
    
    
def prefixedIdFromUri(uri):
    prefix = prefixFromUri(uri)
    if prefix:
        return "%s:%s" % (prefix,os.path.basename(uri))
    return uri
    
               
     
        
    
    
    