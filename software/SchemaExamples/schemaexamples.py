#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

import logging
import os
import io
import glob
import re
import threading

IDPREFIX = "eg-"
DEFTEXAMPLESFILESGLOB = ("data/*examples.txt","data/ext/*/*examples.txt")
NO_JSON_REGEXPS = (
    re.compile('No JSON-?LD',re.I),
    re.compile('This example is in microdata only',re.I),
    re.compile('No Json example available',re.I),
    re.compile('microdata only', re.I))


ldscript_match = re.compile('[\s\S]*<\s*script\s+type="application\/ld\+json"\s*>(.*)<\s*\/script\s*>[\s\S]*',re.S)


log = logging.getLogger(__name__)


class Example():
    """Representation of an example file, with accessors for the various parts."""
    ExamplesCount = 0
    MaxId = 0

    def __init__ (self, terms, original_html, microdata, rdfa, jsonld, exmeta, jsonld_offset=None):
        self.terms = terms
        if not len(terms):
            log.info("No terms for ex: %s in file %s" % (exmeta["filepos"],exmeta["file"]) )
            first_term = 'Empty'
        else:
            first_term = terms[0]
        self.original_html = original_html
        self.microdata = microdata
        self.rdfa = rdfa
        self.jsonld = jsonld
        self.jsonld_offset = jsonld_offset
        self.exmeta = exmeta
        self.keyvalue = self.exmeta.get('id',None)
        if not self.keyvalue:
            self.keyvalue = "%s-temp-%s"% (first_term,Example.ExamplesCount)
            self.exmeta['id'] = self.keyvalue
        else:
            idnum = self.getIdNum()
            if idnum > -1:
                Example.MaxId = max(Example.MaxId,idnum)
                self.keyvalue = Example.formatId(idnum)
        Example.ExamplesCount += 1

    def __str__(self):
        buf = []
        buf.append("Example: \nTerms: ")
        if not len(self.terms):
            buf.append("No Terms!")
        else:
            buf.append("%s" % self.terms)
        buf.append("\nKeyvalue: %s" % self.keyvalue)
        buf.append("\nOrigLen: %s MicroLen: %s RdfaLen: %s JsonLen: %s" % (len(self.original_html),len(self.microdata),len(self.rdfa),len(self.jsonld)))
        buf.append("\nexmeta: %s" % self.exmeta)
        return ''.join(buf)

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

    def getJsonldRaw(self):
        jsondata = self.getJsonld()
        jsondata = jsondata.strip()
        if len(jsondata):
            jsonmatch = ldscript_match.match(jsondata)
            if jsonmatch:
                #extract json from within script tag
                jsondata = jsonmatch.group(1).strip()
        return jsondata

    def setJsonld(self,content):
        self.jsonld = content

    def hasHtml(self):
        return len(self.original_html.strip()) > 0

    def hasMicrodata(self):
        content = self.microdata.strip()
        if len(content) > 0:
            if "itemtype" in content and "itemprop" in content:
                return True
        return False
    def hasRdfa(self):
        content = self.rdfa.strip()
        if len(content) > 0:
            if "typeof" in content and "property" in content:
                return True
        return False

    def hasJsonld(self):
        """Return True if there is real JSON, and not a placehold comment in the JSON section."""
        json_content = self.getJsonldRaw()
        if not json_content:
            return False
        for reg in NO_JSON_REGEXPS:
            if reg.match(json_content):
                return False
        if json_content:
            if "@type" in json_content:
                return True
        return False

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
       termnames = ', '.join(self.terms)
       idd = "#%s" % self.keyvalue
       if "-temp-" in idd:
           idd = ""

       sections = [
         "TYPES: %s %s\n" % (idd, termnames),
         "PRE-MARKUP:", self.getHtml(),
         "MICRODATA:", self.getMicrodata(),
         "RDFA:", self.getRdfa(),
         "JSON:", self.getJsonld(),
       ]
       return "\n".join(sections)

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

    EXAMPLESLOADED=False
    EXAMPLESMAP = {}
    EXAMPLES = {}
    exlock = threading.RLock()


    @staticmethod
    def loadExamplesFiles(exfiles,init=False):
        global DEFTEXAMPLESFILESGLOB
        if init:
            EXAMPLESLOADED=False
            EXAMPLESMAP = {}
            EXAMPLES = {}

        if SchemaExamples.EXAMPLESLOADED:
            log.info("Examples files already loaded")
            return

        if not exfiles or exfiles == "default":
            log.info("SchemaExamples.loadExamplesFiles() loading from default files found in globs: %s" % ','.join(DEFTEXAMPLESFILESGLOB))
            exfiles = []
            for g in DEFTEXAMPLESFILESGLOB:
                exfiles.extend(glob.glob(g))
        elif isinstance(exfiles, str):
            log.info("SchemaExamples.loadExamplesFiles() loading from file: %s" % exfiles)
            exfiles = [exfiles]
        else:
             log.info("SchemaExamples.loadExamplesFiles() loading from %d" % len(exfiles))

        if not len(exfiles):
            raise Exception("No examples file(s) to load")


        parser = ExampleFileParser()
        for f in exfiles:
            for example in parser.parse(f):
                #log.info("Ex: %s %s" % (example.keyvalue,example.terms))
                keyvalue = example.keyvalue
                example.setMeta("source",f)
                with SchemaExamples.exlock:
                    if not SchemaExamples.EXAMPLES.get(keyvalue,None):
                        SchemaExamples.EXAMPLES[keyvalue] = example

                    for term in example.terms:
                        if(not SchemaExamples.EXAMPLESMAP.get(term, None)):
                            SchemaExamples.EXAMPLESMAP[term] = []

                        if not keyvalue in SchemaExamples.EXAMPLESMAP.get(term):
                            SchemaExamples.EXAMPLESMAP.get(term).append(keyvalue)
        SchemaExamples.EXAMPLESLOADED = True

    @staticmethod
    def loaded():
        if not SchemaExamples.EXAMPLESLOADED:
            log.info("Loading examples files")
            SchemaExamples.loadExamplesFiles("default")
            log.info("Loaded %d examples", SchemaExamples.count())


    @staticmethod
    def examplesForTerm(term):
        SchemaExamples.loaded()
        examples = []
        examps = SchemaExamples.EXAMPLESMAP.get(term)
        if examps:
            for e in examps:
                ex = SchemaExamples.EXAMPLES.get(e)
                if ex:
                    examples.append(ex)
        return sorted(examples,key=lambda x: x.keyvalue)

    @staticmethod
    def allExamples(sort=False):
        SchemaExamples.loaded()
        ret = SchemaExamples.EXAMPLES.values()
        if sort:
            return sorted(ret, key=lambda x: (x.exmeta['file'],x.exmeta['filepos']))
        return ret

    @staticmethod
    def allExamplesSerialised(sort=False):
        SchemaExamples.loaded()
        examples = SchemaExamples.allExamples(sort=sort)
        f = io.StringIO()
        for ex in examples:
            f.write(ex.serialize())
            f.write("\n")
        return f.getvalue()

    @staticmethod
    def count():
        SchemaExamples.loaded()
        return len(SchemaExamples.EXAMPLES)


