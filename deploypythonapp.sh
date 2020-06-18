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

if [[ $# -eq 1  && "$1" == "-devapp" ]]
then
    echo "Not synchronising 'sdopythonapp' with git"
    shift
else
    echo "Checking sdopythonapp is upto date"
    git submodule update --remote
fi
echo

devpath=`which dev_appserver.py`
if [ ! -z "$devpath" ]
then
    echo "Dev App Server located at $devpath"
    APP_ENGINE=${devpath%%"/bin/dev_appserver.py"}
    export APP_ENGINE="${APP_ENGINE}/platform/google_appengine/"
    echo "Setting \$APP_ENGINE to '$APP_ENGINE"
    echo 
fi



sdopythonapp/runscripts/runpythondeploy.sh $@
