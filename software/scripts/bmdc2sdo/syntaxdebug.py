#!/usr/bin/env python3

import os
import sys
import logging

from typing import Dict, Optional, Union
from collections import OrderedDict

# Ensure data/ repo is nearby (for a basic MCF parser), for example:
# sys.path.insert(1, '/home/danbri/working/datcom/data/')

DEBUG = True

#from util.mcf_dict_util import mcf_to_dict_list

def debug_print(message):
    if DEBUG:
        print(f"DEBUG: {message}")


def mcf_to_dict_list(mcf_str: str) -> list:
    """Converts MCF file string to a list of OrderedDict objects.

    Args:
        mcf_str: String read from MCF file.
        
    Returns:
        List of OrderedDict objects where each object represents a node in the MCF file.
    """
    # TODO preserve empty lines if required
    # split by \n\n
    nodes_str_list = mcf_str.split('\n\n')
    # each node
    node_list = []

    for node in nodes_str_list:
        node = node.strip()
        # check for comments
        node_str_list = node.split('\n')
        cur_node = OrderedDict()
        comment_ctr = 0
        is_first_prop = True
        # add each pv to ordered dict
        for pv_str in node_str_list:
            # TODO handle multiple occurrences of same property within a node
            pv_str = pv_str.strip()
            if pv_str.startswith('#'):
                cur_node[f'__comment{comment_ctr}'] = pv_str
                comment_ctr += 1
            elif is_first_prop:
                is_first_prop = False
                if pv_str and not pv_str.startswith('Node: '):
                    raise ValueError(
                        f'Missing "Node: <name>" in MCF node {node}')
            if pv_str and not pv_str.startswith('#'):
                # find p, prefix, v
                pv = pv_str.split(':')
                if pv_str.count(':') == 1:
                    p = pv[0].strip()
                    prefix = ''
                    v = pv[1].strip()
                elif pv_str.count(':') == 2:
                    p = pv[0].strip()
                    prefix = pv[1].strip()
                    v = pv[2].strip()
                else:
                    p = pv[0].strip()
                    prefix = pv[1].strip()
                    v = ':'.join(pv[2:]).strip()
                    # TODO detect colon within a str(for e.g. descriptionURL)
                    logging.warning(
                        "Warning - unexpected number of ':' found in %s",
                        pv_str)

                cur_node[p] = {}
                cur_node[p]['value'] = v
                if v.startswith('[') and v.endswith(']'):
                    cur_node[p]['complexValue'] = re.sub(' +', ' ',
                                                         v)[1:-1].split(' ')
                if v.count(':') > 0 and ',' in v:
                    # TODO better handling of multiple values
                    cur_node[p]['multiple_values'] = []
                    vals = v.split(',')
                    for cur_v in vals:
                        temp_dict = {}
                        if ':' in cur_v:
                            temp_dict['namespace'] = cur_v[:cur_v.
                                                           index(':')].strip()
                            temp_dict['value'] = cur_v[cur_v.index(':') +
                                                       1:].strip()
                        else:
                            temp_dict['namespace'] = ''
                            temp_dict['value'] = cur_v
                cur_node[p]['namespace'] = prefix
        node_list.append(cur_node)
    return node_list



def parse_sample_data(sample_data_str):
    sample_data_list = mcf_to_dict_list(sample_data_str)

    for sample_data in sample_data_list:
        if 'subClassOf' in sample_data:
            sub_class_values = sample_data["subClassOf"]["value"].split(",")
            print("Parsed subClassOf values:")
            for value in sub_class_values:
                print(value.strip())

        if 'domainIncludes' in sample_data:
            domain_values = sample_data["domainIncludes"]["value"].split(",")
            print("Parsed domainIncludes values:")
            for value in domain_values:
                print(value.strip())

        if 'rangeIncludes' in sample_data:
            range_values = sample_data["rangeIncludes"]["value"].split(",")
            print("Parsed rangeIncludes values:")
            for value in range_values:
                print(value.strip())

