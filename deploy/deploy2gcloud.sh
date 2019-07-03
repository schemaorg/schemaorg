#!/bin/bash
set -e
set -u

#schemaorg deployment to gcloud script

PWD=`pwd`
PROG="`basename $0`"
if [ `basename $PWD` != "schemaorg" ]
then
	echo "Not in the schemaorg directory! Aborting"
	exit 1
fi
DDIR=deploy
SDIR=scripts
if [ ! -d ./$DDIR ]
then 
    echo "No valid $DDIR directory! Aborting"
	exit 1
fi
if [ ! -d $SDIR ]
then 
    echo "No valid $SDIR directory! Aborting"
	exit 1
fi

function usage {
    echo "usage: $(basename $0) [-c config] [-p project] [-v version] [-yyaml file]"
}

PROJECT=""
VERSION=""
YAML=""
CONF=""
while getopts 'c:p:v:y:' OPTION; do
  case "$OPTION" in
    y)
        YAML="$OPTARG"
    ;;

    p)
        PROJECT="$OPTARG"
    ;;

    v)
        VERSION="$OPTARG"
    ;;
    
    c)
        CONF="$OPTARG"
    ;;

    ?)
        usage 
        exit 1
    ;;
  esac
done 

if [ ! -z "$CONF" ]
then
    if [ "$CONF" = "schemaorg" ]
    then
        PROJECT="schemaorgae"
        YAML="schemaorg.yaml"
    elif [ "$CONF" = "webschemas" ]
    then
        PROJECT="webschemas_g"
        YAML="webscemas.yaml"
    elif [ "$CONF" = "test" ]
    then
        PROJECT="sdo-rjwtest"
        YAML="app.yaml"
    else
        echo "Invalid config name '$CONF' - aborting"
        exit 1
    fi
fi

while [ -z "$PROJECT" ]
do
    read -r -p "Project: " response
    P="$response"
    if [ ! -z "$P" ]
    then
        echo "Checking project: $P"
        for proj in `gcloud projects list --format="value(projectId)"`
        do
            if [ "$proj" = "$P" ]
            then
                PROJECT=$P
                break
            fi
        done
        if [ -z "$PROJECT" ]
        then
            echo "Project '$P' not valid and/or accessible"
        else
            echo "Project '$P'  valid "
        fi
    fi
done
while [ -z "$VERSION" ]
do
    read -r -p "Version: " response
   # VERSION="$response"
   if [ ! -z "$response" ]
   then
        VERSION="${response//./-}"
        VERSION="${VERSION// /}"
    fi
done
echo "Using version '$VERSION'"
while [ -z "$YAML" ]
do
    read -r -p "Yaml file: " response
    YAML="$response"
    if [ ! -f "$YAML" ]
    then
        echo "No such file '$YAML'"
        YAML=""
    elif [ "${YAML##*.}" != "yaml" ]
    then
        echo "'$YAML' not a .yaml file"
        YAML=""
    fi
done
    
cont="N"
while [ "$cont" != "Y" ]
do
    echo "\nAbout to deploy vesion '$VERSION' to Gcloud project '$PROJECT' using yaml '$YAML' "
    read -r -p "Continue? (y/n): " response
    case $response in
    Y|y)
        cont="Y"
        ;;
    N|n)
        echo "Aborting"
        exit 1
        ;;
    esac
done    
    
################# Deploy steps

scripts/appdeploy.sh --quiet --no-promote --project "$PROJECT" --version="$VERSION" "$YAML" 
echo "\n\nVersion '$VERSION' of project '$PROJECT' deployed \n"

URL="${VERSION}-dot-${PROJECT}.appspot.com"
echo "Starting exercise of site: $URL\n"

scripts/exercisesite.py --site "$URL"
echo "\n\nSite excersised"
echo "\nMigrating traffic"
gcloud app services --quiet --project "$PROJECT" set-traffic --splits="$VERSION"=1
echo "\nDone"