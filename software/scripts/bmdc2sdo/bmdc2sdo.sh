#!/bin/bash

# biological_taxonomy.mcf     
# disease.mcf                                   
# genome_annotation.mcf
# biomedical_stat_vars.mcf
# encode.mcf
# human_cell_type_enum.mcf
# virus_taxonomic_ranking_enum.mcf
# chemical_compound_enum.mcf
# GeneticVariant_alt_id_database_properties.mcf
# human_tissue_enum.mcf
# virus_taxonomy_enum.mcf
# chemical_compound.mcf
# GeneticVariant_GenVarSource_enums.mcf
# interaction_type_enum.mcf
# virus_taxonomy.mcf
# disease_enum.mcf
# genome_annotation_enum.mcf
# pharmGKB_id_properties.mcf

export MCF=/home/danbri/working/sdo/schema/biomedical_schema
export DIR=../../../data/ext/pending

echo $MCF
ls $MCF


# cp fixup-BMDC.ttl.dist $DIR/fixup-BMDC.ttl # fixes


# ok
./mcf2turtle.py $MCF/biological_taxonomy.mcf > $DIR/bmdc_biological_taxonomy.ttl
 # this needs genome_annotation.mcf for BiologicalElement dcs:

# wip
#./mcf2turtle.py $MCF/genome_annotation.mcf > $DIR/bmdc_genome_annotation.ttl

# this .mcf needs a fix on line 41: s/ode/Node/
#./mcf2turtle.py $MCF/chemical_compound.mcf > $DIR/bmdc_chemical_compound.ttl


# not yet ok

#./mcf2turtle.py $MCF/disease.mcf  > $DIR/bmdc_disease.ttl
# RecursionError: maximum recursion depth exceeded -- on site build.

# This fails even when the "ode"/"Node" fix is made,
# barfs during site build phase, possibly missing defs?
# https://github.com/datacommonsorg/schema/pull/800
#./mcf2turtle.py $MCF/chemical_compound.mcf  > $DIR/bmdc_chemical_compound.ttl
# typo https://github.com/datacommonsorg/schema/blob/main/biomedical_schema/chemical_compound.mcf#L41


# fails bad
#./mcf2turtle.py $MCF/encode.mcf  > $DIR/bmdc_encode.ttl


# Files so far written:
ls -l $DIR/bmdc*.ttl

# test everything:
# find ~/working/datcom/schema/biomedical_schema -exec ./mcf2turtle.py {} \; > out.txt
