#!/usr/bin/env python3
"""Debug helper to inspect parsed Data Commons MCF domain/range/subclass fields."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from scripts.bmdc2sdo.mcf2turtle import mcf_to_dict_list, multiprop

SAMPLE_MCF: str = """Node: dcid:Disease
name: "Disease"
typeOf: schema:Class
subClassOf: schema:Thing
description: "Disease - a defined disorder with a set of symptoms that effect the biological processes of a living entity and is not the direct result of physical injury."
descriptionUrl: "https://disease-ontology.org/"

Node: dcid:DiseaseDiseaseAssociation
name: "DiseaseDiseaseAssociation"
typeOf: schema:Class
subClassOf: dcs:Disease
description: "The association between two diseases."

Node: dcid:DiseaseGeneAssociation
name: "DiseaseGeneAssociation"
typeOf: schema:Class
subClassOf: dcs:Disease,dcs:ICD10Code
description: "The association of a disease with a gene."

Node: dcid:DiseaseGeneticVariantAssociation
name: "DiseaseGeneticVariantAssociation"
typeOf: schema:Class
subClassOf: dcs:Disease
description: "The association between a disease and a genetic variant."

Node: dcid:MeSHConcept
name: "MeSHConcept"
typeOf: schema:Class
subClassOf: dcs:MeSHDescriptor
description: "The bearer of linguistic meaning in MeSH as defined by the ScopeNote, comprising a DescriptorRecord or SupplementalRecord or QualifierRecord, and consisting of Term elements."
descriptionUrl: "https://www.nlm.nih.gov/mesh/xml_data_elements.html#Concept"

Node: dcid:MeSHDescriptor
name: "MeSHDescriptor"
typeOf: schema:Class
subClassOf: schema:Intangible
description: "Cluster of one or more concepts used for subject indexing and retrieval."
descriptionUrl: "https://www.nlm.nih.gov/mesh/xml_data_elements.html#DescriptorRecord"

Node: dcid:MeSHQualifier
name: "MeSHQualifier"
typeOf: schema:Class
subClassOf: schema:Intangible
description: "Seven-character alphanumeric string uniquely identifying a QualifierRecord."
descriptionUrl: "https://www.nlm.nih.gov/mesh/xml_data_elements.html#QualifierUI"

Node: dcid:MeSHSupplementaryRecord
name: "MeSHSupplementaryRecord"
typeOf: schema:Class
subClassOf: dcs:MeSHDescriptor
description: "Cluster of one or more concepts used for subject indexing and retrieval."
descriptionUrl: "https://www.nlm.nih.gov/mesh/xml_data_elements.html#SupplementalRecord"

Node: dcid:MeSHTerm
name: "MeSHTerm"
typeOf: schema:Class
subClassOf: dcs:MeSHConcept
description: "Alphanumeric string which comprises the basic unit of the MeSH vocabulary."
descriptionUrl: "https://www.nlm.nih.gov/mesh/xml_data_elements.html#Term"

Node: dcid:medicalSubjectHeadingSupplementaryRecordID
name: "medicalSubjectHeadingSupplementaryRecordID"
typeOf: schema:Property
rangeIncludes: dcs:MeSHSupplementaryRecord, schema:Text
domainIncludes: dcs:ChemicalCompound, dcs:MeSHSupplementaryRecord
description: "A unique ID for a Medical Subject Heading supplementary record."

Node: dcid:medicalSubjectHeadingQualifierID
name: "medicalSubjectHeadingQualifierID"
typeOf: schema:Property
rangeIncludes: dcs:MeSHQualifier, schema:Text
domainIncludes: dcs:MeSHConcept, dcs:MeSHQualifier
description: "A unique ID for a Medical Subject Heading Qualifier record."
"""


def parse_sample_data(sample_data_str: str) -> None:
    for node in mcf_to_dict_list(sample_data_str):
        for prop in ("subClassOf", "domainIncludes", "rangeIncludes"):
            if values := multiprop(node, prop):
                print(f"Parsed {prop} values:")
                for value in values:
                    print(value)


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "mcf_file",
        nargs="?",
        type=Path,
        help="Optional MCF file to inspect (defaults to built-in sample)",
    )
    args = parser.parse_args(argv)
    mcf_text = (
        args.mcf_file.read_text(encoding="utf-8")
        if args.mcf_file
        else SAMPLE_MCF
    )
    parse_sample_data(mcf_text)


if __name__ == "__main__":
    main()
