#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

from __future__ import with_statement

import logging
logging.basicConfig(level=logging.INFO) 
log = logging.getLogger(__name__)

import threading
import os
import sys
import re
import rdflib
from rdflib import URIRef
import io
from sdoterm import *
from localmarkdown import Markdown

VOCABURI="http://schema.org/"
CORE    = "core"
DEFTRIPLESFILESGLOB = ["data/*.ttl","data/ext/*/*.ttl"]
LOADEDDEFAULT=False
TERMS={}
EXPANDEDTERMS={}
TERMSLOCK = threading.Lock()
RDFLIBLOCK = threading.Lock()

DATATYPEURI = URIRef(VOCABURI+"DataType")
ENUMERATIONURI = URIRef(VOCABURI+"Enumeration")
THINGURI = URIRef(VOCABURI+"Thing")

class SdoTermSource():
    
    TYPE = "Class"
    PROPERTY = "Property"
    DATATYPE = "Datatype"
    ENUMERATION = "Enumeration"
    ENUMERATIONVALUE = "Enumerationvalue"
    REFERENCE = "Reference"
    TERMCOUNTS=None
    
    SOURCEGRAPH=None
    MARKDOWNPROCESS=True
    
    def __init__(self,uri,ttype=None,label='',layer=None,cat=None):
        #log.info('%s %s "%s" %s %s' % (uri,ttype,label, layer, cat))
        uri = str(uri)
        self.uri = uri
        self.id = uri2id(uri)
        self.label = label
        self.layer = CORE
        if  layer:
            self.layer = layer
        self.category = cat
        if not cat:
              self.category = ""
        self.termdesc = None
        
        self.parent = None
        self.checkedDataTypeParents = False    
        self.supersededBy = None
        self.supersedes = None
        self.supers = None
        self.termStack = None
        self.subs = None
        self.members = None
        self.props = None
        self.propUsedOn = None
        self.ranges = None
        self.domains = None
        self.targetOf = None
        self.equivalents = None
        self.gotinverseOf = False
        self.inverseOf = None
        self.comments = None
        self.comment = None
        self.srcaks = None
        self.sources = None
        self.aks = None
        self.examples = None
        self.enum = None
        
        


        
        if ttype == rdflib.RDFS.Class:
            self.ttype = SdoTerm.TYPE
            if self.uri == str(DATATYPEURI): #The base DataType is defined as a Class
                self.ttype = SdoTerm.DATATYPE
            elif self.uri == str(ENUMERATIONURI): #The base Enumeration Type is defined as a Class
                self.ttype = SdoTerm.ENUMERATION
            elif self.isEnumeration():
                self.ttype = SdoTerm.ENUMERATION
        elif ttype == rdflib.RDF.Property:
            self.ttype = SdoTerm.PROPERTY
        elif ttype == ENUMERATIONURI:
            self.ttype = SdoTerm.ENUMERATION
        elif ttype == DATATYPEURI:
            self.ttype = SdoTerm.DATATYPE
        elif not ttype:
            self.ttype = SdoTerm.REFERENCE
            self.label = id
        else:
            self.parent = SdoTermSource._getTerm(str(ttype),createReference=True)
            
            if self.parent.termType == SdoTerm.ENUMERATION:
                self.ttype = SdoTerm.ENUMERATIONVALUE
            elif self.parent.termType == SdoTerm.DATATYPE:
                self.ttype = SdoTerm.DATATYPE
            else:
                self.ttype = SdoTerm.REFERENCE
                #raise Exception("Unknown parent type '%s' for term: %s" % (ttype, self.uri))
                
        if self.ttype == SdoTerm.TYPE:
            self.termdesc = SdoType(self.id,self.uri,self.label)
        elif self.ttype == SdoTerm.PROPERTY:
            self.termdesc = SdoProperty(self.id,self.uri,self.label)
        elif self.ttype == SdoTerm.DATATYPE:
            self.termdesc = SdoDataType(self.id,self.uri,self.label)
        elif self.ttype == SdoTerm.ENUMERATION:
            self.termdesc = SdoEnumeration(self.id,self.uri,self.label)
        elif self.ttype == SdoTerm.ENUMERATIONVALUE:
            self.termdesc = SdoEnumerationvalue(self.id,self.uri,self.label)
            if self.parent:
                self.termdesc.enumerationParent = self.parent.id
        elif self.ttype == SdoTerm.REFERENCE:
            self.termdesc = SdoReference(self.id,self.uri,self.label)

        self.termdesc.category = self.category
        self.termdesc.acknowledgements = self.getAcknowledgements()
        self.termdesc.comment = self.getComment()
        self.termdesc.comments = self.getComments()
        self.termdesc.equivalents = self.getEquivalents()
        self.termdesc.pending = self.inLayers("pending")
        self.termdesc.retired = self.inLayers("attic")
        self.termdesc.sources = self.getSources()
        self.termdesc.subs = self.getSubs()
        self.termdesc.supers = self.getSupers()
        self.termdesc.supersededBy = self.getSupersededBy()
        self.termdesc.supersedes = self.getSupersedes()
        self.termdesc.superseded = self.superseded()
        self.termdesc.termStack = self.getTermStack()
        self.termdesc.superPaths = self.getParentPaths() #MUST be called after supers has been added to self.termdesc
        
        #Class (Type) Building
        if self.ttype == SdoTerm.TYPE or self.ttype == SdoTerm.DATATYPE or self.ttype == SdoTerm.ENUMERATION:
            self.termdesc.properties = self.getProperties(getall=False)
            self.termdesc.allproperties = self.getProperties(getall=True)
            self.termdesc.expectedTypeFor = self.getTargetOf()
            if self.ttype == SdoTerm.ENUMERATION:
                if not len(self.termdesc.properties):
                    self.termdesc.termStack = []
            self.termdesc.enumerationMembers = self.getEnumerationMembers()
        elif self.ttype == SdoTerm.PROPERTY:
            self.termdesc.domainIncludes = self.getDomains()
            self.termdesc.rangeIncludes = self.getRanges()
            self.termdesc.inverse = self.getInverseOf()
        elif self.ttype == SdoTerm.ENUMERATIONVALUE:
            pass
        elif self.ttype == SdoTerm.REFERENCE:
            self.termdesc.label = prefixedIdFromUri(self.uri)
            self.termdesc.comment = self.getComment()
        
        
        
        TERMS[self.uri] = self.termdesc
        
        #log.info("SdoTermSource %s %s" %(self.ttype,self.id))

    def __str__(self):
        return ("<SdoTermSource: %s '%s'>") % (self.ttype,self.id)
    def getTermdesc(self):
        return self.termdesc
    def getType(self):
        return self.ttype
    def isClass(self):
        return self.ttype == SdoTerm.TYPE
    def isProperty(self):
        return self.ttype == SdoTerm.PROPERTY
    def isDataType(self):
        if self.ttype == SdoTerm.DATATYPE:
            return True
        if self.isClass() and not self.checkedDataTypeParents:
            self.checkedDataTypeParents = True
            for super in self.getSupers():
                if super.isDataType():
                   self.ttype = SdoTerm.DATATYPE
                   return True
        return False

    def isEnumeration(self):
        if self.enum == None:
            query = """ 
            ASK  {
                    %s rdfs:subClassOf* %s.
             }""" % (uriWrap(toFullId(self.id)),uriWrap(ENUMERATIONURI))
            ret = [] 
            #log.info("query %s" % query)
            res = SdoTermSource.query(query)
            for row in res:
                self.enum = row
        #log.info("res %s" % self.enum)
        return self.enum
            
        
        return self.ttype == SdoTerm.ENUMERATION
    def isEnumerationValue(self):
        return self.ttype == SdoTerm.ENUMERATIONVALUE
    def isReference(self):
        return self.ttype == SdoTerm.REFERENCE
    def getId(self):
        return self.id
    def getParent(self):
        return self.parent
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
                if sys.version_info.major == 3:
                    self.comments.append(str(c))
                else:
                    self.comments.append(unicode(c))
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
                t = uri2id(str(s))
                if t:
                    tmp.append(t)
                    
            if len(tmp) > 1:
                log.debug("Warning '%s' supersededBy more than 1 term ()%s" % (self.id,len(tmp)))
            if len(tmp):
                self.supersededBy = tmp[0]
            else:
                self.supersededBy = ""
        return self.supersededBy
    def superseded(self):
        return len(self.getSupersededBy()) > 0
    def getSupersedes(self):
        if not self.supersedes:
            self.supersedes = []
            subs = self.loadSubjects("schema:supersededBy")
            for sub in subs:
                self.supersedes.append(uri2id(str(sub)))
        return self.supersedes
    def getSourcesAndAcks(self):
        if not self.srcaks:
            self.srcaks = []
            objs = self.loadObjects("dc:source")
            objs += self.loadObjects("dct:source") #TODO Findout why dc:source in rdf files cets turned into dct:source when loaded.
            objs += self.loadObjects("schema:source") #To accept later ttl versions.
            self.sources = []
            self.aks = []
            for obj in objs:
                obj = str(obj)
                term = SdoTermSource._getTerm(obj,createReference=True)

            #An aknowledgement is a 'source' with a comment
            #A source is a source without a comment
                if term and term.comment and len(term.comment):
                    self.aks.append(term.comment)
                else:
                    self.sources.append(obj)
                self.srcaks.append(obj)                
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
        if not self.gotinverseOf:
            self.gotinverseOf = True
            inverse = self.loadValue("schema:inverseOf")
            if inverse:
                self.inverseOf = uri2id(str(inverse))
        return self.inverseOf
    def getSupers(self):
        if not self.supers:
            self.loadsupers()
        return self.supers
    def getTermStack(self):
        if not self.termStack:
            self.termStack = []
            for sup in self.getSupers():
                s = SdoTermSource._getTerm(sup,createReference=True)
                if s.termType == SdoTerm.REFERENCE:
                    continue
                self.termStack.append(s.id)
                if s.termStack:
                    self.termStack.extend(s.termStack)                
            stack = []
            for t in reversed(self.termStack):
                if t not in stack:
                    stack.append(t)
            self.termStack = list(reversed(stack))
        return self.termStack
    def getSubs(self):
        if not self.subs:
            self.loadsubs()
        return self.subs
    def getProperties(self, getall = False):
        if not self.props:
            self.props = []
            subs = self.loadSubjects("schema:domainIncludes")
            for sub in subs:
                self.props.append(uri2id(str(sub)))
            self.props.sort()
        ret = self.props
        
        if getall:
            allprops = []
            allprops.extend(self.props)
            for t in self.getTermStack():
                if t != self.id:
                    if t == "Enumeration": 
                        break
                    trm = SdoTermSource._getTerm(t,createReference=True)
                    if trm.termType == SdoTerm.TYPE or trm.termType == SdoTerm.DATATYPE or trm.termType == SdoTerm.ENUMERATION:
                        for p in trm.properties:
                            if p not in allprops:
                                allprops.append(p)
            allprops.sort()
            ret = allprops
        return ret
            
    def getPropUsedOn(self):
        raise Exception("Not implemented yet")
        return self.propUsedOn
    def getRanges(self):
        if not self.ranges:
            self.ranges = []
            objs = self.loadObjects("schema:rangeIncludes")
            for obj in objs:
                self.ranges.append(uri2id(str(obj)))
            self.ranges.sort()
        return self.ranges
    def getDomains(self):
        if not self.domains:
            self.domains = []
            objs = self.loadObjects("schema:domainIncludes")
            for obj in objs:
                self.domains.append(uri2id(str(obj)))
            self.domains.sort()
        return self.domains

    def getTargetOf(self,plusparents=False,stopontarget=False):
        if not self.targetOf:
            self.targetOf = []
            subs = self.loadSubjects("schema:rangeIncludes")
            for sub in subs:
                self.targetOf.append(uri2id(str(sub)))
        ret = self.targetOf
        if not (len(self.targetOf) and stopontarget):
            if plusparents:
                targets = self.targetOf
                for s in self.getSupers():
                    sup = SdoTermSource._getTerm(s,createReference=True)
                    if sup.uri() == ENUMERATIONURI or sup.uri == THINGURI:
                        break
                    ptargets = sup.expectedTypeFor
                    for t in ptargets:
                        targets.append(t)
                    if len(targets) and stopontarget:
                        break
                ret = targets
        ret.sort()
        return ret
    def getEquivalents(self):
        if not self.equivalents:
            self.equivalents = []
            equivalents = self.loadObjects("owl:equivalentClass")
            equivalents.extend(self.loadObjects("owl:equivalentProperty"))
            for e in equivalents:
                self.equivalents.append(str(e))
        #log.info("equivalents: %s" % self.equivalents)
        return self.equivalents
    def inLayers(self,layers):
        return self.layer in layers

    @staticmethod
    def subClassOf(child,parent):
        if isinstance(child, str):
            child = SdoTermSource.getTerm(child)
        if isinstance(parent, str):
            parent = SdoTermSource.getTerm(parent)

        if child == parent:
            return True

        parents = child.supers
        if parent.id in parents:
            return True
        else:
            for p in parents:
                if SdoTermSource.subClassOf(p,parent):
                    return True
        return False

                    
    def loadComment(self):
        comments = self.getComments()
        wpre = None
        name = self.termdesc.id
        if name.startswith("http:"): #Wikilinks in markdown default to current site - extermals need overriding
            val = os.path.basename(name)
            wpre = name[:len(name) - len(val)]
        
        first = True
        buf = []
        for com in comments:
            if not first:
                buf.append(" ")
            else:
                first = False
            if SdoTermSource.MARKDOWNPROCESS:
                buf.append  (Markdown.parse(com,wpre=wpre))
            else:
                buf.append(com)
        ret = ''.join(buf)
        if not len(ret):
            ret = ""
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
        res = SdoTermSource.query(query)
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
        res = SdoTermSource.query(query)
        #log.info("res %d" % len(res))
        for row in res:
            #log.info(">%s<" % row.sub)
            ret.append(row.sub)
        return ret
        
    def loadsupers(self):
        fullId = toFullId(self.id)
        #log.info("loadsupers(%s)" % self.id)
        query = """ 
        SELECT ?sup WHERE {
             {
                 %s rdfs:subClassOf ?sup .
             }UNION{
                 %s rdfs:subPropertyOf ?sup .
             }
         }
         ORDER BY ?sup""" % (uriWrap(fullId),uriWrap(fullId))
         
        #log.info("query %s" % query)
        res = SdoTermSource.query(query)
        #log.info("res %d" % len(res))
        self.supers = []
        for row in res:
            self.supers.append(uri2id(str(row.sup)))


    def loadsubs(self):
        fullId = toFullId(self.id)
        #log.info("checksupers(%s)" % self.id)
        if self.ttype == SdoTerm.TYPE or self.ttype == SdoTerm.DATATYPE or self.ttype == SdoTerm.ENUMERATION:
            sel = "rdfs:subClassOf"
        else:
            sel = "rdfs:subPropertyOf"
        query = """ 
        SELECT ?sub WHERE {
                ?sub %s %s.
         }ORDER BY ?sub""" % (uriWrap(sel),uriWrap(fullId))
        #log.info("query %s" % query)
        res = SdoTermSource.query(query)
        #log.info("res %d" % len(res))
        self.subs = []
        for row in res:
            self.subs.append(uri2id(str(row.sub)))

        if self.ttype == SdoTerm.DATATYPE:
            subjects = self.loadSubjects("a") #Enumerationvalues have an Enumeration as a type
            for child in subjects:
                self.subs.append(uri2id(str(child)))
                                        

    def getEnumerationMembers(self):
        
        if not self.members and self.ttype == SdoTerm.ENUMERATION:
            self.members = []
            subjects = self.loadSubjects("a") #Enumerationvalues have an Enumeration as a type
            for child in subjects:
                self.members.append(uri2id(str(child)))
            self.members.sort()
        return self.members
                                        
        
    
    def getParentPaths(self, cstack=None):
        self._pstacks = []
        if cstack == None:
            cstack = []
        self._pstacks.append(cstack)
        self._getParentPaths(self.termdesc,cstack)
        
        inserts = []
        if self.ttype == SdoTerm.PROPERTY:
            inserts = ["Property","Thing"]
        elif self.ttype == SdoTerm.DATATYPE and self.id != "DataType":
            inserts = ["DataType"]        
        elif self.ttype == SdoTerm.TYPE:
            base = self._pstacks[0][0]
            if base != self.id:
                basetype = SdoTermSource._getTerm(base)
            else:
                basetype = self.termdesc
            if basetype.termType == SdoTerm.DATATYPE:
                inserts = ["DataType"]
                
        for ins in inserts:
            for s in self._pstacks:
                s.insert(0,ins)
                
            
        return self._pstacks
        
    def _getParentPaths(self, term, cstack):
        #if ":" in term.id:  #Suppress external class references
            #ßreturn

        cstack.insert(0,term.id)
        tmpStacks = []
        tmpStacks.append(cstack)
        supers = term.supers

        if term.termType == SdoTerm.ENUMERATIONVALUE and term.enumerationParent:
            if term.enumerationParent not in supers:
                supers.append(term.enumerationParent)
            
        if supers:
            for i in range(len(supers)):
                if(i > 0):
                    t = cstack[:]
                    tmpStacks.append(t)
                    self._pstacks.append(t)

            x=0
            for p in supers:
                if not (p.startswith("http:") or p.startswith("https:")):
                    sup = SdoTermSource._getTerm(p)
                    self._getParentPaths(sup,tmpStacks[x])
                    x += 1

    @staticmethod
    def getParentPathTo(start_term,end_term=None):
        #Output paths from start_term to only if end_term in path
        start_term = SdoTermSource.getTerm(start_term)
        if not end_term:
            end_term = "Thing"
     
        superpaths = start_term.superPaths
        outList = []
        for path in superpaths:
            if end_term in path:
                outList.append(path)
        return outList
            

    @staticmethod
    def checkForEnumVal(term):
        if term.ttype ==  SdoTerm.ENUMERATION:
            return True
            
        for t in term.supers:
            if SdoTermSource.checkForEnumVal(t):
                return True
        return False   
        
        

    @staticmethod
    def expandTerms(terms):
        ret = []
        for t in terms:
            ret.append(SdoTermSource.expandTerm(t))
        return ret
        
    @staticmethod
    def expandTerm(termdesc,depth=0):
        
        import copy
        termdesc = copy.copy(termdesc)
        
        #log.info("Expanding %s" % termdesc.id)

        if not termdesc.expanded:
            termdesc.expanded = True
            supers = []
            for path in termdesc.superPaths:
                supers.append(SdoTermSource.termsFromIds(path))
            termdesc.superPaths = supers
                
                
            termdesc.termStack = SdoTermSource.termsFromIds(termdesc.termStack)
            termdesc.supers = SdoTermSource.termsFromIds(termdesc.supers)
            termdesc.equivalents = SdoTermSource.termsFromIds(termdesc.equivalents)
        
            if termdesc.termType == SdoTerm.TYPE or termdesc.termType == SdoTerm.DATATYPE or termdesc.termType == SdoTerm.ENUMERATION:
                termdesc.properties = SdoTermSource.termsFromIds(termdesc.properties)
                termdesc.expectedTypeFor = SdoTermSource.termsFromIds(termdesc.expectedTypeFor)

                if depth < 2: #Expand the properties but prevent recursion further
                    props = []
                    for p in termdesc.properties:
                        props.append(SdoTermSource.expandTerm(p,depth=depth +1))
                    termdesc.properties = props
                    expects = []
                    for e in termdesc.expectedTypeFor:
                        expects.append(SdoTermSource.expandTerm(e,depth=depth +1))
                    termdesc.expectedTypeFor = expects
                
                if termdesc.termType == SdoTerm.ENUMERATION:
                    termdesc.enumerationMembers = SdoTermSource.termsFromIds(termdesc.enumerationMembers)
            elif termdesc.termType == SdoTerm.PROPERTY:
                termdesc.domainIncludes = SdoTermSource.termsFromIds(termdesc.domainIncludes)
                termdesc.rangeIncludes = SdoTermSource.termsFromIds(termdesc.rangeIncludes)
                termdesc.inverse = SdoTermSource.termFromId(termdesc.inverse)
            elif termdesc.termType == SdoTerm.ENUMERATIONVALUE:
                termdesc.enumerationParent = SdoTermSource.termFromId(termdesc.enumerationParent)

            if not depth: #Expand the indivdual termdescs in the terms' termstack but prevent recursion further.
                stack = []
                for t in termdesc.termStack:
                    stack.append(SdoTermSource.expandTerm(t,depth=depth +1))
                termdesc.termStack = stack
        
        return termdesc
 
    @staticmethod
    def termFromId(id=""):
        ids = SdoTermSource.termsFromIds([id])
        if len(ids):
            return ids[0]
        return None
        
    @staticmethod
    def termsFromIds(ids=[]):
        ret = []
        for tid in ids:
            if tid and len(tid):
                if type(tid) is str:
                    ret.append(SdoTermSource._getTerm(tid,createReference=True))
                else:
                    ret.append(tid )
        return ret

    @staticmethod
    def termsFromResults(res,termId=None):
        ret = []
        single = False
        if termId:
            single = True
        tmp = SdoTermSource.TmpTerm(termId)
        count = 0
        for row in res: #Assumes termdefinition rows are ordered by termId
            if not single:
                termId = str(row.term)
            if tmp.id != termId: #New term definition starts on this row
                if tmp.id:
                    term = SdoTermSource.createTerm(tmp)
                    if term:
                        ret.append(term)
                        count += 1
                tmp = SdoTermSource.TmpTerm(termId)
            tmp.types.append(row.type)
            tmp.sups.append(row.sup)
            tmp.tt = row.type
            tmp.lab = row.label
            tmp.cat = row.cat
            tmp.layer = layerFromUri(row.layer)
            
        term = SdoTermSource.createTerm(tmp)
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
            
        term = TERMS.get(tmp.id,None) 
        if not term:  #Already created this term ?     
            t =  SdoTermSource(tmp.id,ttype=tmp.tt,label=tmp.lab,layer=tmp.layer,cat=tmp.cat)
            term = t.termdesc
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
    def getAllTypes(layer=None,expanded=False):
        return SdoTermSource.getAllTerms(ttype = SdoTerm.TYPE,layer=layer,expanded=expanded)
        
    @staticmethod
    def getAllProperties(layer=None,expanded=False):
        return SdoTermSource.getAllTerms(ttype = SdoTerm.PROPERTY,layer=layer,expanded=expanded)

    @staticmethod
    def getAllEnumerations(layer=None,expanded=False):
        return SdoTermSource.getAllTerms(ttype = SdoTerm.ENUMERATION,layer=layer,expanded=expanded)

    @staticmethod
    def getAllEnumerationvalues(layer=None,expanded=False):
        return SdoTermSource.getAllTerms(ttype = SdoTerm.ENUMERATIONVALUE,layer=layer,expanded=expanded)

        
    @staticmethod
    def getAllTerms(ttype=None,layer=None,supressSourceLinks=False,expanded=False):
        typsel = ""
        extra = ""
        if ttype == SdoTerm.TYPE:
            typsel = "a <%s>;" % rdflib.RDFS.Class
        elif ttype == SdoTerm.PROPERTY:
            typsel = "a <%s>;" % rdflib.RDF.Property
        elif ttype == SdoTerm.DATATYPE:
            typsel = "a <%s>;" % DATATYPEURI
        elif ttype == SdoTerm.ENUMERATION:
            typsel = "rdfs:subClassOf* <%s>;" % ENUMERATIONURI
        elif ttype == SdoTerm.ENUMERATIONVALUE:
            extra = "?type rdfs:subClassOf*  <%s>." % ENUMERATIONURI
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
            
            
        query = """SELECT DISTINCT ?term ?type ?label ?layer ?sup ?cat WHERE {
             ?term a ?type;
                %s
                %s
                rdfs:label ?label.
            %s
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
        """ % (typsel,laysel,extra,fil,supress)
        
        #log.info("query %s" % query)
        res = SdoTermSource.query(query)
        #log.info("res %d" % len(res))

        terms = []
        if expanded:
            terms = SdoTermSource.termsFromResults(res,termId=None)
        else:
            for row in res:
                terms.append(uri2id(str(row.term)))
        
        #log.info("count %s TERMS %s" % (len(terms),len(TERMS)))
        return terms
        
    @staticmethod
    def setSourceGraph(g):
        SdoTermSource.SOURCEGRAPH = g
        g.bind("schema",VOCABURI)
        g.bind("owl","http://www.w3.org/2002/07/owl#")
        g.bind("dc","http://purl.org/dc/elements/1.1/")
        g.bind("dct","http://purl.org/dc/terms/")
        g.bind("dctype","http://purl.org/dc/dcmitype/")
        g.bind("void","http://rdfs.org/ns/void#")
        g.bind("dcat","http://www.w3.org/ns/dcat#")
        
        TERMS={} #Clear cache
        EXPANDEDTERMS={}

    @staticmethod
    def loadSourceGraph(files=None):
        import glob
        global DEFTRIPLESFILESGLOB

        if not files or files == "default":
            if SdoTermSource.SOURCEGRAPH:
                if not SdoTermSource.LOADEDDEFAULT:
                    raise Exception("Sourcegraph already loaded - canot overwrite with defaults")
                print("Default files already loaded")
                return
        
            else:
                SdoTermSource.LOADEDDEFAULT = True
                print("SdoTermSource.loadSourceGraph() loading from default files found in globs: %s" %  DEFTRIPLESFILESGLOB)
                files = []
                for g in DEFTRIPLESFILESGLOB:
                    files.extend(glob.glob(g))
        elif isinstance(files, str):
            SdoTermSource.LOADEDDEFAULT = False
            print("SdoTermSource.loadSourceGraph() loading from file: %s" % files)
            files = [files]
        else:
            SdoTermSource.LOADEDDEFAULT = False
            print("SdoTermSource.loadSourceGraph() loading from %d files" % len(files))

        if not len(files):
            raise Exception("No triples file(s) to load")

        SdoTermSource.setSourceGraph(rdflib.Graph())
        for f in files:
            ex = os.path.splitext(f)[1]
            if ex == ".nt":
                format = "nt"
            elif ex == ".ttl":
                format = "turtle"
            else:
                raise Exception("Unsupported file format: %s" % ex)
            try:
                g = rdflib.Graph()
                g.parse(source=f, format=format)
                SdoTermSource.SOURCEGRAPH += g
            except Exception as e:
                raise Exception("Error loading graph source %s: %s" % (f,e))

    @staticmethod
    def sourceGraph():
        if SdoTermSource.SOURCEGRAPH == None:
            SdoTermSource.loadSourceGraph()
        return SdoTermSource.SOURCEGRAPH
    
    @staticmethod
    def getNamespaces():
        list(SdoTermSource.SOURCEGRAPH.namespaces())
        
    @staticmethod
    def vocabUri():
        return VOCABURI
    

    @staticmethod
    def query(q):
        if SdoTermSource.SOURCEGRAPH == None:
            SdoTermSource.loadSourceGraph()

        graph = SdoTermSource.SOURCEGRAPH
        #print("Query: %s" % q)
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
        
    @staticmethod
    def termCounts():
        if not SdoTermSource.TERMCOUNTS:
            count = """SELECT (COUNT(?s) as ?count) WHERE {
                ?s a ?type .
                FILTER (strStarts(str(?s),"%s"))
            } """ % VOCABURI
            res = SdoTermSource.query(count)
            allterms = int(res[0][0])

            count = """SELECT (COUNT(?s) as ?count) WHERE {
                ?s a rdfs:Class .
                FILTER (strStarts(str(?s),"%s"))
            } """ % VOCABURI
            res = SdoTermSource.query(count)
            classes = int(res[0][0])
            
            count = """SELECT (COUNT(?s) as ?count) WHERE {
                ?s a rdf:Property .
                FILTER (strStarts(str(?s),"%s"))
            } """ % VOCABURI
            res = SdoTermSource.query(count)
            properties = int(res[0][0])
            
            count = """SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {
                ?s rdfs:subClassOf* schema:Enumeration .
                FILTER (strStarts(str(?s),"%s"))
            } """ % VOCABURI
            res = SdoTermSource.query(count)
            enums = int(res[0][0])

            count = """SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {
                ?s a ?type .
                ?type rdfs:subClassOf* schema:Enumeration .
                FILTER (strStarts(str(?s),"%s"))
            } """ % VOCABURI
            res = SdoTermSource.query(count)
            enumvals = int(res[0][0])

            count = """SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {
                {
                    ?s a schema:DataType .
                }UNION{
                    ?s rdf:type* schema:DataType .
                }UNION{
                    ?s rdfs:subClassOf* ?x .
                    ?x a schema:DataType .
                }
                FILTER (strStarts(str(?s),"%s"))
           } """ % VOCABURI
            res = SdoTermSource.query(count)
            datatypes = int(res[0][0])

            count = """SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {
                ?s rdfs:subClassOf* ?x .
                ?x a schema:DataType .
                FILTER (strStarts(str(?s),"%s"))
           } """ % VOCABURI
            res = SdoTermSource.query(count)
            datatypeclasses = int(res[0][0])
            
            types = classes
            types -= 2 #Eumeration & DataType
            types -= enums
            types -= datatypeclasses

            SdoTermSource.TERMCOUNTS = {}
            SdoTermSource.TERMCOUNTS[SdoTerm.TYPE] = types
            SdoTermSource.TERMCOUNTS[SdoTerm.PROPERTY] = properties
            SdoTermSource.TERMCOUNTS[SdoTerm.DATATYPE] = datatypes
            SdoTermSource.TERMCOUNTS[SdoTerm.ENUMERATION] = enums
            SdoTermSource.TERMCOUNTS[SdoTerm.ENUMERATIONVALUE] = enumvals
            SdoTermSource.TERMCOUNTS["All"] = allterms
        return SdoTermSource.TERMCOUNTS
            

    @staticmethod
    def setMarkdownProcess(x):
        SdoTermSource.MARKDOWNPROCESS = x

    @staticmethod
    def termCache():
        return TERMS

    @staticmethod
    def getTerm(termId,expanded=False,refresh=False,createReference=False):
        #log.info("getTerm(%s,%s,%s)" % (termId,refresh,createReference))
        with TERMSLOCK:
            return SdoTermSource._getTerm(termId,expanded=expanded,refresh=refresh,createReference=createReference)

    @staticmethod
    def _getTerm(termId,expanded=False,refresh=False,createReference=False):

        if not termId:
            return None
        #log.info("GET: %s" % termId)
        termId = str(termId)
        fullId = toFullId(termId)
        #log.info("_GETTERM termId %s full %s" % (termId,fullId))
        term = TERMS.get(fullId,None)
        #if term:
            #log.info("GOT %s" % fullId)
            
        if term and refresh:
            del TERMS[termId]
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
        
        #log.info("QUERY %s" % query)
        if not term:
            #log.info("query %s" % query)
            res = SdoTermSource.query(query)
            if len(res):
                term = SdoTermSource.termsFromResults(res,termId=fullId)
            elif createReference:
                term = SdoTermSource(fullId).getTermdesc()
            else:
                log.debug("No definition of term %s" % fullId)

        if term and expanded and not term.expanded:
            exterm = EXPANDEDTERMS.get(fullId,None)
            if not exterm:
                exterm = SdoTermSource.expandTerm(term)
                EXPANDEDTERMS[fullId] = exterm
                term.allproperties = []
            term = exterm
                
        return term

