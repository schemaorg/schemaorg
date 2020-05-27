#!/bin/sh


# To stage a release on webschemas.org,
# e.g. 
# scripts/appdeploy.sh --no-promote --project webschemas-g  --version=3-7 webschemas.yaml


PWD=`pwd`
PROG="`basename $0`"

if [ ! -d ./admin ]
then
    mkdir ./admin
fi

date -u > ./admin/deploy_timestamp.txt

echo gcloud app deploy $@
gcloud app deploy $@
