#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

# Import standard python libraries

import threading
import os
import re
import sys
import logging
import glob

# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software
import software.SchemaTerms.sdoterm as sdoterm
import software.SchemaTerms.sdotermsource as sdotermsource
import software.SchemaTerms.localmarkdown as localmarkdown

log = logging.getLogger(__name__)


class collaborator():
    COLLABORATORS = {}
    CONTRIBUTORS = {}
    def __init__(self,ref,desc=None):
        self.ref = ref
        self.urirel = "/docs/collab/" + ref
        self.uri = "https://schema.org" + self.urirel
        self.docurl = self.urirel
        self.terms = None
        self.contributor = False
        self.img = self.code = self.title = self.url = None
        self.description = ""
        self.acknowledgement = ""
        self.parseDesc(desc)

        collaborator.COLLABORATORS[self.ref]=self

    def __str__(self):
        return "<collaborator ref: %s uri: %s contributor: %s img: '%s' title: '%s' url: '%s'>" % (self.ref,self.uri,self.contributor,self.img,self.title,self.url)

    def parseDesc(self,desc):
        state = 0
        dt = []
        at = []
        target = None
        for line in desc.splitlines():
            if line.startswith("---"):
                state += 1
            if state == 1:
                if line.startswith("---"):
                    continue
                match = self.matchval('url',line)
                if match:
                    self.url = match
                    continue
                match = self.matchval('title',line)
                if match:
                    self.title = match
                    continue
                match = self.matchval('img',line)
                if match:
                    self.img = match
                    continue
            elif (state > 1):
                if self.matchsep('--- DescriptionText.md',line):
                    target = 'd'
                    continue
                if self.matchsep('--- AcknowledgementText.md',line):
                    target = 'a'
                    continue
                if target:
                    if target == 'a':
                        at.append(line)
                    elif target == 'd':
                        dt.append(line)
        self.description = ''.join(dt)
        self.acknowledgement = ''.join(at)
        self.description = localmarkdown.Markdown.parse(self.description)
        self.acknowledgement = localmarkdown.Markdown.parse(self.acknowledgement)


    def matchval(self,val,line):
        ret = None
        matchstr = "(?i)%s:" % val
        o = re.search(matchstr,line)
        if o:
            ret = line[len(val)+1:]
            ret = ret.strip()
        return ret

    def matchsep(self,val,line):
        line = re.sub(' ', '', line).lower()
        val = re.sub(' ', '', val).lower()
        return line.startswith(val)

    def isContributor(self):
        return self.contributor

    def getTerms(self):
        if not self.contributor:
            return []
        if not self.terms:
            self.terms = sdotermsource.SdoTermSource.getAcknowledgedTerms(self.uri)
        return self.terms


    @classmethod
    def getCollaborator(cls, ref):
        cls.loadCollaborators()
        coll = cls.COLLABORATORS.get(ref,None)
        if not coll:
            log.warning("No such collaborator: %s" % ref)
        return coll

    @classmethod
    def getContributor(cls, ref):
        ref = os.path.basename(ref)
        cls.loadContributors()
        cont = cls.CONTRIBUTORS.get(ref,None)
        if not cont:
            log.warning("No such contributor: %s" % ref)
        return cont

    @classmethod
    def createCollaborator(cls, filename):
        code = os.path.basename(filename)
        ref = os.path.splitext(code)[0]
        coll = None
        try:
            with open(filename,'r') as f:
                desc = f.read()
            coll = cls(ref,desc=desc)
        except Exception as e:
            log.error("Error loading colaborator source %s: %s" % (filename,e))
        return coll

    @classmethod
    def loadCollaborators(cls):
        if not len(cls.COLLABORATORS):
            for filename in glob.glob("data/collab/*.md"):
                cls.createCollaborator(filename)
            log.info("%s Loaded %s collaborators", cls, len(collaborator.COLLABORATORS))

    @classmethod
    def createContributor(cls, ref):
        code = os.path.basename(ref)
        coll = cls.getCollaborator(ref)
        if coll:
            coll.contributor = True
            cls.CONTRIBUTORS[ref]=coll

    @classmethod
    def loadContributors(cls):
        if not len(cls.CONTRIBUTORS):
            cls.loadCollaborators()
            query = """
            SELECT distinct ?val WHERE {
                    [] schema:contributor ?val.
            }"""
            res = sdotermsource.SdoTermSource.query(query)

            for row in res:
                cont = row.val
                cls.createContributor(os.path.basename(str(cont)))
            log.info("%s Loaded %s contributors", cls, len(collaborator.CONTRIBUTORS))

    @classmethod
    def collaborators(cls):
        cls.loadCollaborators()
        return list(cls.COLLABORATORS.values())

    @classmethod
    def contributors(cls):
        cls.loadContributors()
        return list(cls.CONTRIBUTORS.values())
