#!/bin/sh
EXTENSIONS="attic auto bib health-lifesci pending meta"
PWD=`pwd`
PROG="`basename $0`"
if [ `basename $PWD` != "schemaorg" ]
then
	echo "Not in the schemaorg directory! Aborting"
	exit 1
fi
if [ "$#" -ne 1 ]
then
  echo "Usage: $0 VERSION" 
  exit 1
fi
VER=$1
DIR="./data/releases/$1"

echo "$PROG:\n\tAbout to build release files for version $VER  \n\tIncluding extensions: $EXTENSIONS"
read -r -p  "Continue? y/n: " response
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
	for form in json-ld turtle nt nquads rdf csv
	do
		echo "\t$file: $form"
		./scripts/exportgraphs.py -i "$in" -e "$ex1" -e "$ex2" -g "#$VER" -f $form -o $DIR/$file 2>&1 > /dev/null
	done
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


