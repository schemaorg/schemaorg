from __future__ import with_statement
from glob import glob

import sys
if not (sys.version_info.major == 3 and sys.version_info.minor > 5):
    print("Python version %s.%s not supported version 3.6 or above required - exiting" % (sys.version_info.major,sys.version_info.minor))
    sys.exit(1)

import logging
logging.basicConfig(level=logging.INFO) 
log = logging.getLogger(__name__)

import threading
import os
import re
from sdotermsource import SdoTermSource
from localmarkdown import Markdown

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
        self.acknowlegement = ""
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
        self.description = Markdown.parse(self.description)
        self.acknowledgement = Markdown.parse(self.acknowledgement)


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
            self.terms = SdoTermSource.getAcknowledgedTerms(self.uri)
        return self.terms


    @staticmethod
    def getCollaborator(ref):
        collaborator.loadCollaborators()
        coll = collaborator.COLLABORATORS.get(ref,None)
        if not coll:
            print("No such collaborator: %s" % ref)
        return coll

    @staticmethod
    def getContributor(ref):
        ref = os.path.basename(ref)
        collaborator.loadContributors()
        cont = collaborator.CONTRIBUTORS.get(ref,None)
        if not cont:
            print("No such contributor: %s" % ref)
        return cont

    @staticmethod
    def createCollaborator(file):
        code = os.path.basename(file)
        ref = os.path.splitext(code)[0]
        coll = None
        try:
            with open(file,'r') as f:
                desc = f.read()
            coll = collaborator(ref,desc=desc)
        except Exception as e:
            print("Error loading colaborator source %s: %s" % (file,e))

            #raise Exception("Error loading colaborator source %s: %s" % (file,e))

        return coll

    @staticmethod
    def loadCollaborators():
        import glob
        if not len(collaborator.COLLABORATORS):
            for file in glob.glob("data/collab/*.md"):
                collaborator.createCollaborator(file)
            print("Loaded %s collaborators" % len(collaborator.COLLABORATORS))

    @staticmethod
    def createContributor(ref,):
        code = os.path.basename(ref)
        coll = collaborator.getCollaborator(ref)
        if coll:
            coll.contributor = True
            collaborator.CONTRIBUTORS[ref]=coll



    @staticmethod
    def loadContributors():
        if not len(collaborator.CONTRIBUTORS):
            collaborator.loadCollaborators()
            query = """ 
            SELECT distinct ?val WHERE {
                    [] schema:contributor ?val.
            }""" 
            res = SdoTermSource.query(query)

            for row in res:
                cont = row.val
                collaborator.createContributor(os.path.basename(str(cont)))
            print("Loaded %s contributors" % len(collaborator.CONTRIBUTORS))

    @staticmethod
    def collaborators():
        collaborator.loadCollaborators()
        return list(collaborator.COLLABORATORS.values())
    @staticmethod
    def contributors():
        collaborator.loadContributors()
        return list(collaborator.CONTRIBUTORS.values())
