#!/bin/sh
EXTENSIONS="attic auto bib health-lifesci pending meta"
PWD=`pwd`
PROG="`basename $0`"
if [ `basename $PWD` != "schemaorg" ]
then
	echo "Not in the schemaorg directory! Aborting"
	exit 1
fi
if [ "$#" -lt 1 ]
then
  echo "Usage: $0 VERSION [yes]" 
  exit 1
fi
VER=$1
DIR="./data/releases/$1"

pre=$2
echo "PRE: $pre"
response=""

if [ "$#" -eq 2 ] 
then
    if [ "$pre" -eq "yes" ]
    then
        response="Y"
    fi
fi

if [ -z "$response" ]
then
    echo "$PROG:\n\tAbout to build release files for version $VER  \n\tIncluding extensions: $EXTENSIONS"
    read -r -p  "Continue? y/n: " response
fi
case $response in
	[yY])
		echo
	;;
	*)
		echo "Aborting!"
	exit 0
esac

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
	forms=""
    for form in json-ld turtle nt nquads rdf csv
	do
        forms="$forms -f $form"
        
    done
	./scripts/exportgraphs.py -i "$in" -e "$ex1" -e "$ex2" -g "#$VER" $forms -o $DIR/$file 2>&1 > /dev/null
}

echo
echo "Creating core: "
dump core extensions schema
echo
echo "Creating all-layers: "
dump "" "" all-layers
for e in $EXTENSIONS
do
	echo
	echo "Creating $e"
	dump "$e" "ALL" "ext-$e"
done

echo "Creating archive context file"

./scripts/buildarchivecontext.py -o schemaorgcontext.jsonld -d $DIR

echo "creating owl file"
./scripts/buildowlfile.py
echo done



