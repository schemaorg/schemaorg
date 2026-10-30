#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import logging
from pathlib import Path
import re
from typing import Any, Collection, Dict, Iterable, List, Optional, Tuple, Union

import requests

from schemaorg.layout import Issues
import util.paths as paths


IDPREFIX: str = "eg-"
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
    """Representation of an example file, with accessors for the various parts.

    Every example carries the identifier authored in its file (``#eg-0487``,
    ``#eg-3617a``, ...); sequential ``eg-NNNN`` ones are zero-padded.
    """

    def __init__(
        self, terms: List[str], original_html: str, microdata: str, rdfa: str, jsonld: str, exmeta: Dict[str, Any], jsonld_offset: Optional[int] = None
    ) -> None:
        self.terms: List[str] = terms
        if not terms:
            log.info(
                f"No terms for ex: {exmeta.get('filepos')} in file {exmeta.get('file')}"
            )
        self.original_html: str = original_html
        self.microdata: str = microdata
        self.rdfa: str = rdfa
        self.jsonld: str = jsonld
        self.jsonld_offset: Optional[int] = jsonld_offset
        self.exmeta: Dict[str, Any] = exmeta
        keyvalue: Optional[str] = self.exmeta.get("id", None)
        if not keyvalue:
            raise ValueError(
                f"Example {exmeta.get('filepos')} in file {exmeta.get('file')} has no identifier"
            )
        self.keyvalue: str = keyvalue
        idnum: int = self.getIdNum()
        if idnum > -1:
            self.keyvalue = Example.formatId(idnum)
        self.exselect: List[str] = []

    def __str__(self) -> str:
        buf: List[str] = []
        buf.append("Example: \nTerms: ")
        if not self.terms:
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

    def getMicrodata(self) -> str:
        return self.microdata

    def getRdfa(self) -> str:
        return self.rdfa

    def getJsonld(self) -> str:
        return self.jsonld

    def getJsonldRaw(self) -> str:
        jsondata: str = self.getJsonld().strip()
        if jsondata and (jsonmatch := ldscript_match.match(jsondata)):
            # extract json from within script tag
            jsondata = jsonmatch.group(1).strip()
        return jsondata

    def hasHtml(self) -> bool:
        return bool(self.original_html.strip())

    def hasMicrodata(self) -> bool:
        content: str = self.microdata.strip()
        return bool(content and "itemtype" in content and "itemprop" in content)

    def hasRdfa(self) -> bool:
        content: str = self.rdfa.strip()
        return bool(content and "typeof" in content and "property" in content)

    def hasJsonld(self) -> bool:
        """Return True if there is real JSON, and not a placehold comment in the JSON section."""
        json_content: str = self.getJsonldRaw()
        if not json_content:
            return False
        if any(reg.match(json_content) for reg in NO_JSON_REGEXPS):
            return False
        return "@type" in json_content

    def setMeta(self, name: str, val: Any) -> None:
        self.exmeta[name] = val

    def getMeta(self, name: str) -> Any:
        return self.exmeta.get(name)

    def getIdNum(self) -> int:
        """Numeric part of a sequential ``eg-NNNN`` identifier, -1 for any other identifier."""
        idnum: int = -1
        if self.keyvalue.startswith(IDPREFIX):
            try:
                idnum = int(self.keyvalue.removeprefix(IDPREFIX))
            except (ValueError, TypeError):
                pass
        return idnum

    def serialize(self) -> str:
        termnames: str = ", ".join(self.terms)
        sections: List[str] = [
            f"TYPES: #{self.keyvalue} {termnames}\n",
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
    def formatId(val: int) -> str:
        return f"eg-{val:04d}"


class SchemaExamples:
    """Immutable-by-convention collection of examples indexed by ID and term."""

    def __init__(self, examples: Iterable[Example] = ()) -> None:
        self._examples: Dict[str, Example] = {}
        self._by_term: Dict[str, List[str]] = {}
        for example in examples:
            keyvalue: str = example.keyvalue
            previous: Optional[Example] = self._examples.get(keyvalue)
            if previous is not None:
                raise ValueError(
                    f"Duplicate example identifier '{keyvalue}' in {example.getMeta('source')}, "
                    f"already defined in {previous.getMeta('source')}"
                )
            self._examples[keyvalue] = example
            for term in example.terms:
                mapped_ids = self._by_term.setdefault(term, [])
                if keyvalue not in mapped_ids:
                    mapped_ids.append(keyvalue)

    @classmethod
    def from_files(cls, files: Iterable[Union[str, Path]]) -> SchemaExamples:
        load_files: List[str] = [str(f) for f in files]
        if not load_files:
            return cls()
        log.info(f"Loading examples from {len(load_files)} files")
        parser = ExampleFileParser()
        parsed: List[Example] = []
        for f in load_files:
            for example in parser.parse(f):
                example.setMeta("source", f)
                parsed.append(example)
        instance = cls(parsed)
        log.info(f"Loaded {len(instance)} examples")
        return instance

    @classmethod
    def from_default(cls) -> SchemaExamples:
        return cls.from_files(Issues(paths.DefaultInputLayout()).get_example_files())

    def __len__(self) -> int:
        return len(self._examples)

    def examplesForTerm(self, term: str) -> List[Example]:
        examples: List[Example] = [
            ex
            for e in self._by_term.get(term, [])
            if (ex := self._examples.get(e))
        ]
        return sorted(examples, key=lambda x: str(x.keyvalue))

    def allExamples(self) -> Collection[Example]:
        return self._examples.values()


class ExampleFileParser:
    def __init__(self) -> None:
        self.file: str = ""
        self.filepos: int = 0
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
        # strip: leading blank lines, strip multi blank lines (replace with 1)
        # end with blank line
        temp: List[str] = []
        begin: bool = True
        inwhitespace: bool = False

        for line in self.currentStr:
            if not line.strip():
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
        if ident in self.idcache:
            raise ValueError(
                f"Example {self.filepos} in file {self.file} has duplicate identifier: '{ident}'"
            )
        self.idcache.append(ident)
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
        self.file = filen
        self.filepos = 0
        self.idcache = []
        self.initFields()
        examples: List[Example] = []
        egid: re.Pattern = re.compile(r"""#(\S+)\s+""")

        self.file = self.file.removeprefix("file://")

        content: str
        if "://" in self.file:
            r: requests.Response = requests.get(self.file)
            content = r.text
        else:
            content = Path(self.file).read_text(encoding="utf-8")

        lines: List[str] = re.split("\n|\r", content)
        first: bool = True
        boilerplate: bool = False
        for lineno, line in enumerate(lines):
            # Per-example sections begin with e.g.:
            # 'TYPES: #music-2 Person, MusicComposition, Organization'
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
                self.exmeta["file"] = str(paths.DefaultInputLayout().relative_file(self.file))
                self.exmeta["filepos"] = self.filepos
                typelist: List[str] = re.split(":", line)
                tdata: str = egid.sub(
                    self.process_example_id, typelist[1]
                )  # strips IDs, records them in exmeta["id"]
                ttl: List[str] = tdata.split(",")
                for ttli in ttl:
                    ttli = ttli.strip()
                    if ttli:
                        if "@@" not in ttli and "FakeEntryNeeded" not in ttli:
                            self.terms.append(ttli)
                        else:
                            boilerplate = True
                if not boilerplate and "id" not in self.exmeta:
                    raise ValueError(
                        f"Example {self.filepos} in file {self.file} has no identifier"
                    )
            else:
                # Heuristic to find the start line that will be used by
                # `getJsonldRaw`.
                if '<script type="application/ld+json">' in line:
                    self.jsonld_offset = lineno + 1
                tokens: Tuple[str, ...] = ("PRE-MARKUP:", "MICRODATA:", "RDFA:", "JSON:")
                for tk in tokens:
                    if line.startswith(tk):
                        self.nextPart(tk)
                        line = line.removeprefix(tk)
                self.currentStr.append(line)
        self.nextPart("TYPES:")  # should flush on each block of examples
        if not first and not boilerplate:
            examples.append(self.makeExample())  # should flush last one
        self.initFields()
        return examples
