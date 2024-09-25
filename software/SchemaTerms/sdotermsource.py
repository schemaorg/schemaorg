#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Import standard python libraries
import copy
import glob
import localmarkdown
import logging
import os
import rdflib
import re
import sys
import threading

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software
import software.SchemaTerms.sdoterm as sdoterm

log = logging.getLogger(__name__)

DEFVOCABURI = "https://schema.org/"
VOCABURI = None
DATATYPEURI = None
ENUMERATIONURI = None
THINGURI = None

CORE = "core"
DEFTRIPLESFILESGLOB = ("data/*.ttl", "data/ext/*/*.ttl")
LOADEDDEFAULT = False


def _loadOneSourceGraph(file_path):
    """Load the content of one source file."""
    name, extension = os.path.splitext(file_path)
    if extension == ".nt":
        file_format = "nt"
    elif extension == ".ttl":
        file_format = "turtle"
    else:
        raise NotImplementedError("Unsupported file format: %s" % extension)
    try:
        graph = rdflib.Graph()
        graph.parse(source=file_path, format=file_format)
        return graph
    except Exception as e:
        message = "Error parsing source file '%s': %s" % (file_path, e)
        log.warn(message)
        raise IOError(message)


class SdoTermSource:
    TYPE = "Class"
    PROPERTY = "Property"
    DATATYPE = "Datatype"
    ENUMERATION = "Enumeration"
    ENUMERATIONVALUE = "Enumerationvalue"
    REFERENCE = "Reference"
    TERMCOUNTS = None

    SOURCEGRAPH = None
    MARKDOWNPROCESS = True
    EXPANDEDTERMS = {}
    TERMS = {}

    TERMSLOCK = threading.Lock()
    RDFLIBLOCK = threading.Lock()

    def __init__(self, uri, ttype=None, label="", layer=None):
        cls = self.__class__
        global DATATYPEURI, ENUMERATIONURI
        uri = str(uri)
        self.uri = uri
        self.id = uri2id(uri)
        self.label = label
        self.layer = CORE
        if layer:
            self.layer = layer
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
            self.ttype = sdoterm.SdoTerm.TYPE
            if self.uri == str(DATATYPEURI):  # The base DataType is defined as a Class
                self.ttype = sdoterm.SdoTerm.DATATYPE
            elif self.uri == str(
                ENUMERATIONURI
            ):  # The base Enumeration Type is defined as a Class
                self.ttype = sdoterm.SdoTerm.ENUMERATION
            elif self.isEnumeration():
                self.ttype = sdoterm.SdoTerm.ENUMERATION
        elif ttype == rdflib.RDF.Property:
            self.ttype = sdoterm.SdoTerm.PROPERTY
        elif ttype == ENUMERATIONURI:
            self.ttype = sdoterm.SdoTerm.ENUMERATION
        elif ttype == DATATYPEURI:
            self.ttype = sdoterm.SdoTerm.DATATYPE
        elif not ttype:
            self.ttype = sdoterm.SdoTerm.REFERENCE
            self.label = id
        else:
            self.parent = cls._getTerm(str(ttype), createReference=True)

            if self.parent.termType == sdoterm.SdoTerm.ENUMERATION:
                self.ttype = sdoterm.SdoTerm.ENUMERATIONVALUE
            elif self.parent.termType == sdoterm.SdoTerm.DATATYPE:
                self.ttype = sdoterm.SdoTerm.DATATYPE
            else:
                self.ttype = sdoterm.SdoTerm.REFERENCE
                # raise Exception("Unknown parent type '%s' for term: %s" % (ttype, self.uri))

        if self.ttype == sdoterm.SdoTerm.TYPE:
            self.termdesc = sdoterm.SdoType(self.id, self.uri, self.label)
        elif self.ttype == sdoterm.SdoTerm.PROPERTY:
            self.termdesc = sdoterm.SdoProperty(self.id, self.uri, self.label)
        elif self.ttype == sdoterm.SdoTerm.DATATYPE:
            self.termdesc = sdoterm.SdoDataType(self.id, self.uri, self.label)
        elif self.ttype == sdoterm.SdoTerm.ENUMERATION:
            self.termdesc = sdoterm.SdoEnumeration(self.id, self.uri, self.label)
        elif self.ttype == sdoterm.SdoTerm.ENUMERATIONVALUE:
            self.termdesc = sdoterm.SdoEnumerationvalue(self.id, self.uri, self.label)
            if self.parent:
                self.termdesc.enumerationParent = self.parent.id
        elif self.ttype == sdoterm.SdoTerm.REFERENCE:
            self.termdesc = sdoterm.SdoReference(self.id, self.uri, self.label)

        self.termdesc.acknowledgements = self.getAcknowledgements()
        self.termdesc.comment = self.getComment()
        self.termdesc.comments = self.getComments()
        self.termdesc.equivalents = self.getEquivalents()
        self.termdesc.pending = self.inLayers("pending")
        self.termdesc.retired = self.inLayers("attic")
        self.termdesc.extLayer = self.getExtLayer()
        self.termdesc.sources = self.getSources()
        self.termdesc.subs = self.getSubs()
        self.termdesc.supers = self.getSupers()
        self.termdesc.supersededBy = self.getSupersededBy()
        self.termdesc.supersedes = self.getSupersedes()
        self.termdesc.superseded = self.superseded()
        self.termdesc.termStack = self.getTermStack()
        self.termdesc.superPaths = (
            self.getParentPaths()
        )  # MUST be called after supers has been added to self.termdesc

        # Class (Type) Building
        if (
            self.ttype == sdoterm.SdoTerm.TYPE
            or self.ttype == sdoterm.SdoTerm.DATATYPE
            or self.ttype == sdoterm.SdoTerm.ENUMERATION
        ):
            self.termdesc.properties = self.getProperties(getall=False)
            self.termdesc.allproperties = self.getProperties(getall=True)
            self.termdesc.expectedTypeFor = self.getTargetOf()
            if self.ttype == sdoterm.SdoTerm.ENUMERATION:
                if not len(self.termdesc.properties):
                    self.termdesc.termStack = []
            self.termdesc.enumerationMembers = self.getEnumerationMembers()
        elif self.ttype == sdoterm.SdoTerm.PROPERTY:
            self.termdesc.domainIncludes = self.getDomains()
            self.termdesc.rangeIncludes = self.getRanges()
            self.termdesc.inverse = self.getInverseOf()
        elif self.ttype == sdoterm.SdoTerm.ENUMERATIONVALUE:
            pass
        elif self.ttype == sdoterm.SdoTerm.REFERENCE:
            self.termdesc.label = prefixedIdFromUri(self.uri)
            self.termdesc.comment = self.getComment()

        cls.TERMS[self.uri] = self.termdesc

        # log.info("SdoTermSource %s %s" %(self.ttype,self.id))

    def __str__(self):
        return ("<SdoTermSource: %s '%s'>") % (self.ttype, self.id)

    def getTermdesc(self):
        return self.termdesc

    def getType(self):
        return self.ttype

    def isClass(self):
        return self.ttype == sdoterm.SdoTerm.TYPE

    def isProperty(self):
        return self.ttype == sdoterm.SdoTerm.PROPERTY

    def isDataType(self):
        if self.ttype == sdoterm.SdoTerm.DATATYPE:
            return True
        if self.isClass() and not self.checkedDataTypeParents:
            self.checkedDataTypeParents = True
            for super in self.getSupers():
                if super.isDataType():
                    self.ttype = sdoterm.SdoTerm.DATATYPE
                    return True
        return False

    def isEnumeration(self):
        global ENUMERATIONURI
        if self.enum == None:
            query = """
            ASK  {
                    %s rdfs:subClassOf* %s.
             }""" % (uriWrap(toFullId(self.id)), uriWrap(ENUMERATIONURI))
            ret = []
            res = self.__class__.query(query)
            for row in res:
                self.enum = row
        # log.info("res %s" % self.enum)
        return self.enum

        return self.ttype == sdoterm.SdoTerm.ENUMERATION

    def isEnumerationValue(self):
        return self.ttype == sdoterm.SdoTerm.ENUMERATIONVALUE

    def isReference(self):
        return self.ttype == sdoterm.SdoTerm.REFERENCE

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
                log.debug(
                    "Warning '%s' supersededBy more than 1 term (%d)"
                    % (self.id, len(tmp))
                )
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

    def getSources(self):
        if not self.sources:
            objs = self.loadObjects("schema:source")  # To accept later ttl versions.
            self.sources = []
            for obj in objs:
                self.sources.append(obj)
        return self.sources

    def getAcknowledgements(self):
        # Local import to avoid circular import error.
        from sdocollaborators import collaborator

        if not self.aks:
            self.aks = []
            objs = self.loadObjects(
                "schema:contributor"
            )  # To accept later ttl versions.
            for obj in objs:
                cont = collaborator.getContributor(str(obj))
                self.aks.append(cont)
            self.aks = sorted(self.aks, key=lambda t: t.title)
        return self.aks

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
                s = self.__class__._getTerm(sup, createReference=True)
                if s.termType == sdoterm.SdoTerm.REFERENCE:
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

    def getProperties(self, getall=False):
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
                    trm = self.__class__._getTerm(t, createReference=True)
                    if (
                        trm.termType == sdoterm.SdoTerm.TYPE
                        or trm.termType == sdoterm.SdoTerm.DATATYPE
                        or trm.termType == sdoterm.SdoTerm.ENUMERATION
                    ):
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

    def getTargetOf(self, plusparents=False, stopontarget=False):
        global ENUMERATIONURI, THINGURI
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
                    sup = cls._getTerm(s, createReference=True)
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
        return self.equivalents

    def inLayers(self, layers):
        return self.layer in layers

    def getExtLayer(self):
        ret = ""
        lay = self.layer
        if len(lay) and lay != CORE:
            ret = lay
        return ret

    @classmethod
    def subClassOf(cls, child, parent):
        if isinstance(child, str):
            child = cls.getTerm(child)
        if isinstance(parent, str):
            parent = cls.getTerm(parent)

        if child == parent:
            return True

        parents = child.supers
        if parent.id in parents:
            return True

        for p in parents:
            if cls.subClassOf(p, parent):
                return True
        return False

    def loadComment(self):
        comments = self.getComments()
        wpre = None
        name = self.termdesc.id
        if name.startswith(
            "http:"
        ):  # Wikilinks in markdown default to current site - extermals need overriding
            val = os.path.basename(name)
            wpre = name[: len(name) - len(val)]

        first = True
        buf = []
        for com in comments:
            if not first:
                buf.append(" ")
            else:
                first = False
            if self.__class__.MARKDOWNPROCESS:
                buf.append(localmarkdown.Markdown.parse(com, wpre=wpre))
            else:
                buf.append(com)
        ret = "".join(buf)
        if not len(ret):
            ret = ""
        self.comment = ret.strip()

    def loadValue(self, valType):
        ret = self.loadObjects(valType)
        if not ret or len(ret) == 0:
            return None
        return ret[0]

    def loadObjects(self, pred):
        query = """
        SELECT ?val WHERE {
                %s %s ?val.
         }""" % (uriWrap(toFullId(self.id)), uriWrap(pred))
        res = self.__class__.query(query)
        return [row.val for row in res]

    def loadSubjects(self, pred):
        query = """
        SELECT ?sub WHERE {
                ?sub %s %s.
         }""" % (uriWrap(pred), uriWrap(toFullId(self.id)))
        res = self.__class__.query(query)
        return [row.sub for row in res]

    def loadsupers(self):
        fullId = toFullId(self.id)
        query = """
        SELECT ?sup WHERE {
             {
                 %s rdfs:subClassOf ?sup .
             }UNION{
                 %s rdfs:subPropertyOf ?sup .
             }
         }
         ORDER BY ?sup""" % (uriWrap(fullId), uriWrap(fullId))

        res = self.__class__.query(query)
        self.supers = [uri2id(str(row.sup)) for row in res]

    def loadsubs(self):
        fullId = toFullId(self.id)
        if (
            self.ttype == sdoterm.SdoTerm.TYPE
            or self.ttype == sdoterm.SdoTerm.DATATYPE
            or self.ttype == sdoterm.SdoTerm.ENUMERATION
        ):
            sel = "rdfs:subClassOf"
        else:
            sel = "rdfs:subPropertyOf"
        query = """
        SELECT ?sub WHERE {
                ?sub %s %s.
         }ORDER BY ?sub""" % (uriWrap(sel), uriWrap(fullId))
        res = self.__class__.query(query)
        self.subs = [uri2id(str(row.sub)) for row in res]

        if self.ttype == sdoterm.SdoTerm.DATATYPE:
            subjects = self.loadSubjects(
                "a"
            )  # Enumerationvalues have an Enumeration as a type
            self.subs.extend([uri2id(str(child)) for child in subjects])

    def getEnumerationMembers(self):
        if not self.members and self.ttype == sdoterm.SdoTerm.ENUMERATION:
            subjects = self.loadSubjects(
                "a"
            )  # Enumerationvalues have an Enumeration as a type
            self.members = [uri2id(str(child)) for child in subjects]
            self.members.sort()
        return self.members

    def getParentPaths(self, cstack=None):
        self._pstacks = []
        if cstack == None:
            cstack = []
        self._pstacks.append(cstack)
        self._getParentPaths(self.termdesc, cstack)

        inserts = []
        if self.ttype == sdoterm.SdoTerm.PROPERTY:
            inserts = ["Property", "Thing"]
        elif self.ttype == sdoterm.SdoTerm.DATATYPE and self.id != "DataType":
            inserts = ["DataType"]
        elif self.ttype == sdoterm.SdoTerm.TYPE:
            base = self._pstacks[0][0]
            if base != self.id:
                basetype = self.__class__._getTerm(base)
            else:
                basetype = self.termdesc
            if basetype.termType == sdoterm.SdoTerm.DATATYPE:
                inserts = ["DataType"]

        for ins in inserts:
            for s in self._pstacks:
                s.insert(0, ins)

        return self._pstacks

    def _getParentPaths(self, term, cstack):
        cstack.insert(0, term.id)
        tmpStacks = []
        tmpStacks.append(cstack)
        supers = term.supers

        if term.termType == sdoterm.SdoTerm.ENUMERATIONVALUE and term.enumerationParent:
            if term.enumerationParent not in supers:
                supers.append(term.enumerationParent)

        if supers:
            for i in range(len(supers)):
                if i > 0:
                    t = cstack[:]
                    tmpStacks.append(t)
                    self._pstacks.append(t)

            x = 0
            for p in supers:
                if not (p.startswith("http:") or p.startswith("https:")):
                    sup = self.__class__._getTerm(p)
                    self._getParentPaths(sup, tmpStacks[x])
                    x += 1

    @classmethod
    def getParentPathTo(cls, start_term, end_term=None):
        # Output paths from start_term to only if end_term in path
        start_term = cls.getTerm(start_term)
        if not end_term:
            end_term = "Thing"

        superpaths = start_term.superPaths
        outList = []
        for path in superpaths:
            if end_term in path:
                outList.append(path)
        return outList

    @classmethod
    def checkForEnumVal(cls, term):
        if term.ttype == sdoterm.SdoTerm.ENUMERATION:
            return True

        for t in term.supers:
            if cls.checkForEnumVal(t):
                return True
        return False

    @classmethod
    def expandTerms(cls, terms):
        return [cls.expandTerm(t) for t in terms]

    @classmethod
    def expandTerm(cls, termdesc, depth=0):
        termdesc = copy.copy(termdesc)

        if not termdesc.expanded:
            termdesc.expanded = True
            supers = []
            for path in termdesc.superPaths:
                supers.append(SdoTermSource.termsFromIds(path))
            termdesc.superPaths = supers

            termdesc.termStack = cls.termsFromIds(termdesc.termStack)
            termdesc.supers = cls.termsFromIds(termdesc.supers)
            termdesc.subs = cls.termsFromIds(termdesc.subs)
            termdesc.equivalents = cls.termsFromIds(termdesc.equivalents)

            if (
                termdesc.termType == sdoterm.SdoTerm.TYPE
                or termdesc.termType == sdoterm.SdoTerm.DATATYPE
                or termdesc.termType == sdoterm.SdoTerm.ENUMERATION
            ):
                termdesc.properties = cls.termsFromIds(termdesc.properties)
                termdesc.expectedTypeFor = cls.termsFromIds(termdesc.expectedTypeFor)

                if depth < 2:  # Expand the properties but prevent recursion further
                    props = []
                    for p in termdesc.properties:
                        props.append(SdoTermSource.expandTerm(p, depth=depth + 1))
                    termdesc.properties = props
                    expects = []
                    for e in termdesc.expectedTypeFor:
                        expects.append(SdoTermSource.expandTerm(e, depth=depth + 1))
                    termdesc.expectedTypeFor = expects

                if termdesc.termType == sdoterm.SdoTerm.ENUMERATION:
                    termdesc.enumerationMembers = cls.termsFromIds(
                        termdesc.enumerationMembers
                    )
            elif termdesc.termType == sdoterm.SdoTerm.PROPERTY:
                termdesc.domainIncludes = cls.termsFromIds(termdesc.domainIncludes)
                termdesc.rangeIncludes = cls.termsFromIds(termdesc.rangeIncludes)
                termdesc.inverse = cls.termFromId(termdesc.inverse)
            elif termdesc.termType == sdoterm.SdoTerm.ENUMERATIONVALUE:
                termdesc.enumerationParent = cls.termFromId(termdesc.enumerationParent)

            if not depth:  # Expand the individual termdescs in the terms' termstack but prevent recursion further.
                stack = []
                for t in termdesc.termStack:
                    stack.append(SdoTermSource.expandTerm(t, depth=depth + 1))
                termdesc.termStack = stack

        return termdesc

    @classmethod
    def termFromId(cls, id=""):
        ids = cls.termsFromIds([id])
        if len(ids):
            return ids[0]
        return None

    @classmethod
    def termsFromIds(cls, ids=[]):
        ret = []
        for tid in ids:
            if tid and len(tid):
                if type(tid) is str:
                    ret.append(cls._getTerm(tid, createReference=True))
                else:
                    ret.append(tid)
        return ret

    @classmethod
    def termsFromResults(cls, res, termId=None):
        ret = []
        single = False
        if termId:
            single = True
        tmp = cls.TmpTerm(termId)
        count = 0
        for row in res:  # Assumes termdefinition rows are ordered by termId
            if not single:
                termId = str(row.term)
            if tmp.id != termId:  # New term definition starts on this row
                if tmp.id:
                    term = cls.createTerm(tmp)
                    if term:
                        ret.append(term)
                        count += 1
                tmp = cls.TmpTerm(termId)
            tmp.types.append(row.type)
            tmp.sups.append(row.sup)
            tmp.tt = row.type
            tmp.lab = row.label
            tmp.layer = layerFromUri(row.layer)

        term = cls.createTerm(tmp)
        if term:
            ret.append(term)
            count += 1

        if single:
            return ret[0]
        else:
            return ret

    @classmethod
    def createTerm(cls, tmp):
        global DATATYPEURI, ENUMERATIONURI
        if not tmp or not tmp.id:
            return None

        if DATATYPEURI in tmp.types:
            tmp.tt = DATATYPEURI
        elif ENUMERATIONURI in tmp.sups:
            tmp.tt = ENUMERATIONURI

        term = cls.TERMS.get(tmp.id, None)
        if not term:  # Already created this term ?
            t = cls(tmp.id, ttype=tmp.tt, label=tmp.lab, layer=tmp.layer)
            term = t.termdesc
        return term

    class TmpTerm:
        def __init__(self, id):
            self.id = id
            self.types = []
            self.sups = []
            self.lab = None
            self.layer = None
            self.tt = ""

    @classmethod
    def triples4Term(cls, termId):
        term = cls.getTerm(termId)
        g = cls.SOURCEGRAPH
        triples = g.triples((rdflib.URIRef(term.uri), None, None))
        return triples

    @classmethod
    def getTermAsRdfString(cls, termId, format, full=False):
        global VOCABURI
        term = cls.getTerm(termId)
        if not term or term.termType == sdoterm.SdoTerm.REFERENCE:
            return ""
        g = rdflib.Graph()

        schema = rdflib.Namespace(VOCABURI)
        g.bind("schema", VOCABURI)

        if not full:  # Only the term definition
            triples = cls.triples4Term(term)
            for trip in triples:
                g.add(trip)
        else:  # full - Include all related terms
            types = []
            props = []
            stack = [term]

            stack.extend(SdoTermSource.termsFromIds(term.termStack))
            for t in stack:
                if t.termType == sdoterm.SdoTerm.PROPERTY:
                    props.append(t)
                else:
                    types.append(t)
                    if t.termType == sdoterm.SdoTerm.ENUMERATIONVALUE:
                        types.append(SdoTermSource.termFromId(t.enumerationParent))
                    elif t == stack[0]:
                        props.extend(SdoTermSource.termsFromIds(t.allproperties))

            for t in types:
                triples = cls.triples4Term(t.id)
                for trip in triples:
                    g.add(trip)

            for p in props:
                triples = cls.triples4Term(p.id)
                for trip in triples:
                    g.add(trip)

        kwargs = {"sort_keys": True}
        if format == "rdf":
            format = "pretty-xml"
        ret = g.serialize(format=format, auto_compact=True, **kwargs)
        return ret

    @classmethod
    def getAllTypes(cls, layer=None, expanded=False):
        return cls.getAllTerms(
            ttype=sdoterm.SdoTerm.TYPE, layer=layer, expanded=expanded
        )

    @classmethod
    def getAllProperties(cls, layer=None, expanded=False):
        return cls.getAllTerms(
            ttype=sdoterm.SdoTerm.PROPERTY, layer=layer, expanded=expanded
        )

    @classmethod
    def getAllEnumerations(cls, layer=None, expanded=False):
        return cls.getAllTerms(
            ttype=sdoterm.SdoTerm.ENUMERATION, layer=layer, expanded=expanded
        )

    @classmethod
    def getAllEnumerationvalues(cls, layer=None, expanded=False):
        return cls.getAllTerms(
            ttype=sdoterm.SdoTerm.ENUMERATIONVALUE, layer=layer, expanded=expanded
        )

    @classmethod
    def getAllTerms(
        cls, ttype=None, layer=None, suppressSourceLinks=False, expanded=False
    ):
        global DATATYPEURI, ENUMERATIONURI
        typsel = ""
        extra = ""
        if ttype == sdoterm.SdoTerm.TYPE:
            typsel = "a <%s>;" % rdflib.RDFS.Class
        elif ttype == sdoterm.SdoTerm.PROPERTY:
            typsel = "a <%s>;" % rdflib.RDF.Property
        elif ttype == sdoterm.SdoTerm.DATATYPE:
            typsel = "a <%s>;" % DATATYPEURI
        elif ttype == sdoterm.SdoTerm.ENUMERATION:
            typsel = "rdfs:subClassOf* <%s>;" % ENUMERATIONURI
        elif ttype == sdoterm.SdoTerm.ENUMERATIONVALUE:
            extra = "?type rdfs:subClassOf*  <%s>." % ENUMERATIONURI
        elif not ttype:
            typesel = ""
        else:
            log.debug("Invalid type value '%s'" % ttype)

        laysel = ""
        fil = ""
        suppress = ""
        if layer:
            if layer == "core":
                fil = "FILTER NOT EXISTS { ?term schema:isPartOf ?x. }"
            else:
                laysel = "schema:isPartOf <%s>;" % uriFromLayer(layer)

        if suppressSourceLinks:
            suppress = "FILTER NOT EXISTS { ?s dc:source ?term. }"

        query = """SELECT DISTINCT ?term ?type ?label ?layer ?sup WHERE {
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
            %s
            %s
        }
        ORDER BY ?term
        """ % (typsel, laysel, extra, fil, suppress)

        # log.info("query %s" % query)
        res = cls.query(query)
        # log.info("res %d" % len(res))

        terms = []
        if expanded:
            terms = cls.termsFromResults(res, termId=None)
        else:
            for row in res:
                term = uri2id(str(row.term))
                if not term in terms:
                    terms.append(term)

        log.info("count %s TERMS %s" % (len(terms), len(cls.TERMS)))
        return terms

    @classmethod
    def getAcknowledgedTerms(cls, ack):
        query = (
            """SELECT DISTINCT ?term ?type ?label ?layer ?sup WHERE {
             ?term a ?type;
                schema:contributor <%s>;
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
            }
            ORDER BY ?term
            """
            % ack
        )
        res = cls.query(query)
        terms = cls.termsFromResults(res, termId=None)
        return terms

    @classmethod
    def setSourceGraph(cls, g):
        global VOCABURI
        cls.SOURCEGRAPH = g
        g.bind("schema", VOCABURI)
        g.bind("owl", "http://www.w3.org/2002/07/owl#")
        g.bind("dc", "http://purl.org/dc/elements/1.1/")
        g.bind("dct", "http://purl.org/dc/terms/")
        g.bind("dctype", "http://purl.org/dc/dcmitype/")
        g.bind("void", "http://rdfs.org/ns/void#")
        g.bind("dcat", "http://www.w3.org/ns/dcat#")

        cls.TERMS = {}  # Clear cache
        cls.EXPANDEDTERMS = {}

    @classmethod
    def loadSourceGraph(cls, files=None, init=False, vocaburi=None):
        global VOCABURI, DEFTRIPLESFILESGLOB
        if init:
            cls.SOURCEGRAPH = None
        if not VOCABURI and not vocaburi:
            cls.setVocabUri(DEFVOCABURI)
        elif vocaburi:
            cls.setVocabUri(vocaburi)

        if not files or files == "default":
            if cls.SOURCEGRAPH:
                if not cls.LOADEDDEFAULT:
                    raise Exception(
                        "Sourcegraph already loaded - cannot overwrite with defaults"
                    )
                log.info("Default files already loaded")
                return

            else:
                cls.LOADEDDEFAULT = True
                log.info(
                    "SdoTermSource.loadSourceGraph() loading from default files found in globs: %s",
                    ",".join(DEFTRIPLESFILESGLOB),
                )
                files = []
                for g in DEFTRIPLESFILESGLOB:
                    files.extend(glob.glob(g))
        elif isinstance(files, str):
            cls.LOADEDDEFAULT = False
            log.info("SdoTermSource.loadSourceGraph() loading from file: %s", files)
            files = [files]
        else:
            cls.LOADEDDEFAULT = False
            log.info(
                "SdoTermSource.loadSourceGraph() loading from %d files", len(files)
            )

        if not len(files):
            raise Exception("No triples file(s) to load")

        cls.setSourceGraph(rdflib.Graph())

        for file_path in files:
            cls.SOURCEGRAPH += _loadOneSourceGraph(file_path)
        log.info(
            "Loaded %s triples - %s terms",
            len(SdoTermSource.sourceGraph()),
            len(SdoTermSource.getAllTerms()),
        )

    @classmethod
    def sourceGraph(cls):
        if cls.SOURCEGRAPH == None:
            cls.loadSourceGraph()
        return cls.SOURCEGRAPH

    @staticmethod
    def setVocabUri(u=None):
        global VOCABURI, DATATYPEURI, ENUMERATIONURI, THINGURI
        VOCABURI = u or DEFVOCABURI
        DATATYPEURI = rdflib.URIRef(VOCABURI + "DataType")
        ENUMERATIONURI = rdflib.URIRef(VOCABURI + "Enumeration")
        THINGURI = rdflib.URIRef(VOCABURI + "Thing")

    @classmethod
    def vocabUri(cls):
        global VOCABURI
        if not VOCABURI:
            cls.setVocabUri()
        return VOCABURI

    @classmethod
    def getNamespaces(cls):
        list(cls.SOURCEGRAPH.namespaces())

    @classmethod
    def query(cls, q):
        graph = cls.sourceGraph()
        with cls.RDFLIBLOCK:
            ret = list(graph.query(q))
        return ret

    @staticmethod
    def term2str(t):
        terms = t
        if not isinstance(t, list):
            terms = [t]
        return map(str, terms)

    @staticmethod
    def term2id(t):
        terms = t
        if not isinstance(t, list):
            terms = [t]
        return [term.getId() for term in terms]

    @classmethod
    def termCounts(cls):
        global VOCABURI
        if not cls.TERMCOUNTS:
            count = (
                """SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {
                ?s a ?type .
                FILTER (strStarts(str(?s),"%s"))
            } """
                % VOCABURI
            )
            res = cls.query(count)
            allterms = int(res[0][0])

            count = (
                """SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {
                ?s a rdfs:Class .
                FILTER (strStarts(str(?s),"%s"))
            } """
                % VOCABURI
            )
            res = cls.query(count)
            classes = int(res[0][0])

            count = (
                """SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {
                ?s a rdf:Property .
                FILTER (strStarts(str(?s),"%s"))
            } """
                % VOCABURI
            )
            res = cls.query(count)
            properties = int(res[0][0])

            count = (
                """SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {
                ?s rdfs:subClassOf* schema:Enumeration .
                FILTER (strStarts(str(?s),"%s"))
            } """
                % VOCABURI
            )
            res = cls.query(count)
            enums = int(res[0][0])

            count = (
                """SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {
                ?s a ?type .
                ?type rdfs:subClassOf* schema:Enumeration .
                FILTER (strStarts(str(?s),"%s"))
            } """
                % VOCABURI
            )
            res = cls.query(count)
            enumvals = int(res[0][0])

            count = (
                """SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {
                {
                    ?s a schema:DataType .
                }UNION{
                    ?s rdf:type* schema:DataType .
                }UNION{
                    ?s rdfs:subClassOf* ?x .
                    ?x a schema:DataType .
                }
                FILTER (strStarts(str(?s),"%s"))
           } """
                % VOCABURI
            )
            res = cls.query(count)
            datatypes = int(res[0][0])

            count = (
                """SELECT (COUNT(DISTINCT ?s) as ?count) WHERE {
                ?s rdfs:subClassOf* ?x .
                ?x a schema:DataType .
                FILTER (strStarts(str(?s),"%s"))
           } """
                % VOCABURI
            )
            res = cls.query(count)
            datatypeclasses = int(res[0][0])

            types = classes
            types -= 1  # DataType not counted
            types -= enums
            types -= datatypeclasses
            datatypes -= 1  # Datatype not counted

            cls.TERMCOUNTS = {}
            cls.TERMCOUNTS[SdoTerm.TYPE] = types
            cls.TERMCOUNTS[SdoTerm.PROPERTY] = properties
            cls.TERMCOUNTS[SdoTerm.DATATYPE] = datatypes
            cls.TERMCOUNTS[SdoTerm.ENUMERATION] = enums
            cls.TERMCOUNTS[SdoTerm.ENUMERATIONVALUE] = enumvals
            cls.TERMCOUNTS["All"] = types + properties + datatypes + enums + enumvals
        return cls.TERMCOUNTS

    @classmethod
    def setMarkdownProcess(cls, process):
        cls.MARKDOWNPROCESS = process

    @classmethod
    def termCache(cls):
        return cls.TERMS

    @classmethod
    def getTerm(cls, termId, expanded=False, refresh=False, createReference=False):
        with cls.TERMSLOCK:
            return cls._getTerm(
                termId,
                expanded=expanded,
                refresh=refresh,
                createReference=createReference,
            )

    @classmethod
    def _getTerm(cls, termId, expanded=False, refresh=False, createReference=False):
        if not termId:
            return None

        termId = str(termId).strip()
        fullId = toFullId(termId)
        term = cls.TERMS.get(fullId, None)

        if term and refresh:
            del cls.TERMS[termId]
            log.info("Term '%s' found and removed" % termId)
            term = None

        query = """
        SELECT ?term ?type ?label ?layer ?sup WHERE {
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

        }""" % (uriWrap(fullId), uriWrap(fullId), uriWrap(fullId), uriWrap(fullId))

        if not term:
            res = cls.query(query)
            if len(res):
                term = cls.termsFromResults(res, termId=fullId)
            elif createReference:
                # Create a new TermSource
                term = cls(fullId).getTermdesc()
            else:
                log.warning("No definition of term %s" % fullId)

        if term and expanded and not term.expanded:
            exterm = cls.EXPANDEDTERMS.get(fullId, None)
            if not exterm:
                exterm = cls.expandTerm(term)
                cls.EXPANDEDTERMS[fullId] = exterm
            term = exterm

        return term


