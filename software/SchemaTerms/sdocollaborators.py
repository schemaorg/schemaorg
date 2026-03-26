#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import standard python libraries

import collections
import glob
import logging
import os
import traceback
import re
import sys
import typing
from typing import Any, Dict, List, Optional, Tuple, Union, Iterable, Sequence


# Import schema.org libraries
if not os.getcwd() in sys.path:
    sys.path.insert(1, os.getcwd())

import software
import software.util.schemaglobals as schemaglobals
import software.SchemaTerms.sdoterm as sdoterm
import software.SchemaTerms.sdotermsource as sdotermsource
import software.SchemaTerms.localmarkdown as localmarkdown

log: logging.Logger = logging.getLogger(__name__)

INCLUDE_RE: re.Pattern = re.compile(R"---\s+([^.]+)\.md")
SECTION_SEPARATOR: str = "---"


class collaborator(object):
    """Wrapper for the collaboration meta-data."""

    COLLABORATORS: Dict[str, "collaborator"] = {}
    CONTRIBUTORS: Dict[str, "collaborator"] = {}

    def __init__(self, ref: str, desc: Optional[str] = None) -> None:
        self.ref: str = ref
        self.urirel: str = os.path.join("/docs", "collab", ref)
        self.uri: str = schemaglobals.HOMEPAGE + self.urirel
        self.docurl: str = self.urirel
        self.terms: Optional[Sequence[sdoterm.SdoTerm]] = None
        self.contributor: bool = False
        self.img: Optional[str] = None
        self.code: Optional[str] = None
        self.title: Optional[str] = None
        self.url: Optional[str] = None
        self.description: str = ""
        self.acknowledgement: str = ""
        if desc:
            self._parseDesc(desc)

        collaborator.COLLABORATORS[self.ref] = self
        log.debug(f"Created collaborator for '{ref}'")

    def __str__(self) -> str:
        return (
            f"<collaborator ref: {self.ref} uri: {self.uri} contributor: {self.contributor} img: '{self.img}' title: '{self.title}' url: '{self.url}'>"
        )

    def _parseDesc(self, desc: str) -> None:
        """Parses data from the pseudo-markdown format.

        Args:
          desc: content of the file, typically found at the path data/collab/*.md
        """
        section: int = 0
        attributes: Dict[str, str] = {}
        lines_by_section: Dict[str, List[str]] = collections.defaultdict(list)
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
                include_match = re.search(INCLUDE_RE, line)
                if include_match:
                    section_selector = include_match.groups()[0]
                    continue
                lines_by_section[section_selector].append(line)

        self.url = attributes.get("url")
        self.title = attributes.get("title")
        self.img = attributes.get("img")
        attributes.pop("url", None)
        attributes.pop("title", None)
        attributes.pop("img", None)
        if attributes:
            log.warning(
                f"Unknown attributes found in collaborator file {self.urirel}: {attributes}"
            )

        description_lines: List[str] = lines_by_section["DescriptionText"]
        acknowledgement_lines: List[str] = lines_by_section["AcknowledgementText"]
        lines_by_section.pop("DescriptionText", None)
        lines_by_section.pop("AcknowledgementText", None)

        if lines_by_section:
            log.warning(
                f"Unknown sections found in collaborator file {self.urirel}: {list(lines_by_section.keys())}"
            )

        self.description = localmarkdown.Markdown.parseLines(description_lines)
        self.acknowledgement = localmarkdown.Markdown.parseLines(acknowledgement_lines)

    def isContributor(self) -> bool:
        return self.contributor

    def getTerms(self) -> Sequence[sdoterm.SdoTerm]:
        if not self.contributor:
            return []
        if not self.terms:
            self.terms = sdotermsource.SdoTermSource.getAcknowledgedTerms(self.uri)
        return self.terms

    @classmethod
    def getCollaborator(cls, ref: str) -> Optional["collaborator"]:
        cls.loadCollaborators()
        key: str = os.path.basename(ref)
        coll: Optional[collaborator] = cls.COLLABORATORS.get(key, None)
        if not coll:
            log.warning(f"No collaborator for '{ref}'")
        return coll

    @classmethod
    def getContributor(cls, ref: str) -> Optional["collaborator"]:
        key: str = os.path.basename(ref)
        cls.loadContributors()
        cont: Optional[collaborator] = cls.CONTRIBUTORS.get(key, None)
        if not cont:
            log.warning(f"No contributor for '{ref}'")
        return cont

    @classmethod
    def createCollaborator(cls, file_path: str) -> Optional["collaborator"]:
        code: str = os.path.basename(file_path)
        ref, _ = os.path.splitext(code)
        try:
            with open(file_path, "r", encoding="utf-8") as file_handle:
                desc = file_handle.read()
            return cls(ref, desc=desc)
        except OSError as e:
            log.error(f"Error loading colaborator source: {e}")
            return None

    @classmethod
    def loadCollaborators(cls) -> None:
        if not len(cls.COLLABORATORS):
            for file_path in glob.glob("data/collab/*.md"):
                cls.createCollaborator(file_path)
            log.info(f"Loaded {len(cls.COLLABORATORS)} collaborators")

    @classmethod
    def createContributor(cls, ref: str) -> None:
        key: str = os.path.basename(ref)
        coll: Optional[collaborator] = cls.getCollaborator(key)
        if coll:
            coll.contributor = True
            cls.CONTRIBUTORS[key] = coll

    @classmethod
    def loadContributors(cls) -> None:
        if not len(cls.CONTRIBUTORS):
            cls.loadCollaborators()
            query: str = """
            SELECT distinct ?val WHERE {
                    [] schema:contributor ?val.
            }"""
            res = sdotermsource.SdoTermSource.query(query)
            for row in res:
                cls.createContributor(str(row.val))
            log.info(f"Loaded {len(cls.CONTRIBUTORS)} contributors")

    @classmethod
    def collaborators(cls) -> List["collaborator"]:
        cls.loadCollaborators()
        return list(cls.COLLABORATORS.values())

    @classmethod
    def contributors(cls) -> List["collaborator"]:
        cls.loadContributors()
        return list(cls.CONTRIBUTORS.values())
