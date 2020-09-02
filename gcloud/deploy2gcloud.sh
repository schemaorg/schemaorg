#!/bin/bash
set -e
set -u

#schemaorg deployment to gcloud script

PWD=`pwd`
PROG="`basename $0`"
echo ${PROG}
echo
if [ `basename $PWD` != "schemaorg" ]
then
	echo "Not in the schemaorg directory! Aborting"
	exit 1
fi
if [ ! -d "./site" ]
then
    echo "No 'site' directory! Aborting"
    exit 1
fi

cd site
echo Preparing .yaml files
cp gcloud/*.yaml .
echo Done

function usage {
    echo "usage: $(basename $0) -e -m [-p project] [-v version] [-y yaml file]"
	echo "-m bypasses migrate traffic to new version step"
}

PROJECT=""
VERSION=""
YAML=""
CONF=""
EXE="Y"
MIG="Y"
while getopts 'p:v:y:em' OPTION; do
  case "$OPTION" in
    e)
      EXE="N"
    ;;
    m)
        MIG="N"
    ;;
    y)
        YAML="$OPTARG"
    ;;

    p)
        PROJECT="$OPTARG"
    ;;

    v)
        VERSION="$OPTARG"
    ;;


    ?)
        usage
        exit 1
    ;;
  esac
done

while [ -z "$PROJECT" ]
do
    echo
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
            echo
            echo "Project '$P' not valid and/or accessible"
        else
            echo "Project '$P'  valid "
        fi
    fi
done
while [ -z "$VERSION" ]
do
    echo
    read -r -p "Appengine Version ID: " response
   # VERSION="$response"
   if [ ! -z "$response" ]
   then
        VERSION="${response//./-}"
        VERSION="${VERSION// /}"
    fi
done
echo "Using version ID '$VERSION'"
while [ -z "$YAML" ]
do
    read -r -p "Yaml file [other.yaml]: " response
    YAML="$response"
    if [ -z "$YAML" ]
    then
        YAML="other.yaml"
    fi
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
    echo
    echo "About to deploy version '$VERSION' to Gcloud project '$PROJECT' using yaml '$YAML' "
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
URL="${VERSION}-dot-${PROJECT}.appspot.com"
FULLURL="https://$URL"


echo
echo "Checking for version conflicts"

for ver in `gcloud app versions list --hide-no-traffic --project $PROJECT --uri`
do
    if [ "$ver" = "$FULLURL" ]
    then
        echo "WARNING!!! Version ${VERSION} is already serving traffic for project ${PROJECT}"
        echo "This deployment WILL OVERWRITE that version"
        read -r -p "Continue? (y/n): " response
        case $response in
        Y|y)
            break
            ;;
        N|n)
            echo "Aborting"
            exit 1
            ;;
        *)
            echo "Aborting"
            exit 1
            ;;
        esac
    fi
done

echo gcloud app deploy --quiet --no-promote --project "$PROJECT" --version="$VERSION" "$YAML"
echo
gcloud app deploy --quiet --no-promote --project "$PROJECT" --version="$VERSION" "$YAML"
echo

echo "Version '$VERSION' of project '$PROJECT' deployed "
echo clearing .yaml files
rm -f *.yaml

if [ "$MIG" = "Y" ]
then
    echo
    echo "Migrating traffic"
    gcloud app services --quiet --project "$PROJECT" set-traffic --splits="$VERSION"=1
    echo
    echo "Done"
else
    echo
    echo "Traffic not migrated - to put $VERSION live use appengine console"
    echo "Access it via this url: http://$URL"
fi

cd $PWD