def toFullId(termId):
    global VOCABURI
    if not ":" in termId:  # Includes full path or namespaces
        fullId = VOCABURI + termId

    elif termId.startswith("http"):
        fullId = termId
    else:
        sp = termId.split(":")
        pre = sp[0]
        id = sp[1]
        fullId = "%s%s" % (uriForPrefix(pre), id)
    return fullId


def uriWrap(id):
    if id.startswith("http://") or id.startswith("https://"):
        id = "<%s>" % id
    return id


LAYERPATTERN = None


def layerFromUri(uri):
    global VOCABURI
    global LAYERPATTERN
    if uri:
        if not LAYERPATTERN:
            voc = VOCABURI
            if voc.endswith("/") or voc.endswith("#"):
                voc = voc[: len(voc) - 1]
            prto, root = getProtoAndRoot(voc)
            LAYERPATTERN = "^%s([\w]*)\.%s" % (prto, root)

        if LAYERPATTERN:
            m = re.search(LAYERPATTERN, str(uri))
            if m:
                return m.group(1)
    return None


def uriFromLayer(layer=None):
    global VOCABURI
    voc = VOCABURI
    if voc.endswith("/") or voc.endswith("#"):
        voc = voc[: len(voc) - 1]
    if not layer:
        return voc
    prto, root = getProtoAndRoot(voc)
    return "%s%s.%s" % (prto, layer, root)


def getProtoAndRoot(uri):
    m = re.search("^(http[s]?:\/\/)(.*)", uri)
    if m:
        prto = m.group(1)
        root = m.group(2)
        return prto, root
    return None, None


def uri2id(uri):
    global VOCABURI
    if uri.startswith(VOCABURI):
        return uri[len(VOCABURI) :]
    return uri


def prefixFromUri(uri):
    uri = str(uri)
    ns = SdoTermSource.SOURCEGRAPH.namespaces()
    for pref, pth in ns:
        if uri.startswith(str(pth)):
            return pref
    return None


def uriForPrefix(pre):
    pre = str(pre)
    ns = cls.SOURCEGRAPH.namespaces()
    for pref, pth in ns:
        if pre == pref:
            return pth
    return None


def prefixedIdFromUri(uri):
    prefix = prefixFromUri(uri)
    if prefix:
        base = os.path.basename(uri)
        if "#" in base:
            base = base.split("#")[1]
        return "%s:%s" % (prefix, base)
    return uri
