from __future__ import annotations

from collections.abc import Collection, Iterable
import logging
from pathlib import Path
import re
from typing import Any

from schemaorg.layout import Issues
import util.paths as paths

IDPREFIX: str = "eg-"
NO_JSON_REGEXPS: tuple[re.Pattern[str], ...] = (
    re.compile("No JSON-?LD", re.I),
    re.compile("This example is in microdata only", re.I),
    re.compile("No Json example available", re.I),
    re.compile("microdata only", re.I),
)

ldscript_match: re.Pattern[str] = re.compile(
    r'[\s\S]*<\s*script\s+type="application\/ld\+json"\s*>(.*)<\s*\/script\s*>[\s\S]*',
    re.S,
)
_EGID_RE: re.Pattern[str] = re.compile(r"#(\S+)\s+")
_SECTION_TOKENS: tuple[str, ...] = ("PRE-MARKUP:", "MICRODATA:", "RDFA:", "JSON:")

log: logging.Logger = logging.getLogger(__name__)


class Example:
    """Representation of an example file, with accessors for the various parts.

    Every example carries the identifier authored in its file (``#eg-0487``,
    ``#eg-3617a``, ...); sequential ``eg-NNNN`` ones are zero-padded.
    """

    def __init__(
        self,
        terms: list[str],
        original_html: str,
        microdata: str,
        rdfa: str,
        jsonld: str,
        exmeta: dict[str, Any],
        jsonld_offset: int | None = None,
    ) -> None:
        self.terms: list[str] = terms
        if not terms:
            log.info(
                "No terms for ex: %s in file %s",
                exmeta.get("filepos"),
                exmeta.get("file"),
            )
        self.original_html: str = original_html
        self.microdata: str = microdata
        self.rdfa: str = rdfa
        self.jsonld: str = jsonld
        self.jsonld_offset: int | None = jsonld_offset
        self.exmeta: dict[str, Any] = exmeta
        keyvalue: str | None = self.exmeta.get("id")
        if not keyvalue:
            raise ValueError(
                f"Example {exmeta.get('filepos')} in file {exmeta.get('file')} has no identifier"
            )
        self.keyvalue: str = keyvalue
        idnum: int = self.getIdNum()
        if idnum > -1:
            self.keyvalue = Example.formatId(idnum)

    def __str__(self) -> str:
        terms_str = str(self.terms) if self.terms else "No Terms!"
        return (
            f"Example: \nTerms: {terms_str}"
            f"\nKeyvalue: {self.keyvalue}"
            f"\nOrigLen: {len(self.original_html)} MicroLen: {len(self.microdata)} "
            f"RdfaLen: {len(self.rdfa)} JsonLen: {len(self.jsonld)}"
            f"\nexmeta: {self.exmeta}"
        )

    def getKey(self) -> str:
        return self.keyvalue

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
        sections: list[str] = [
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
        self._examples: dict[str, Example] = {}
        self._by_term: dict[str, list[str]] = {}
        for example in examples:
            keyvalue: str = example.keyvalue
            previous: Example | None = self._examples.get(keyvalue)
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
    def from_files(cls, files: Iterable[str | Path]) -> SchemaExamples:
        load_files: list[str] = [str(f) for f in files]
        if not load_files:
            return cls()
        log.info("Loading examples from %d files", len(load_files))
        parser = ExampleFileParser()
        parsed: list[Example] = []
        for f in load_files:
            for example in parser.parse(f):
                example.setMeta("source", f)
                parsed.append(example)
        instance = cls(parsed)
        log.info("Loaded %d examples", len(instance))
        return instance

    @classmethod
    def from_default(cls) -> SchemaExamples:
        return cls.from_files(Issues(paths.DefaultInputLayout()).get_example_files())

    def __len__(self) -> int:
        return len(self._examples)

    def examplesForTerm(self, term: str) -> list[Example]:
        examples = [
            ex
            for e in self._by_term.get(term, ())
            if (ex := self._examples.get(e))
        ]
        return sorted(examples, key=lambda x: x.keyvalue)

    def allExamples(self) -> Collection[Example]:
        return self._examples.values()


class ExampleFileParser:
    def __init__(self) -> None:
        self.file: str = ""
        self.filepos: int = 0
        self.initFields()
        self.idcache: set[str] = set()

    def initFields(self) -> None:
        self.currentStr: list[str] = []
        self.terms: list[str] = []
        self.exmeta: dict[str, Any] = {}
        self.preMarkupStr: str = ""
        self.microdataStr: str = ""
        self.rdfaStr: str = ""
        self.jsonStr: str = ""
        self.jsonld_offset: int | None = None
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
        temp: list[str] = []
        begin: bool = True
        inwhitespace: bool = False

        for line in self.currentStr:
            if not line.strip():
                if not begin:
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

    def process_example_id(self, m: re.Match[str]) -> str:
        ident: str = m.group(1)
        if ident in self.idcache:
            raise ValueError(
                f"Example {self.filepos} in file {self.file} has duplicate identifier: '{ident}'"
            )
        self.idcache.add(ident)
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

    def parse(self, filen: str | Path) -> list[Example]:
        self.file = str(filen).removeprefix("file://")
        self.filepos = 0
        self.idcache = set()
        self.initFields()
        examples: list[Example] = []

        content = Path(self.file).read_text(encoding="utf-8")
        rel_file = str(paths.DefaultInputLayout().relative_file(self.file))

        first: bool = True
        boilerplate: bool = False
        for lineno, line in enumerate(content.splitlines()):
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
                self.exmeta["file"] = rel_file
                self.exmeta["filepos"] = self.filepos
                _, type_spec = line.split(":", 1)
                tdata = _EGID_RE.sub(
                    self.process_example_id, type_spec
                )  # strips IDs, records them in exmeta["id"]
                for item in tdata.split(","):
                    term_name = item.strip()
                    if term_name:
                        if "@@" not in term_name and "FakeEntryNeeded" not in term_name:
                            self.terms.append(term_name)
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
                for tk in _SECTION_TOKENS:
                    if line.startswith(tk):
                        self.nextPart(tk)
                        line = line.removeprefix(tk)
                self.currentStr.append(line)
        self.nextPart("TYPES:")  # should flush on each block of examples
        if not first and not boilerplate:
            examples.append(self.makeExample())  # should flush last one
        self.initFields()
        return examples
