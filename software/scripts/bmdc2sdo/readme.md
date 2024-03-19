
# find ../schema/biomedical_schema/ -name \*.mcf -exec ./bmdc2sdo.py {} \;

# TODO:
# - fix issue with multiple types in a rangeIncludes/subClassOf/domainIncludes.
# - add enumerations exporter (and statvars?)

# Usage: 
# python mcf2turtle.py ~/working/datcom/schema/biomedical_schema/biological_taxonomy.mcf 
# or several files
# find ~/working/datcom/schema/biomedical_schema/ -name \*.mcf -exec ./mcf2turtle.py {} \;
# to concatenate, or 
# find ~/working/datcom/schema/biomedical_schema/ -name \*.mcf -exec ./mcf2turtle.py {} > ./{}.ttl \;
# to echo filenames.

# Schema.org Utility to import definitions from a Data Commons collection of MCF files.
# Pass it a .mcf file, it should emit Schema.org configuration Turtle to STDOUT.

# This allows us to spin up an instance of the Schema.org site codebase on AppSpot or elsewhere,
# allowing draft proposals to be explored in their entirity.
# 
# Target TTL format is https://github.com/schemaorg/schemaorg/blob/main/data/ext/pending/issue-2862.ttl
#

# OK:
#  via python mcf2turtle.py ~/working/datcom/schema/biomedical_schema/biological_taxonomy.mcf  > tmp/biological_taxonomy.ttl
#
# biological_taxonomy.mcf     

# TODO:
# GeneticVariant_alt_id_database_properties.mcf  
# pharmGKB_id_properties.mcf
# biomedical_stat_vars.mcf
# GeneticVariant_GenVarSource_enums.mcf          
# chemical_compound_enum.mcf
# genome_annotation_enum.mcf
# virus_taxonomic_ranking_enum.mcf
# chemical_compound.mcf
# genome_annotation.mcf
# virus_taxonomy_enum.mcf
# disease_enum.mcf
# human_cell_type_enum.mcf
# virus_taxonomy.mcf
# disease.mcf
# human_tissue_enum.mcf
# encode.mcf
# interaction_type_enum.mcf

# Sample MCF property definition:
# Node: dcid:medicalSubjectHeadingSupplementaryRecordID
# name: "medicalSubjectHeadingSupplementaryRecordID"
# typeOf: schema:Property
# rangeIncludes: dcs:MeSHSupplementaryRecord, schema:Text
# domainIncludes: dcs:ChemicalCompound, dcs:MeSHSupplementaryRecord
# description: "A unique ID for a Medical Subject Heading supplementary record."
