#!/usr/bin/env python3
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

IDPREFIX = "eg-"

class Example ():
    ExamplesCount = 0
    MaxId = 0

    def __init__ (self, terms, original_html, microdata, rdfa, jsonld, exmeta):
        self.terms = terms
        if not len(terms):
            log.info("No terms for ex: %s in file %s" % (exmeta["filepos"],emeta["file"]) )
        self.original_html = original_html
        self.microdata = microdata
        self.rdfa = rdfa
        self.jsonld = jsonld
        self.exmeta = exmeta
        self.keyvalue = self.exmeta.get('id',None)
        if not self.keyvalue:
            self.keyvalue = "%s-temp-%s"% (terms[0],Example.ExamplesCount)
            self.exmeta['id'] = self.keyvalue
        else:
            idnum = self.getIdNum()
            if idnum > -1:
                Example.MaxId = max(Example.MaxId,idnum)
                self.keyvalue = Example.formatId(idnum)
        Example.ExamplesCount += 1

    def getKey(self):
        return self.keyvalue
    def setKey(self,key):
        self.keyvalue = key
        
    def terms(self):
        return self.terms
    def setTerms(self,terms):
        self.terms = terms
        
    def getHtml(self):
        return self.original_html
    def setHtml(self,content):
        self.original_html = content
        
    def getMicrodata(self):
        return self.microdata
    def setMicrodata(self,content):
        self.microdata = content
        
    def getRdfa(self):
        return self.rdfa
    def setRdfa(self,content):
        self.rdfa = content
        
    def getJsonld(self):
        return self.jsonld
    def setJsonld(self,content):
        self.jsonld = content

    def hasHtml(self):
        return len(self.original_html.strip()) > 0
    def hasMicrodata(self):
        return len(self.microdata.strip()) > 0
    def hasRdfa(self):
        return len(self.rdfa.strip()) > 0
    def hasJsonld(self):
        return len(self.jsonld.strip()) > 0
        
    def setMeta(self,name,val):
        self.exmeta[name] = val
    def getMeta(self,name):
        return self.exmeta.get(name,None)
        
    def getIdNum(self):
        idnum = -1
        if self.keyvalue.startswith(IDPREFIX):
            try:
                idnum = int(self.keyvalue[len(IDPREFIX):])
            except:
                pass
        return idnum

    def hasValidId(self):
        return self.getIdNum() > -1
        

    def serialize(self):
        buff = []
        termnames = ""
        first = True
        idd = "#%s" % self.keyvalue
        if "-temp-" in idd:
            idd = ""
        for t in self.terms:
            if first:
                first = False
            else:
                termnames += ", "
            termnames += t
            
        buff.append("TYPES: %s %s\n" % (idd,termnames))
        buff.append("PRE-MARKUP:\n%s" % self.getHtml())
        buff.append("MICRODATA:\n%s" % self.getMicrodata())
        buff.append("RDFA:\n%s" % self.getRdfa())
        buff.append("JSON:\n%s" % self.getJsonld())
        return "\n".join(buff)
        
    @staticmethod
    def nextId():
        Example.MaxId += 1
        return Example.formatId(Example.MaxId)
        
    @staticmethod
    def formatId(val):
        return 'eg-{0:04d}'.format(val)

    @staticmethod
    def nextIdReset(val=None):
        if not val:
            val = 0
        Example.MaxId = val

class SchemaExamples():
    
    EXAMPLESMAP = {}
    EXAMPLES = {}    
    exlock = threading.RLock()
    
    
    @staticmethod
    def loadExamplesFile(exfile):
        return SchemaExamples.loadExamplesFiles([exfile])
    

    @staticmethod
    def loadExamplesFiles(exfiles):
        parser = ExampleFileParser()
        for f in exfiles:
            for example in parser.parse(f):
                #log.info("Ex: %s %s" % (example.keyvalue,example.terms))
                keyvalue = example.keyvalue
                with SchemaExamples.exlock:
                    if not SchemaExamples.EXAMPLES.get(keyvalue,None):
                        SchemaExamples.EXAMPLES[keyvalue] = example

                    for term in example.terms:
                
                        if(not SchemaExamples.EXAMPLESMAP.get(term, None)):
                            SchemaExamples.EXAMPLESMAP[term] = []
                    
                        if not keyvalue in SchemaExamples.EXAMPLESMAP.get(term):
                            SchemaExamples.EXAMPLESMAP.get(term).append(keyvalue)
                
            
    @staticmethod
    def examplesForTerm(term):
        examples = []
        examps = SchemaExamples.EXAMPLESMAP.get(term)
        if examps:
            for e in examps:
                ex = SchemaExamples.EXAMPLES.get(e)
                if ex:
                    examples.append(ex)
        return examples

    @staticmethod
    def allExamples(sort=False):
        ret = SchemaExamples.EXAMPLES.values()
        if sort:
            return sorted(ret, key=lambda x: (x.exmeta['file'],x.exmeta['filepos']))
        return ret
            
            
    @staticmethod
    def count():
        return len(SchemaExamples.EXAMPLES)


