#!/bin/bash
set -e
set -u

#Deployment for the schema.org site

function usage {
    echo "usage: $(basename $0) -e -m"
	echo "-m bypasses migrate traffic to new version step"
}

EXE=""
MIG=""
while getopts 'm' OPTION; do
  case "$OPTION" in
    m)
        MIG="-m"
    ;;
    ?)
        usage
        exit 1
    ;;
  esac
done

echo "Deploy to gcloud for Schema.org"

software/gcloud/deploy2gcloud.sh $MIG -p schemaorgae -y schemaorg.yaml

    
    

