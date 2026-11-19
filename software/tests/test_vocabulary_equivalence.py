#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Equivalence test comparing Vocabulary against SdoTermSource (S12)."""

import os
from typing import Dict, List, Set, Tuple
import unittest

from rdflib import URIRef

from schemaorg import constants
from schemaorg.graph_loader import GraphLoader
from schemaorg.layout import InputLayout, Issues
from schemaorg.model import (
    DataType,
    EnumerationValue,
    SDO,
    SchemaProperty,
    SchemaType,
    SdoUri,
    Vocabulary,
    VocabularyLoader,
)
import SchemaTerms.localmarkdown as localmarkdown
from SchemaTerms.sdotermsource import SdoTermSource

# Known differences between SdoTermSource and Vocabulary:
# - Non-schema.org dataset URI returned by SdoTermSource.getAllTerms() because
#   its SPARQL query does not filter subjects to the https://schema.org/ namespace.
KNOWN_NON_SCHEMA_TERMS: Set[str] = {
    "https://op.europa.eu/en/web/eu-vocabularies/model/-/resource/dataset/eli",
}

# - `priceSpecification` and `timestamp` are `rdf:Property` terms authored with
#   `owl:equivalentClass` instead of `owl:equivalentProperty` in the source TTL;
#   SdoTermSource.getEquivalents() queries both predicates indiscriminately.
KNOWN_PROPERTY_EQUIVALENT_CLASS_TERMS: Set[str] = {
    "priceSpecification",
    "timestamp",
}

REPRESENTATIVE_TERMS: Tuple[str, ...] = (
    "Thing",
    "Person",
    "Organization",
    "LocalBusiness",
    "Restaurant",
    "Article",
    "NewsArticle",
    "DataType",
    "Boolean",
    "True",
    "False",
    "Number",
    "Integer",
    "Text",
    "URL",
    "Enumeration",
    "DayOfWeek",
    "Monday",
    "EventStatusType",
    "EventCancelled",
    "MedicalSpecialty",
    "Cardiovascular",
    "Oncologic",
    "Radiography",
    "name",
    "alumni",
    "alumniOf",
    "actor",
    "actors",
    "acceptedAnswer",
    "parentOrganization",
    "subOrganization",
    "priceSpecification",
    "timestamp",
)