class ExampleFileParser():

    def __init__ (self):
        logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
        self.file = ""
        self.filepos = 0
        self.initFields()
        self.idcache = []

    def initFields(self):
        self.currentStr = []
        self.terms = []
        self.exmeta = {}
        self.preMarkupStr = ""
        self.microdataStr = ""
        self.rdfaStr = ""
        self.jsonStr = ""
        self.state= ""

    def nextPart(self, next):
        self.trimCurrentStr() 
        
        if (self.state == 'PRE-MARKUP:'):
            self.preMarkupStr = "".join(self.currentStr)
        elif (self.state ==  'MICRODATA:'):
            self.microdataStr = "".join(self.currentStr)
        elif (self.state == 'RDFA:'):
            self.rdfaStr = "".join(self.currentStr)
        elif (self.state == 'JSON:'):
            self.jsonStr = "".join(self.currentStr)
        self.state = next
        self.currentStr = []
        
    def trimCurrentStr(self):
        #strip: leading blank lines, strip multi blank lines (replace with 1) end with blank line
        temp = []
        begin = True
        inwhitespace = False
        
        for line in self.currentStr:
            linelen = len(line.strip())
            if not linelen:
                if begin:
                    continue
                else:
                    inwhitespace = True
            else:
                if begin:
                    temp.append("\n")
                    begin = False
                if inwhitespace:
                    temp.append("\n")
                    inwhitespace = False
                temp.append(line+"\n")
                
        if not inwhitespace:
            temp.append("\n")
        self.currentStr = temp

    def process_example_id(self, m):
        ident = m.group(1)
        if ident not in self.idcache:
            self.idcache.append(ident)
        else:
            raise Exception("Example %s in file %s has duplicate ident: '%s'" % (self.filepos,self.file,ident))
        self.exmeta["id"] = ident
        return ''

    def parse (self, filen):
        import codecs
        self.file = filen
        self.filepos = 0
        examples = []
        egid = re.compile("""#(\S+)\s+""")
        
        if self.file.startswith("file://"):
            self.file = self.file[7:]
        
        if "://" in self.file:
            content = urllib.urlopen(self.file).read().decode("utf8")
        else:
            fd = codecs.open(self.file, 'r', encoding="utf8")
            content = fd.read()
            fd.close()
        
        lines = re.split('\n|\r', content)
        first = True
        boilerplate = False
        for line in lines:
            # Per-example sections begin with e.g.: 'TYPES: #music-2 Person, MusicComposition, Organization'
            line = line.rstrip()

            if line.startswith("TYPES:"):
                self.filepos += 1
                self.nextPart('TYPES:')
                #Create example from what has been previously collected
                if first:
                    first = False
                else:
                    if not boilerplate:
                        examples.append(Example(self.terms, self.preMarkupStr, self.microdataStr, self.rdfaStr, self.jsonStr, self.exmeta))
                    boilerplate = False
                    self.initFields()
                self.exmeta['file'] = self.file
                self.exmeta['filepos'] = self.filepos
                typelist = re.split(':', line)
                tdata = egid.sub(self.process_example_id, typelist[1]) # strips IDs, records them in exmeta["id"]
                ttl = tdata.split(',')
                for ttli in ttl:
                    ttli = ttli.strip()
                    if len(ttli):
                        if "@@" not in ttli and not "FakeEntryNeeded" in ttli:
                            self.terms.append(ttli)
                        else:
                            boilerplate = True
            else:
                tokens = ["PRE-MARKUP:", "MICRODATA:", "RDFA:", "JSON:"]
                for tk in tokens:
                    ltk = len(tk)
                    if line.startswith(tk):
                        self.nextPart(tk)
                        line = line[ltk:]
                self.currentStr.append(line)
        self.nextPart('TYPES:') # should flush on each block of examples
        self.filepos += 1
        if not boilerplate:
            examples.append(Example(self.terms, self.preMarkupStr, self.microdataStr, self.rdfaStr, self.jsonStr, self.exmeta)) # should flush last one
        return examples



