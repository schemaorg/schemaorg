#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import os
import io
import glob
import re
import threading
import typing
from typing import Any, Dict, List, Optional, Tuple, Union, Iterable, Sequence, Set, Collection

IDPREFIX: str = "eg-"
DEFTEXAMPLESFILESGLOB: Tuple[str, str] = ("data/*examples.txt", "data/ext/*/*examples.txt")
NO_JSON_REGEXPS: Tuple[re.Pattern, ...] = (
    re.compile("No JSON-?LD", re.I),
    re.compile("This example is in microdata only", re.I),
    re.compile("No Json example available", re.I),
    re.compile("microdata only", re.I),
)


ldscript_match: re.Pattern = re.compile(
    r'[\s\S]*<\s*script\s+type="application\/ld\+json"\s*>(.*)<\s*\/script\s*>[\s\S]*',
    re.S,
)


log: logging.Logger = logging.getLogger(__name__)


class Example:
    """Representation of an example file, with accessors for the various parts."""

    ExamplesCount: int = 0
    MaxId: int = 0

    def __init__(
        self, terms: List[str], original_html: str, microdata: str, rdfa: str, jsonld: str, exmeta: Dict[str, Any], jsonld_offset: Optional[int] = None
    ) -> None:
        self.terms: List[str] = terms
        if not len(terms):
            log.info(
                f"No terms for ex: {exmeta.get('filepos')} in file {exmeta.get('file')}"
            )
            first_term: str = "Empty"
        else:
            first_term = terms[0]
        self.original_html: str = original_html
        self.microdata: str = microdata
        self.rdfa: str = rdfa
        self.jsonld: str = jsonld
        self.jsonld_offset: Optional[int] = jsonld_offset
        self.exmeta: Dict[str, Any] = exmeta
        self.keyvalue: Optional[str] = self.exmeta.get("id", None)
        if not self.keyvalue:
            self.keyvalue = f"{first_term}-temp-{Example.ExamplesCount}"
            self.exmeta["id"] = self.keyvalue
        else:
            idnum: int = self.getIdNum()
            if idnum > -1:
                Example.MaxId = max(Example.MaxId, idnum)
                self.keyvalue = Example.formatId(idnum)
        Example.ExamplesCount += 1
        self.exselect: List[str] = []

    def __str__(self) -> str:
        buf: List[str] = []
        buf.append("Example: \nTerms: ")
        if not len(self.terms):
            buf.append("No Terms!")
        else:
            buf.append(f"{self.terms}")
        buf.append(f"\nKeyvalue: {self.keyvalue}")
        buf.append(
            f"\nOrigLen: {len(self.original_html)} MicroLen: {len(self.microdata)} RdfaLen: {len(self.rdfa)} JsonLen: {len(self.jsonld)}"
        )
        buf.append(f"\nexmeta: {self.exmeta}")
        return "".join(buf)

    def getKey(self) -> Optional[str]:
        return self.keyvalue

    def setKey(self, key: str) -> None:
        self.keyvalue = key

    def getTerms(self) -> List[str]:
        return self.terms

    def setTerms(self, terms: List[str]) -> None:
        self.terms = terms

    def getHtml(self) -> str:
        return self.original_html

    def setHtml(self, content: str) -> None:
        self.original_html = content

    def getMicrodata(self) -> str:
        return self.microdata

    def setMicrodata(self, content: str) -> None:
        self.microdata = content

    def getRdfa(self) -> str:
        return self.rdfa

    def setRdfa(self, content: str) -> None:
        self.rdfa = content

    def getJsonld(self) -> str:
        return self.jsonld

    def getJsonldRaw(self) -> str:
        jsondata: str = self.getJsonld()
        jsondata = jsondata.strip()
        if len(jsondata):
            jsonmatch = ldscript_match.match(jsondata)
            if jsonmatch:
                # extract json from within script tag
                jsondata = jsonmatch.group(1).strip()
        return jsondata

    def setJsonld(self, content: str) -> None:
        self.jsonld = content

    def hasHtml(self) -> bool:
        return len(self.original_html.strip()) > 0

    def hasMicrodata(self) -> bool:
        content: str = self.microdata.strip()
        if len(content) > 0:
            if "itemtype" in content and "itemprop" in content:
                return True
        return False

    def hasRdfa(self) -> bool:
        content: str = self.rdfa.strip()
        if len(content) > 0:
            if "typeof" in content and "property" in content:
                return True
        return False

    def hasJsonld(self) -> bool:
        """Return True if there is real JSON, and not a placehold comment in the JSON section."""
        json_content: str = self.getJsonldRaw()
        if not json_content:
            return False
        for reg in NO_JSON_REGEXPS:
            if reg.match(json_content):
                return False
        if json_content:
            if "@type" in json_content:
                return True
        return False

    def setMeta(self, name: str, val: Any) -> None:
        self.exmeta[name] = val

    def getMeta(self, name: str) -> Any:
        return self.exmeta.get(name, None)

    def getIdNum(self) -> int:
        idnum: int = -1
        if self.keyvalue and self.keyvalue.startswith(IDPREFIX):
            try:
                idnum = int(self.keyvalue[len(IDPREFIX) :])
            except (ValueError, TypeError):
                pass
        return idnum

    def hasValidId(self) -> bool:
        return self.getIdNum() > -1

    def serialize(self) -> str:
        termnames: str = ", ".join(self.terms)
        idd: str = f"#{self.keyvalue}"
        if "-temp-" in idd:
            idd = ""

        sections: List[str] = [
            f"TYPES: {idd} {termnames}\n",
            "PRE-MARKUP:",
            self.getHtml(),
            "MICRODATA:",
            self.getMicrodata(),
            "RDFA:",
            self.getRdfa(),
            "JSON:",
            self.getJsonld(),
        ]
        return "\n".join(sections)

    @staticmethod
    def nextId() -> str:
        Example.MaxId += 1
        return Example.formatId(Example.MaxId)

    @staticmethod
    def formatId(val: int) -> str:
        return f"eg-{val:04d}"

    @staticmethod
    def nextIdReset(val: Optional[int] = None) -> None:
        if val is None:
            val = 0
        Example.MaxId = val


