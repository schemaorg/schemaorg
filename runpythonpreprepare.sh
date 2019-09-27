#!/bin/bash
set -e
set -u

######### sdositeapp local prepare script #######
PWD="`pwd`"
PROG="`basename $0`"
echo $PROG:

if [ ! -x scripts/buildTermConfig.sh ]
then
    echo "No 'scripts/buildTermConfig' script here aboorting!"
    exit
fi
./scripts/buildTermConfig.sh 
