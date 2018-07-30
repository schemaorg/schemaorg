#!/bin/sh
PWD=`pwd`
PROG="`basename $0`"
if [ `basename $PWD` != "schemaorg" ]
then
	echo "Not in the schemaorg directory! Aborting"
	exit 1
fi
date -u > ./admin/deploy_timestamp.txt

echo gcloud app deploy $@
gcloud app deploy $@