def toFullId(termId):

    if not	':' in termId: #Includes full path or namespaces
    	fullId = VOCABURI + termId
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
        
LAYERPATTERN = None
def layerFromUri(uri):
    global LAYERPATTERN
    if uri:
        if not LAYERPATTERN:
            voc = VOCABURI
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
    voc = VOCABURI
    if voc.endswith("/") or voc.endswith('#'):
        voc = voc[:len(voc) - 1]
    if not layer:
        return voc
    prto,root = getProtoAndRoot(voc)
    return "%s%s.%s" % (prto,layer,root)
        
def getProtoAndRoot(uri):
       m = re.search("^(http[s]?:\/\/)(.*)",uri)
       if m:
           prto = m.group(1)
           root = m.group(2)
           return prto,root
       return None,None
         

def uri2id(uri):
    if uri.startswith(VOCABURI):
        return uri[len(VOCABURI):]
    return uri
    

def prefixFromUri(uri):
    uri = str(uri)
    ns = SdoTermSource.SOURCEGRAPH.namespaces()
    for n in ns:
        pref, pth = n
        if uri.startswith(str(pth)):
            return pref
    #log.warning("Requested unknown namespace uri %s" % uri)
    return None
    
def uriForPrefix(pre):
    pre = str(pre)
    ns = SdoTermSource.SOURCEGRAPH.namespaces()
    for n in ns:
        pref, pth = n
        if pre == pref:
            return pth
    #log.warning("Requested unknown prefix %s:" % pre)
    return None
    
    
def prefixedIdFromUri(uri):
    prefix = prefixFromUri(uri)
    if prefix:
        base = os.path.basename(uri)
        if "#" in base:
            base = base.split("#")[1]
        return "%s:%s" % (prefix,base)
    return uri
