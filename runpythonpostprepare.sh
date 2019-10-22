#!/bin/bash
set -e
set -u

PWD="`pwd`"
PROG="`basename $0`"

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