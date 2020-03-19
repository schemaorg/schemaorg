#!/bin/bash
set -e
set -u

######### run local sdopythonapp script #######
PWD="`pwd`"
PROG="`basename $0`"

echo "Run sdopythonapp application localy...."

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

if [ ! -x sdopythonapp/runscripts/runpythonlocal.sh ]
then
    echo "No 'sdopythonapp/runscripts/runpythonlocal.sh' here aborting!"
    exit 1
fi

if [[ $# -eq 1  && "$1" == "-devapp" ]]
then 
    echo "Not synchronising 'sdopythonapp' with git"
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

export DEFAULTBYPASSSTATICBUILD="YES" #set default to N for build static files

sdopythonapp/runscripts/runpythonlocal.sh 