class TestVocabularyEquivalence(unittest.TestCase):
    vocab: Vocabulary

    @classmethod
    def setUpClass(cls) -> None:
        SdoTermSource.loadSourceGraph("default")
        files = Issues(InputLayout(constants.PROJECT_ROOT)).get_ttl_files()
        graph = GraphLoader().load(files)
        cls.vocab = VocabularyLoader(graph).load()

    def test_term_inventory_matches(self) -> None:
        old_ids = set(SdoTermSource.getAllTerms()) - KNOWN_NON_SCHEMA_TERMS
        new_ids = {SdoUri(u).term_name() for u in self.vocab.all_terms()}
        self.assertEqual(new_ids, old_ids)

    def test_terms_match_term_by_term(self) -> None:
        slow = os.environ.get("SCHEMAORG_SLOW_TESTS") == "1"
        term_ids = (
            sorted(set(SdoTermSource.getAllTerms()) - KNOWN_NON_SCHEMA_TERMS)
            if slow
            else list(REPRESENTATIVE_TERMS)
        )

        diffs: List[str] = []
        for tid in term_ids:
            old = SdoTermSource.getTerm(tid)
            new = self.vocab.term(tid)
            if old is None or new is None:
                diffs.append(f"{tid}: missing old={old is not None} new={new is not None}")
                continue

            uri = new.uri
            if (new.label or "") != (old.label or ""):
                diffs.append(f"{tid}.label: new={new.label!r} old={old.label!r}")

            new_comment = (
                localmarkdown.Markdown.parse(new.comment).strip()
                if new.comment
                else ""
            )
            old_comment = (old.comment or "").strip()
            if new_comment != old_comment:
                diffs.append(f"{tid}.comment: new={new_comment!r} old={old_comment!r}")

            new_supers = tuple(sorted((SdoUri(u).term_name() for u in getattr(new, "supers", ()))))
            if new_supers != tuple(sorted(old.supers.ids)):
                diffs.append(f"{tid}.supers: new={new_supers} old={old.supers.ids}")

            new_subs = tuple(SdoUri(u).term_name() for u in self.vocab.subs.get(uri, ()))
            if new_subs != tuple(old.subs.ids):
                diffs.append(f"{tid}.subs: new={new_subs} old={old.subs.ids}")

            new_eqs = sorted(str(u) for u in getattr(new, "equivalents", ()))
            old_eqs = sorted(str(u) for u in old.equivalents.ids)
            if new_eqs != old_eqs and tid not in KNOWN_PROPERTY_EQUIVALENT_CLASS_TERMS:
                diffs.append(f"{tid}.equivalents: new={new_eqs} old={old_eqs}")

            new_sup_by = SdoUri(new.supersededBy[0]).term_name() if new.supersededBy else ""
            if new_sup_by != (old.supersededBy or ""):
                diffs.append(f"{tid}.supersededBy: new={new_sup_by!r} old={old.supersededBy!r}")

            new_supersedes = [SdoUri(u).term_name() for u in self.vocab.supersedes.get(uri, ())]
            if new_supersedes != list(old.supersedes or []):
                diffs.append(f"{tid}.supersedes: new={new_supersedes} old={old.supersedes}")

            new_layer = self.vocab.layer(uri)
            old_layer = "pending" if old.pending else ("attic" if old.retired else (old.extLayer or "core"))
            if new_layer != old_layer:
                diffs.append(f"{tid}.layer: new={new_layer!r} old={old_layer!r}")

            if isinstance(new, SchemaProperty):
                new_domains = tuple(sorted(SdoUri(u).term_name() for u in new.domainIncludes))
                if new_domains != tuple(sorted(old.domainIncludes.ids)):
                    diffs.append(f"{tid}.domains: new={new_domains} old={old.domainIncludes.ids}")

                new_ranges = tuple(sorted(SdoUri(u).term_name() for u in new.rangeIncludes))
                if new_ranges != tuple(sorted(old.rangeIncludes.ids)):
                    diffs.append(f"{tid}.ranges: new={new_ranges} old={old.rangeIncludes.ids}")

                new_inv = SdoUri(new.inverseOf[0]).term_name() if new.inverseOf else None
                if new_inv != old.inverse.id:
                    diffs.append(f"{tid}.inverse: new={new_inv!r} old={old.inverse.id!r}")
            elif isinstance(new, EnumerationValue):
                enum_parents = sorted(
                    SdoUri(rt).term_name()
                    for rt in new.rdf_types
                    if rt in self.vocab.enumerations
                )
                new_parent = enum_parents[0] if enum_parents else None
                if new_parent != old.enumerationParent.id:
                    diffs.append(
                        f"{tid}.enumerationParent: new={new_parent!r} old={old.enumerationParent.id!r}"
                    )
            else:
                new_props = tuple(SdoUri(u).term_name() for u in self.vocab.declared_properties.get(uri, ()))
                if new_props != tuple(old.properties.ids):
                    diffs.append(f"{tid}.properties: new={new_props} old={old.properties.ids}")

                new_all_props = tuple(SdoUri(u).term_name() for u in self.vocab.all_properties.get(uri, ()))
                # SdoTermSource clears termStack on Enumeration classes that have no direct
                # properties, severing the ancestor chain for 2nd-level Enumeration subclasses
                # (e.g. EventStatusType -> StatusEnumeration -> Enumeration).
                if new_all_props != tuple(old.allproperties.ids) and uri not in self.vocab.enumerations:
                    diffs.append(f"{tid}.allproperties: new={new_all_props} old={old.allproperties.ids}")

                new_expected = tuple(SdoUri(u).term_name() for u in self.vocab.expected_type_for.get(uri, ()))
                if new_expected != tuple(old.expectedTypeFor.ids):
                    diffs.append(f"{tid}.expectedTypeFor: new={new_expected} old={old.expectedTypeFor.ids}")

                if uri in self.vocab.enumerations:
                    new_members = tuple(SdoUri(u).term_name() for u in self.vocab.enumeration_members.get(uri, ()))
                    if new_members != tuple(old.enumerationMembers.ids):
                        diffs.append(f"{tid}.enumerationMembers: new={new_members} old={old.enumerationMembers.ids}")

        self.assertEqual(diffs, [], "\n".join(diffs[:50]))


if __name__ == "__main__":
    unittest.main()
