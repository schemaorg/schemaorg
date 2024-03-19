#!/bin/bash

export MCF=~/working/datcom/schema/biomedical_schema
export DIR=../../../data/ext/pending

# ok
./mcf2turtle.py $MCF/biological_taxonomy.mcf > $DIR/bmdc_biological_taxonomy.ttl


# not yet ok

./mcf2turtle.py $MCF/disease.mcf  > $DIR/bmdc_disease.ttl

# Files so far written:
ls -l $DIR/bmdc*.ttl