def main():
    sample_data_str = """Node: dcid:medicalSubjectHeadingQualifierID
name: "medicalSubjectHeadingQualifierID"
typeOf: schema:Property
rangeIncludes: dcs:MeSHQualifier, schema:Text
domainIncludes: dcs:MeSHConcept, dcs:MeSHQualifier
description: "A unique ID for a Medical Subject Heading Qualifier record." """


    sample2 = """Node: dcid:Disease
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
description: "The bearer of linguistic meaning in MeSH as defined by the ScopeNote, comprising a DescriptorRecord or SupplementalRecord or QualifierRecord, and consisting of Term elements. One of the three main objects in the MeSH XML (the others being the record, and term). A single record will have one or more concepts, one of which is the preferred concept of the record. A Concept will have one or more terms, one of which is the preferred term for the concept. Referred to uniquely by both a ConceptUI and a ConceptName."
descriptionUrl: "https://www.nlm.nih.gov/mesh/xml_data_elements.html#Concept"

Node: dcid:MeSHDescriptor
name: "MeSHDescriptor"
typeOf: schema:Class
subClassOf: schema:Intangible
description: "Cluster of one or more concepts used for subject indexing and retrieval. Identified uniquely by a DescriptorUI and DescriptorName. A Descriptor. A Descriptor record. Also known as Main Heading. (Note that this differs from the MEDLINE MeshHeading element. For example, the MEDLINE element includes both the Descriptor name and the Qualifier name assigned to a citation.)."
descriptionUrl: "https://www.nlm.nih.gov/mesh/xml_data_elements.html#DescriptorRecord"

Node: dcid:MeSHQualifier
name: "MeSHQualifier"
typeOf: schema:Class
subClassOf: schema:Intangible
description: "Seven-character alpha-numeric string uniquely identifying a QualifierRecord and, along with the QualifierName, used to represent the Qualifier record in other elements. MeSHQualifiers are used to give additional context to MeSHDescriptor. MeSH has rules governing which Qualifiers can be used with a given Descriptor, as well as which MeSHQualifers cannot be used with a given MeSHDescriptor."
descriptionUrl: "https://www.nlm.nih.gov/mesh/xml_data_elements.html#QualifierUI"

Node: dcid:MeSHSupplementaryRecord
name: "MeSHSupplementaryRecord"
typeOf: schema:Class
subClassOf: dcs:MeSHDescriptor
description: "Cluster of one or more concepts used for subject indexing and retrieval. Identified uniquely by a SupplementalRecordUI and SupplementalRecordName. SCR. Supplemental Record. Formerly known as Supplementary Chemical Records."
descriptionUrl: "https://www.nlm.nih.gov/mesh/xml_data_elements.html#SupplementalRecord"

Node: dcid:MeSHTerm
name: "MeSHTerm"
typeOf: schema:Class
subClassOf: dcs:MeSHConcept
description: "Alpha-numeric string which comprises the basic unit of the MeSH vocabulary. Also functions as the name of a Descriptor and concept. The term itself is the String element."
descriptionUrl: "https://www.nlm.nih.gov/mesh/xml_data_elements.html#Term"

Node: dcid:diseaseOntologyID
name: "diseaseOntologyID"
typeOf: schema:Property
rangeIncludes: dcs:Disease
domainIncludes: dcs:Disease
description: "The disease ontology identifier for the disease specified by http://disease-ontology.org/."

Node: dcid:associationSource
name: "associationSource"
typeOf: schema:Property
rangeIncludes: dcs:AssociationSourceEnum
domainIncludes: dcs:DiseaseGeneAssociation
description: "How the association between a disease and a gene was made."

Node: dcid:associationIdentifier
name: "associationIdentifier"
typeOf: schema:Property
rangeIncludes: schema:Text
domainIncludes: dcs:DiseaseGeneAssociation
description: "Identifier for disease-gene association source."

Node: dcid:associationScore
name: "associationScore"
typeOf: schema:Property
rangeIncludes: schema:Number
domainIncludes: dcs:DiseaseGeneAssociation
description: "The score for the association between the disease and the gene."

Node: dcid:associationConfidenceInterval
name: "associationConfidenceInterval"
typeOf: schema:Property
rangeIncludes: schema:Number
domainIncludes: dcs:DiseaseGeneAssociation
description: "The confidence interval of the score for the association between the disease and the gene."

Node: dcid:associationStatus
name: "associationStatus"
typeOf: schema:Property
rangeIncludes: dcs:DiseaseGeneAssociationStatusEnum
domainIncludes: dcs:DiseaseGeneAssociation
description: "The status of the association between the disease and the gene."

Node: dcid:experimentSampleCount
name: "experimentSampleCount"
typeOf: schema:Property
rangeIncludes: schema:Number
domainIncludes: dcs:DiseaseGeneAssociation
description: "The number of samples in the experiment associating a gene with a disease ontology ID."

Node: dcid:experimentPValue
name: "experimentPValue"
typeOf: schema:Property
rangeIncludes: schema:Number
domainIncludes: dcs:DiseaseGeneAssociation
description: "The p-value of the experiment associating a gene with a disease ontology ID."

Node: dcid:nationalLibraryOfMedicineClassificationNumber
name: "nationalLibraryOfMedicineClassificationNumber"
typeOf: schema:Property
rangeIncludes: schema:Text
domainIncludes: dcs:MeSHDescriptor
description: "Classification Number provided by the National Library of Medicine (NLM) Cataloging and Metadata Management Section (CAMMS)."

Node: dcid:isPharmacologicalActionSubstance
name: "isPharmacologicalActionSubstance"
typeOf: schema:Property
rangeIncludes: schema:Boolean
domainIncludes: dcs:MeSHDescriptor, dcs:MeSHSupplementaryRecord
description: "A MeSHDescriptor or MeSHSupplementaryRecord, which has a pharmacological action."

Node: dcid:medicalSubjectHeadingConceptID
name: "medicalSubjectHeadingConceptID"
typeOf: schema:Property
rangeIncludes: dcs:MeSHConcept, schema:Text
domainIncludes: dcs:Disease, dcs:MeSHConcept
description: "A unique ID for a Medical Subject Heading Concept record."

Node: dcid:medicalSubjectHeadingDescriptorID
typeOf: schema:Property
name: "medicalSubjectHeadingDescriptorID"
rangeIncludes: dcs:MeSHDescriptor, schema:Text
domainIncludes: dcs:Disease, dcs:GeneticVariant, dcs:MeSHConcept, dcs:MeSHDescriptor, dcs:MeSHQualifier, dcs:MeSHSupplementaryRecord
description: "A unique ID for a Medical Subject Heading Descriptor record."

Node: dcid:medicalSubjectHeadingQualifierAbbreviation
name: "medicalSubjectHeadingQualifierAbbreviation"
typeOf: schema:Property
domainIncludes: dcs:MeSHQualifier
rangeIncludes: schema:Text
description: "Qualifier Abbreviation."

Node: dcid:medicalSubjectHeadingSupplementaryRecordID
name: "medicalSubjectHeadingSupplementaryRecordID"
typeOf: schema:Property
rangeIncludes: dcs:MeSHSupplementaryRecord, schema:Text
domainIncludes: dcs:ChemicalCompound, dcs:MeSHSupplementaryRecord
description: "A unique ID for a Medical Subject Heading supplementary record."

Node: dcid:medicalSubjectHeadingTermID
name: "medicalSubjectHeadingTermID"
typeOf: schema:Property
rangeIncludes: dcs:MeSHTerm, schema:Text
domainIncludes: dcs:MeSHConcept, dcs:MeSHTerm
description: "A unique ID for a Medical Subject Heading Term record."

Node: dcid:medicalSubjectHeadingTreeNumber
name: "medicalSubjectHeadingTreeNumber"
typeOf: schema:Property
rangeIncludes: schema:Text
domainIncludes: dcs:MeSHDescriptor, dcs:MeSHQualifier
description: "Alpha-numeric string referring to location within a MeSH Descriptor or Qualifier hierarchy."

Node: dcid:medicalSubjectHeadingQualifierID
name: "medicalSubjectHeadingQualifierID"
typeOf: schema:Property
rangeIncludes: dcs:MeSHQualifier, schema:Text
domainIncludes: dcs:MeSHConcept, dcs:MeSHQualifier
description: "A unique ID for a Medical Subject Heading Qualifier record."

Node: dcid:alternateDiseaseOntologyID
typeOf: schema:Property
name: "alternateDiseaseOntologyID"
domainIncludes: dcs:Disease
rangeIncludes: schema:Text
description: "An alternative disease ontology ID (DOID) associated with a disease."

Node: dcid:diseaseSynonym
typeOf: schema:Property
name: "diseaseSynonym"
domainIncludes: dcs:Disease
rangeIncludes: schema:Text
description: "A synonym for a disease name."

Node: dcid:unifiedMedicalLanguageSystemConceptUniqueIdentifier
typeOf: schema:Property
name: "unifiedMedicalLanguageSystemConceptUniqueIdentifier"
domainIncludes: dcs:Disease
rangeIncludes: schema:Text
description: "A concept is a meaning. A meaning can have many different names. A key goal of Metathesaurus construction is to understand the intended meaning of each name in each source vocabulary and to link all the names from all of the source vocabularies that mean the same thing (the synonyms). Concept Unique Identifier (CUI) contain the letter C followed by seven numbers. In the example on the right the CUI is C0018681."
descriptorUrl: "https://www.nlm.nih.gov/research/umls/new_users/online_learning/Meta_005.html"

Node: dcid:geneticAndRareDiseasesID
typeOf: schema:Property
name: "geneticAndRareDiseasesID"
domainIncludes: dcs:Disease
rangeIncludes: schema:Text
description: "The identifier for the disease in the Genetic and Rare Diseases (GARD) database."
descriptionUrl: "https://rarediseases.info.nih.gov/"

Node: dcid:nationalCancerInstituteID
typeOf: schema:Property
name: "nationalCancerInstituteID"
domainIncludes: dcs:Disease
rangeIncludes: schema:Text
description: "The identifier for the disease in the National Cancer Institute (NCI) thesaurus."
descriptionUrl: "https://www.cancer.gov/"

Node: dcid:internationalClassificationOfDiseasesOntologyID
typeOf: schema:Property
name: "internationalClassificationOfDiseasesOntologyID"
domainIncludes: dcs:Disease
rangeIncludes: schema:Text
description: "International Classification of Diseases Ontology (ICDO) is an ontology representation of the ICD system, which includes ICD-10, ICD-9, and the future ICD-11."

Node: dcid:icd10CMCode
typeOf: schema:Property
name: "icd10CMCode"
domainIncludes: dcs:Disease
rangeIncludes: dcs:ICD10Code
description: "The disease diagnosis code for version 10 of the International Classification of Diseases, Clinical Modification."

Node: dcid:icd10ApproximateSynonym
typeOf: dcs:Property
name: "icd10ApproximateSynonym"
domainIncludes: dcs:Disease
rangeIncludes: dcs:ICD10Code

Node: dcid:icd9CMCode
typeOf: schema:Property
name: "icd9CMCode"
domainIncludes: dcs:Disease
rangeIncludes: schema:Text
description: "The disease diagnosis code for version 9 of the International Classification of Diseases, Clinical Modification."

Node: dcid:icd11CMCode
typeOf: schema:Property
name: "icd11CMCode"
domainIncludes: dcs:Disease
rangeIncludes: schema:Text
description: "The disease diagnosis code for version 11 of the International Classification of Diseases, Clinical Modification."

Node: dcid:medDraID
typeOf: schema:Property
name: "medDraID"
domainIncludes: dcs:Disease
rangeIncludes: schema:Text
description: "The disease identifiers extracted from the medDRA medical terminology."
descriptionUrl: "https://www.meddra.org/"

Node: dcid:snomedCT
typeOf: schema:Property
name: "snomedCT"
domainIncludes: dcs:Disease
rangeIncludes: schema:Text
description: "SNOMED CT is a terminology that can cross-map to other international terminologies, classifications and code systems. Maps are associations between particular concepts or terms in one system and concepts or terms in another system that have the same (or similar) meaning."
descriptionUrl: "https://www.snomed.org/use-snomed-ct"

Node: dcid:umlsConceptUniqueID
typeOf: schema:Property
name: "umlsConceptUniqueID"
domainIncludes: dcs:Disease
rangeIncludes: schema:Text
description: "A Unified Medical Language System (UMLS) Concept Unique ID (CUI) is a unique identifier in the Metathesaurus for a concept. CUI contain the letter C followed by seven numbers. An example of a CUI is C0018681."
descriptionUrl: "https://www.nlm.nih.gov/research/umls/new_users/online_learning/Meta_005.html"
"""

    parse_sample_data(sample2)

if __name__ == "__main__":
    main()