#!/bin/bash
set -e
set -u

######### sdositeapp local prepare script #######
PWD="`pwd`"
PROG="`basename $0`"
echo $PROG:

if [ ! -x scripts/buildTermConfig.sh ]
then
    echo "No 'scripts/buildTermConfig' script here aboorting!"
    exit
fi
./scripts/buildTermConfig.sh

DEFREL="Y"

if [  ${DEFAULTBYPASSSTATICBUILD+"false"} ] #set default to N for build static files
then
    DEFREL="N"
fi

while true
do
 echo
 read -r -p "Build site static files Y/N [$DEFREL]: " response
 case $response in
    Y|y)
        REL="Y"
        break
        ;;
    N|n)
        REL="N"
        break
        ;;
    "")
        if [ ! -z "$DEFREL" ]
        then
            REL="$DEFREL"
            break
        fi
        ;;
    esac
done

CONFVER=`grep schemaversion ./versions.json | sed   's|[ \t]*"schemaversion" *: *"\(.*\)".*|\1|g' `

if [ "$REL" = "Y" ]
then
    VER=""
    echo
    while [ -z "$VER" ]
    do
        read -r -p "Version for release files: " VER
    done
    
    if [ "$VER" != "$CONFVER" ]  && [ "$VER" != "tmp" ]
    then
        echo
        echo "WARNING!! "
        echo "         Version '$VER' is not the same as defined as schemaversion in versions.json file ($CONFVER)"
        echo "Fix before continuing!!"
        echo
        exit 1
    fi
        
    ./scripts/buildreleasefiles.sh $VER
    
    if [ $? -ne 0 ]
    then
        exit $?
    fi
elif [ ! -z ${MODE+x} ]
then
    if [ "$MODE" == "DEPLOY" ] #ensure these get built in deploymode
    then
        echo "Building sitemap and owl files"
        ./scripts/buildowlfile.py
        ./scripts/buildsitemap.py
        echo
        echo "Checking release files"
        DIR="./data/releases/${CONFVER}"
        if [ ! ${DIR} ]
        then
            echo
            echo "WARNING!! No release directory for schemaversion '${DIR}' (as defined in versions.json)"
            echo "Build static files before continuing!!"
            echo
            exit 1
        elif [ ! -f "${DIR}/schema-all.html" ]
        then
            echo "creating schema-all.html file"
            ./scripts/buildreleasespage.py -o $DIR/schema-all.html
        fi
        echo "done"
        echo
    fi
fi

 
 