class ExampleFileParser():

    def __init__ (self):
        logging.basicConfig(level=logging.INFO) # dev_appserver.py --log_level debug .
        self.file = ""    # File being parsed.
        self.filepos = 0  # Part index.
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
        self.jsonld_offset = None
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
            raise Exception("Example %s in file %s has duplicate identifier: '%s'" % (self.filepos,self.file,ident))
        self.exmeta["id"] = ident
        return ''

    def makeExample(self):
        """Build an example out of the current state"""
        return Example(
            terms=self.terms, original_html=self.preMarkupStr, microdata=self.microdataStr, rdfa=self.rdfaStr,
            jsonld=self.jsonStr, exmeta=self.exmeta, jsonld_offset=self.jsonld_offset)

    def parse (self, filen):
        import codecs
        import requests
        self.file = filen
        self.filepos = 0
        examples = []
        egid = re.compile("""#(\S+)\s+""")

        if self.file.startswith("file://"):
            self.file = self.file[7:]

        if "://" in self.file:
            r = requests.get(self.file)
            content = r.text
        else:
            fd = codecs.open(self.file, 'r', encoding="utf8")
            content = fd.read()
            fd.close()

        lines = re.split('\n|\r', content)
        first = True
        boilerplate = False
        for lineno, line in enumerate(lines):
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
                        examples.append(self.makeExample())
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
                # Heuristic to find the start line that will be used by `getJsonldRaw`.
                if '<script type="application/ld+json">' in line:
                    self.jsonld_offset = lineno + 1
                tokens = ("PRE-MARKUP:", "MICRODATA:", "RDFA:", "JSON:")
                for tk in tokens:
                    ltk = len(tk)
                    if line.startswith(tk):
                        self.nextPart(tk)
                        line = line[ltk:]
                self.currentStr.append(line)
        self.nextPart('TYPES:') # should flush on each block of examples
        self.filepos += 1
        if not boilerplate:
            self.exmeta['file'] = self.file
            self.exmeta['filepos'] = self.filepos
            examples.append(self.makeExample()) # should flush last one
        self.initFields()
        return examples