class SchemaExamples:
    EXAMPLESLOADED: bool = False
    EXAMPLESMAP: Dict[str, List[str]] = {}
    EXAMPLES: Dict[str, Example] = {}
    exlock: threading.RLock = threading.RLock()

    @staticmethod
    def loadExamplesFiles(exfiles: Optional[Union[str, Iterable[str]]], init: bool = False) -> None:
        global DEFTEXAMPLESFILESGLOB
        if init:
            SchemaExamples.EXAMPLESLOADED = False
            SchemaExamples.EXAMPLESMAP = {}
            SchemaExamples.EXAMPLES = {}

        if SchemaExamples.EXAMPLESLOADED:
            log.info("Examples files already loaded")
            return

        load_files: List[str] = []
        if not exfiles or exfiles == "default":
            log.info(
                f"SchemaExamples.loadExamplesFiles() loading from default files found in globs: {','.join(DEFTEXAMPLESFILESGLOB)}"
            )
            for g in DEFTEXAMPLESFILESGLOB:
                load_files.extend(sorted(glob.glob(g)))

        elif isinstance(exfiles, str):
            log.info(
                f"SchemaExamples.loadExamplesFiles() loading from file: {exfiles}"
            )
            load_files = [exfiles]
        else:
            log.info(
                f"SchemaExamples.loadExamplesFiles() loading from {len(list(exfiles))}"
            )
            load_files = list(exfiles)

        if not len(load_files):
            raise Exception("No examples file(s) to load")

        parser: ExampleFileParser = ExampleFileParser()
        for f in load_files:
            for example in parser.parse(f):
                # log.info("Ex: %s %s" % (example.keyvalue,example.terms))
                keyvalue: str = str(example.keyvalue)
                example.setMeta("source", f)
                with SchemaExamples.exlock:
                    if not SchemaExamples.EXAMPLES.get(keyvalue, None):
                        SchemaExamples.EXAMPLES[keyvalue] = example

                    for term in example.terms:
                        if not SchemaExamples.EXAMPLESMAP.get(term, None):
                            SchemaExamples.EXAMPLESMAP[term] = []

                        mapped_ids = SchemaExamples.EXAMPLESMAP.get(term)
                        if mapped_ids is not None and keyvalue not in mapped_ids:
                            mapped_ids.append(keyvalue)
        SchemaExamples.EXAMPLESLOADED = True

    @staticmethod
    def loaded() -> None:
        if not SchemaExamples.EXAMPLESLOADED:
            log.info("Loading examples files")
            SchemaExamples.loadExamplesFiles("default")
            log.info(f"Loaded {SchemaExamples.count()} examples")

    @staticmethod
    def examplesForTerm(term: str) -> List[Example]:
        SchemaExamples.loaded()
        examples: List[Example] = []
        examps: Optional[List[str]] = SchemaExamples.EXAMPLESMAP.get(term)
        if examps:
            for e in examps:
                ex: Optional[Example] = SchemaExamples.EXAMPLES.get(e)
                if ex:
                    examples.append(ex)
        return sorted(examples, key=lambda x: str(x.keyvalue))

    @staticmethod
    def allExamples(sort: bool = False) -> Collection[Example]:
        SchemaExamples.loaded()
        ret: Collection[Example] = SchemaExamples.EXAMPLES.values()
        if sort:
            return sorted(ret, key=lambda x: (str(x.exmeta.get("file", "")), x.exmeta.get("filepos", 0)))
        return ret

    @staticmethod
    def allExamplesSerialised(sort: bool = False) -> str:
        SchemaExamples.loaded()
        examples: Collection[Example] = SchemaExamples.allExamples(sort=sort)
        f: io.StringIO = io.StringIO()
        for ex in examples:
            f.write(ex.serialize())
            f.write("\n")
        return f.getvalue()

    @staticmethod
    def count() -> int:
        SchemaExamples.loaded()
        return len(SchemaExamples.EXAMPLES)


