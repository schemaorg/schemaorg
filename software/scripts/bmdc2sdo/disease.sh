#!/bin/bash

export MCF=~/working/datcom/schema/biomedical_schema
export DIR=../../../data/ext/pending

./mcf2turtle.py $MCF/disease.mcf 

