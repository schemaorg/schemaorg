#!/bin/bash
set -e
set -u

PWD="`pwd`"
PROG="`basename $0`"

if [  ${SECUREHTTP+"false"} ] #If $SECUREHTTP is set, use the handlers-secure.yaml
then
    echo "$PROG: Copying handlers-secure.yaml to handlers.yaml - implements https 301 redirect"
    cp ./handlers-secure.yaml sdopythonapp/site/handlers.yaml
else
    echo "$PROG: Copying handlers.yaml to handlers.yaml - http or https (No 301 redirect)"
    cp ./handlers.yaml sdopythonapp/site/handlers.yaml
fi
echo

if [ -d "sdopythonapp/site/docs" ] #If we have a local fileset to play with (ie. Not remote)
then
    echo
    if [  ${ROBOTSBLOCK+"false"} ] #If $ROBOTSBLOCK is set, use the robots-blockall.txt
    then
        echo "$PROG: Copying robots-blockall.txt to robots.txt"
        cp docs/robots-blockall.txt sdopythonapp/site/docs/robots.txt
    else
        echo "$PROG: Copying robots.txt to robots.txt"
        cp docs/robots.txt sdopythonapp/site/docs/robots.txt
    fi
    echo
fi
