#!/bin/bash
set -e
set -u

EXTENSIONS="attic auto bib health-lifesci pending meta"
PWD=`pwd`
PROG="`basename $0`"
if [ `basename $PWD` != "schemaorg" ]
then
	echo "Not in the schemaorg directory! Aborting"
	exit 1
fi

function usage {
    echo "usage: $(basename $0) [-y] [-e] [-c] [-o] [-limit somevalue] VERSION"
    echo "    -y   Assume yes to continue"
    echo "    -e   No extentstions (only produce core and all-layers)"
    echo "    -c   No context file"
    echo "    -o   No owl file"
    echo "    -l   \"Output types\" (json-ld|turtle|nt|nquads|rdf|csv)" 
}

if [ "$#" -lt 1 ]
then
usage
  exit 1
fi

LIMIT=""
AUTORUN=0
CONTEXT=1
OWL=1
EXTS=1
while getopts 'yecol:' OPTION; do
  case "$OPTION" in
    y)
        AUTORUN=1
        echo "Run unchallenged"
    ;;

    c)
        CONTEXT=0
    ;;

    o)
        OWL=0
    ;;
    
    e)
        EXTS=0
    ;;


    l)
        LIMIT="$OPTARG"
        echo "The limit value provided is $OPTARG"
    ;;
    ?)
        usage 
        exit 1
    ;;
  esac
done
shift "$(($OPTIND -1))"
VER="$*"


VER=$1
DIR="./data/releases/$1"


if [ $AUTORUN -eq 0 ]
then
    echo "$PROG:\n\tAbout to build release files for version $VER  \n\tIncluding extensions: $EXTENSIONS"
    read -r -p  "Continue? y/n: " response
    case $response in
    	[yY])
    		AUTORUN=1
    	;;
    	*)
    		echo "Aborting!"
    	exit 0
    esac
fi

if [ ! -d  $DIR ]
then
	echo "Creating $VER directory"
	mkdir $DIR
else
	echo "Found $VER directory"	
fi
if [ ! -d  $DIR ]
then
	echo "Failed to create $DIR! Aborting"
fi

echo "Cleaning directory"
rm -f $DIR/*.jsonld 2>&1 > /dev/null
rm -f $DIR/*.rdf 2>&1 > /dev/null
rm -f $DIR/*.nq 2>&1 > /dev/null
rm -f $DIR/*.nt 2>&1 > /dev/null
rm -f $DIR/*.ttl 2>&1 > /dev/null
rm -f $DIR/*.csv 2>&1 > /dev/null

function dump {
	in=$1
	ex=$2
	ex1=$ex
	ex2=""
	if [ "$ex" == "ALL" ]
	then
		ex1="core"
		ex2="extensions"
	fi
	file=$3
    LIMIT=$4
	forms=""
    if [ -z "$LIMIT" ]
    then
        for form in json-ld turtle nt nquads rdf csv
    	do
            forms="$forms -f $form"
        
        done
    else
        forms=$LIMIT
    fi
    
	./scripts/exportgraphs.py -i "$in" -e "$ex1" -e "$ex2" -g "#$VER" $forms -o $DIR/$file 2>&1 > /dev/null
}

echo
echo "Creating core: "
dump core extensions schema "$LIMIT"

echo
echo "Creating all-layers: "
dump "" "" all-layers "$LIMIT"

if [ $EXTS -eq 1 ]
then
    for e in $EXTENSIONS
    do
    	echo
    	echo "Creating $e"
    	dump "$e" "ALL" "ext-$e" "$LIMIT"
    done
fi


if [ $CONTEXT -eq 1 ]
then
    echo "Creating archive context file"
    ./scripts/buildarchivecontext.py -o schemaorgcontext.jsonld -d $DIR
fi

if [ $OWL -eq 1 ]
then
    echo "creating owl file"
    ./scripts/buildowlfile.py
fi
echo done



