"""Collaborator and contributor metadata registry."""

from __future__ import annotations

import collections
from collections.abc import Mapping
import logging
from pathlib import Path
import re
from urllib.parse import urljoin

from rdflib import URIRef

from schemaorg import constants, markdown
from schemaorg.layout import Domain, InputLayout
from schemaorg.model import SchemaTerm, Vocabulary

log: logging.Logger = logging.getLogger(__name__)

_INCLUDE_RE: re.Pattern[str] = re.compile(r"---\s+([^.]+)\.md")
_SECTION_SEPARATOR: str = "---"


class Collaborator:
    """Metadata parsed from a single data/collab/*.md definition."""

    def __init__(
        self,
        ref: str,
        desc: str | None = None,
        contributor: bool = False,
    ) -> None:
        self.ref: str = ref
        self.code: str = Path(ref).name
        self.urirel: str = str(Path("/docs/collab") / ref)
        self.uri: str = urljoin(constants.SCHEMA_URI, self.urirel)
        self.docurl: str = self.urirel
        self.contributor: bool = contributor
        self.img: str | None = None
        self.title: str | None = None
        self.url: str | None = None
        self.description: str = ""
        self.acknowledgement: str = ""
        if desc:
            self._parse_desc(desc)

    def _parse_desc(self, desc: str) -> None:
        section = 0
        attributes: dict[str, str] = {}
        lines_by_section: dict[str, list[str]] = collections.defaultdict(list)
        section_selector = ""

        for line in desc.splitlines():
            if line.startswith(_SECTION_SEPARATOR):
                section += 1
            if section == 1:
                if line.startswith(_SECTION_SEPARATOR):
                    continue
                if ":" in line:
                    key, value = line.split(":", maxsplit=1)
                    attributes[key.strip()] = value.strip()
                continue
            if section > 1:
                if match := _INCLUDE_RE.search(line):
                    section_selector = match.group(1)
                    continue
                lines_by_section[section_selector].append(line)

        self.url = attributes.pop("url", None)
        self.title = attributes.pop("title", None)
        self.img = attributes.pop("img", None)
        if attributes:
            log.warning(
                "Unknown attributes in collaborator %s: %s",
                self.urirel,
                attributes,
            )

        description_lines = lines_by_section.pop("DescriptionText", [])
        acknowledgement_lines = lines_by_section.pop("AcknowledgementText", [])
        if lines_by_section:
            log.warning(
                "Unknown sections in collaborator %s: %s",
                self.urirel,
                list(lines_by_section),
            )

        self.description = markdown.Markdown.parseLines(
            description_lines, wpre="/"
        )
        self.acknowledgement = markdown.Markdown.parseLines(
            acknowledgement_lines, wpre="/"
        )


class CollaboratorRegistry:
    """Collaborator definitions indexed against a Vocabulary's contributor links."""

    def __init__(
        self,
        collaborators: Mapping[str, Collaborator] | None = None,
        acknowledged_uris: Mapping[str, tuple[URIRef, ...]] | None = None,
    ) -> None:
        self._by_ref: dict[str, Collaborator] = dict(collaborators or {})
        self._ack_uris: dict[str, tuple[URIRef, ...]] = dict(
            acknowledged_uris or {}
        )

    @classmethod
    def from_layout(
        cls, input_layout: InputLayout, vocab: Vocabulary | None = None
    ) -> CollaboratorRegistry:
        by_ref: dict[str, Collaborator] = {}
        for path in input_layout.files(Domain.DATA, "collab/*.md"):
            try:
                desc = path.read_text(encoding="utf-8")
            except OSError as exc:
                log.error("Error loading collaborator %s: %s", path, exc)
                continue
            by_ref[path.stem] = Collaborator(path.stem, desc=desc)

        ack_sets: dict[str, set[URIRef]] = collections.defaultdict(set)
        if vocab is not None:
            seen_missing: set[str] = set()
            for term in vocab.all_terms().values():
                for c_uri in term.contributor:
                    key = Path(str(c_uri)).name
                    coll = by_ref.get(key)
                    if coll is None:
                        if str(c_uri) not in seen_missing:
                            seen_missing.add(str(c_uri))
                            log.warning("No collaborator for '%s'", c_uri)
                        continue
                    coll.contributor = True
                    ack_sets[key].add(term.uri)

        ack_uris = {
            k: tuple(sorted(uris, key=str)) for k, uris in ack_sets.items()
        }
        return cls(by_ref, ack_uris)

    def all(self) -> list[Collaborator]:
        return list(self._by_ref.values())

    def get(self, ref: str) -> Collaborator | None:
        return self._by_ref.get(Path(ref).name)

    def for_term(self, term: SchemaTerm) -> tuple[Collaborator, ...]:
        acks = [
            coll
            for c_uri in term.contributor
            if (coll := self.get(str(c_uri))) is not None and coll.contributor
        ]
        return tuple(sorted(acks, key=lambda c: c.title or ""))

    def term_uris(self, ref: str) -> tuple[URIRef, ...]:
        return self._ack_uris.get(Path(ref).name, ())
