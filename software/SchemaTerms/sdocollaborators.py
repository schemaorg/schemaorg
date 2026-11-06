from __future__ import annotations

import collections
from collections.abc import Sequence
import logging
from pathlib import Path
import re
from urllib.parse import urljoin

from schemaorg import constants
import SchemaTerms.localmarkdown as localmarkdown
import SchemaTerms.sdoterm as sdoterm
import SchemaTerms.sdotermsource as sdotermsource
import util.paths as paths

log: logging.Logger = logging.getLogger(__name__)

INCLUDE_RE: re.Pattern[str] = re.compile(R"---\s+([^.]+)\.md")
SECTION_SEPARATOR: str = "---"


class collaborator:
    """Wrapper for the collaboration meta-data."""

    COLLABORATORS: dict[str, collaborator] = {}
    CONTRIBUTORS: dict[str, collaborator] = {}

    def __init__(self, ref: str, desc: str | None = None) -> None:
        self.ref: str = ref
        self.urirel: str = str(Path("/docs/collab") / ref)
        self.uri: str = urljoin(constants.SCHEMA_URI, self.urirel)
        self.docurl: str = self.urirel
        self.terms: Sequence[sdoterm.SdoTerm] | None = None
        self.contributor: bool = False
        self.img: str | None = None
        self.title: str | None = None
        self.url: str | None = None
        self.description: str = ""
        self.acknowledgement: str = ""
        if desc:
            self._parseDesc(desc)

        collaborator.COLLABORATORS[self.ref] = self
        log.debug("Created collaborator for '%s'", ref)

    def __str__(self) -> str:
        return (
            f"<collaborator ref: {self.ref} uri: {self.uri} contributor: {self.contributor} "
            f"img: '{self.img}' title: '{self.title}' url: '{self.url}'>"
        )

    def _parseDesc(self, desc: str) -> None:
        """Parses data from the pseudo-markdown format.

        Args:
          desc: content of the file, typically found at the path data/collab/*.md
        """
        section: int = 0
        attributes: dict[str, str] = {}
        lines_by_section: dict[str, list[str]] = collections.defaultdict(list)
        section_selector: str = ""

        for line in desc.splitlines():
            if line.startswith(SECTION_SEPARATOR):
                section += 1
            if section == 1:
                if line.startswith(SECTION_SEPARATOR):
                    continue
                if ":" in line:
                    key, value = line.split(":", maxsplit=1)
                    attributes[key.strip()] = value.strip()
                continue
            if section > 1:
                if include_match := INCLUDE_RE.search(line):
                    section_selector = include_match.group(1)
                    continue
                lines_by_section[section_selector].append(line)

        self.url = attributes.pop("url", None)
        self.title = attributes.pop("title", None)
        self.img = attributes.pop("img", None)
        if attributes:
            log.warning(
                "Unknown attributes found in collaborator file %s: %s",
                self.urirel,
                attributes,
            )

        description_lines = lines_by_section.pop("DescriptionText", [])
        acknowledgement_lines = lines_by_section.pop("AcknowledgementText", [])

        if lines_by_section:
            log.warning(
                "Unknown sections found in collaborator file %s: %s",
                self.urirel,
                list(lines_by_section),
            )

        self.description = localmarkdown.Markdown.parseLines(description_lines)
        self.acknowledgement = localmarkdown.Markdown.parseLines(acknowledgement_lines)

    def getTerms(self) -> Sequence[sdoterm.SdoTerm]:
        if not self.contributor:
            return []
        if self.terms is None:
            self.terms = sdotermsource.SdoTermSource.getAcknowledgedTerms(self.uri)
        return self.terms

    @classmethod
    def getCollaborator(cls, ref: str) -> collaborator | None:
        cls.loadCollaborators()
        key: str = Path(ref).name
        coll = cls.COLLABORATORS.get(key)
        if not coll:
            log.warning("No collaborator for '%s'", ref)
        return coll

    @classmethod
    def getContributor(cls, ref: str) -> collaborator | None:
        key: str = Path(ref).name
        cls.loadContributors()
        cont = cls.CONTRIBUTORS.get(key)
        if not cont:
            log.warning("No contributor for '%s'", ref)
        return cont

    @classmethod
    def createCollaborator(cls, file_path: str | Path) -> collaborator | None:
        path = Path(file_path)
        ref = path.stem
        try:
            desc = path.read_text(encoding="utf-8")
            return cls(ref, desc=desc)
        except OSError as e:
            log.error("Error loading collaborator source: %s", e)
            return None

    @classmethod
    def loadCollaborators(cls) -> None:
        if not cls.COLLABORATORS:
            for file_path in paths.DefaultInputLayout().files(paths.Domain.DATA, "collab/*.md"):
                cls.createCollaborator(file_path)
            log.info("Loaded %d collaborators", len(cls.COLLABORATORS))

    @classmethod
    def createContributor(cls, ref: str) -> None:
        key: str = Path(ref).name
        coll = cls.getCollaborator(key)
        if coll:
            coll.contributor = True
            cls.CONTRIBUTORS[key] = coll

    @classmethod
    def loadContributors(cls) -> None:
        if not cls.CONTRIBUTORS:
            cls.loadCollaborators()
            query: str = """
            SELECT distinct ?val WHERE {
                    [] schema:contributor ?val.
            }"""
            for row in sdotermsource.SdoTermSource.query(query):
                cls.createContributor(str(row.val))
            log.info("Loaded %d contributors", len(cls.CONTRIBUTORS))

    @classmethod
    def collaborators(cls) -> list[collaborator]:
        cls.loadCollaborators()
        return list(cls.COLLABORATORS.values())
