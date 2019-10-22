#!/bin/bash
set -e
set -u

PWD="`pwd`"
PROG="`basename $0`"


echo
if [  ${ROBOTSBLOCK+"false"} ] #If $ROBOTSBLOCK is set, use the robots-blockall.txt
then
    echo "$PROG: Copying robots.txt to robots.txt"
    cp docs/robots.txt sdopythonapp/site/docs/robots.txt
else
    echo "$PROG: Copying robots-blockall.txt to robots.txt"
    cp docs/robots-blockall.txt sdopythonapp/site/docs/robots.txt
fi
echo