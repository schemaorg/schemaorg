#!/bin/bash
set -e
set -u

######### run local sdopythonapp deply script #######
PWD="`pwd`"
PROG="`basename $0`"

echo "Deploy sdopythonapp application... "

if [ ! -d sdopythonapp ]
then
    echo "No 'sdopythonapp' directory here aborting!"
    exit 1
fi

if [ ! -d sdopythonapp/runscripts ]
then
    echo "No 'sdopythonapp/runscripts' directory here aborting!"
    exit 1
fi

if [ ! -x sdopythonapp/runscripts/runpythondeploy.sh ]
then
    echo "No 'sdopythonapp/runscripts/runpythondeploy.sh' here aborting!"
    exit 1
fi

sdopythonapp/runscripts/runpythondeploy.sh