class ExampleFileParser:
    def __init__(self) -> None:
        logging.basicConfig(level=logging.INFO)  # dev_appserver.py --log_level debug .
        self.file: str = ""  # File being parsed.
        self.filepos: int = 0  # Part index.
        self.initFields()
        self.idcache: List[str] = []

    def initFields(self) -> None:
        self.currentStr: List[str] = []
        self.terms: List[str] = []
        self.exmeta: Dict[str, Any] = {}
        self.preMarkupStr: str = ""
        self.microdataStr: str = ""
        self.rdfaStr: str = ""
        self.jsonStr: str = ""
        self.jsonld_offset: Optional[int] = None
        self.state: str = ""

    def nextPart(self, next_state: str) -> None:
        self.trimCurrentStr()
        if self.state == "PRE-MARKUP:":
            self.preMarkupStr = "".join(self.currentStr)
        elif self.state == "MICRODATA:":
            self.microdataStr = "".join(self.currentStr)
        elif self.state == "RDFA:":
            self.rdfaStr = "".join(self.currentStr)
        elif self.state == "JSON:":
            self.jsonStr = "".join(self.currentStr)

        self.state = next_state
        self.currentStr = []

    def trimCurrentStr(self) -> None:
        # strip: leading blank lines, strip multi blank lines (replace with 1) end with blank line
        temp: List[str] = []
        begin: bool = True
        inwhitespace: bool = False

        for line in self.currentStr:
            linelen: int = len(line.strip())
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
                temp.append(f"{line}\n")

        if not inwhitespace:
            temp.append("\n")
        self.currentStr = temp

    def process_example_id(self, m: re.Match) -> str:
        ident: str = m.group(1)
        if ident not in self.idcache:
            self.idcache.append(ident)
        else:
            raise Exception(
                f"Example {self.filepos} in file {self.file} has duplicate identifier: '{ident}'"
            )
        self.exmeta["id"] = ident
        return ""

    def makeExample(self) -> Example:
        """Build an example out of the current state"""
        return Example(
            terms=self.terms,
            original_html=self.preMarkupStr,
            microdata=self.microdataStr,
            rdfa=self.rdfaStr,
            jsonld=self.jsonStr,
            exmeta=self.exmeta,
            jsonld_offset=self.jsonld_offset,
        )

    def parse(self, filen: str) -> List[Example]:
        import codecs
        import requests

        self.file = filen
        self.filepos = 0
        examples: List[Example] = []
        egid: re.Pattern = re.compile(r"""#(\S+)\s+""")

        if self.file.startswith("file://"):
            self.file = self.file[7:]

        content: str
        if "://" in self.file:
            r: requests.Response = requests.get(self.file)
            content = r.text
        else:
            with codecs.open(self.file, "r", encoding="utf8") as fd:
                content = fd.read()

        lines: List[str] = re.split("\n|\r", content)
        first: bool = True
        boilerplate: bool = False
        for lineno, line in enumerate(lines):
            # Per-example sections begin with e.g.: 'TYPES: #music-2 Person, MusicComposition, Organization'
            line = line.rstrip()

            if line.startswith("TYPES:"):
                self.filepos += 1
                self.nextPart("TYPES:")
                # Create example from what has been previously collected
                if first:
                    first = False
                else:
                    if not boilerplate:
                        examples.append(self.makeExample())
                    boilerplate = False
                    self.initFields()
                self.exmeta["file"] = self.file
                self.exmeta["filepos"] = self.filepos
                typelist: List[str] = re.split(":", line)
                tdata: str = egid.sub(
                    self.process_example_id, typelist[1]
                )  # strips IDs, records them in exmeta["id"]
                ttl: List[str] = tdata.split(",")
                for ttli in ttl:
                    ttli = ttli.strip()
                    if len(ttli):
                        if "@@" not in ttli and "FakeEntryNeeded" not in ttli:
                            self.terms.append(ttli)
                        else:
                            boilerplate = True
            else:
                # Heuristic to find the start line that will be used by `getJsonldRaw`.
                if '<script type="application/ld+json">' in line:
                    self.jsonld_offset = lineno + 1
                tokens: Tuple[str, ...] = ("PRE-MARKUP:", "MICRODATA:", "RDFA:", "JSON:")
                for tk in tokens:
                    ltk: int = len(tk)
                    if line.startswith(tk):
                        self.nextPart(tk)
                        line = line[ltk:]
                self.currentStr.append(line)
        self.nextPart("TYPES:")  # should flush on each block of examples
        self.filepos += 1
        if not boilerplate:
            self.exmeta["file"] = self.file
            self.exmeta["filepos"] = self.filepos
            examples.append(self.makeExample())  # should flush last one
        self.initFields()
        return examples
