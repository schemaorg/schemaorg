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

if [ "$REL" = "Y" ]
then
    VER=""
    echo
    while [ -z "$VER" ]
    do
        read -r -p "Version for release files: " VER
    done
        
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
        echo "done"
        echo
    fi
fi

 
 

