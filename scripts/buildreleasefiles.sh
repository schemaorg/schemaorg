#!/bin/bash
set -e
set -u

EXTENSIONS="attic auto bib health-lifesci pending meta"
PWD=`pwd`
PROG="`basename $0`"
if [ `basename "$PWD"` != "schemaorg" ]
then
	echo "Not in the schemaorg directory! Aborting"
	exit 1
fi

function usage {
    echo "usage: $(basename $0) [-y] [-e] [-c] [-o] [-s] [-m] [-t] [-limit somevalue] VERSION"
    echo "    -y   Assume yes to continue"
#    echo "    -e   No extentstions (only produce core and all-layers)"
    echo "    -c   No context file"
    echo "    -o   No owl file"
    echo "    -s   No schema-all.htmlfile"
    echo "    -m   No sitemap file"
    echo "    -t   No unit tests"
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
RELS=1
OWL=1
MAP=1
EXTS=0
TESTS=1
while getopts 'yecstoml:' OPTION; do
  case "$OPTION" in
    y)
        AUTORUN=1
        echo "Run unchallenged"
    ;;

    c)
        CONTEXT=0
    ;;

    s)
        RELS=0
    ;;
    m)
        MAP=0
    ;;
    t)
        TESTS=0
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


echo 
echo "$PROG:About to build release files for version $VER"
echo "      Including extensions: $EXTENSIONS"

if [ $AUTORUN -eq 0 ]
then
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

echo
echo -n "Preparing by running buildTermConfig.sh...  "
./scripts/buildTermConfig.sh
echo " Prepared."
sleep 3


echo
if [ $TESTS -eq 1 ]
then
  echo "Running Unit Tests... "
  ./scripts/run_tests.py 
  if [ $? -eq 0 ]
  then
      echo
      echo "  Unit Tests ran succesfully"
  else
      echo
      echo "  Unit Tests failed!!"
      echo "$RES"
      echo
      echo "Manually run ./scripts/run_tests.py for more details"
      echo "Aborting..."
      exit 1
  fi
else
    echo "Skipping Unit Tests"
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
    exit 1
fi
sleep 1
echo -n "Cleaning directory... "
rm -f $DIR/*.jsonld 2>&1 > /dev/null
rm -f $DIR/*.rdf 2>&1 > /dev/null
rm -f $DIR/*.nq 2>&1 > /dev/null
rm -f $DIR/*.nt 2>&1 > /dev/null
rm -f $DIR/*.ttl 2>&1 > /dev/null
rm -f $DIR/*.csv 2>&1 > /dev/null
rm -f $DIR/schema.ttl 2>&1 > /dev/null
rm -f $DIR/README.md 2>&1 > /dev/null
rm -f $DIR/schema-all.html  2>&1 > /dev/null
rm -f $DIR/schemaorg.owl  2>&1 > /dev/null
echo " cleaned."
sleep 2


echo -n "Copying README.md, SOFTWARE_README.md into release directory... "
cp ./data/schema.ttl $DIR 
cp ./README.md $DIR
cp ./SOFTWARE_README.md $DIR
echo " copied"
sleep 2

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
        for form in $LIMIT
    	do
            forms="$forms -f $form"
        
        done
    fi
    
	./scripts/exportgraphs.py -i "$in" -e "$ex1" -e "$ex2" -g "#$VER" $forms -o $DIR/$file 2>&1 > /dev/null
}

echo
echo "Creating dump files - this takes a while......."
sleep 2
echo
echo "Creating full dump files (schemaorg-current): "
#dump core extensions schema "$LIMIT"
dump "" "attic" schemaorg-current-http "$LIMIT"

echo
echo "Creating full + attic dump files (schemaorg-all): "
dump "attic" "" schemaorg-all-http "$LIMIT"

echo "Creating https versions:"
(
    cd $DIR
    for file in schemaorg-current schemaorg-all 
    do
        for ext in .ttl .rdf .jsonld .nq .nt -properties.csv -types.csv
        do
            SOURCE="${file}-http${ext}" 
            TARGET="${file}-https${ext}"
            if [ -r $SOURCE ]
            then
                echo "$SOURCE -> $TARGET"
                sed 's|http://schema.org|https://schema.org|g' $SOURCE > $TARGET
            fi
        done
    done
)

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
    echo 
    echo "Created archive context file"
    echo
    sleep 2
fi

if [ $RELS -eq 1 ]
then
    echo "creating schema-all.html file"
    ./scripts/buildreleasespage.py -o $DIR/schema-all.html
    echo
    echo "created schema-all.html file"
    echo
    sleep 2
fi
if [ $OWL -eq 1 ]
then
    echo "creating owl file"
    ./scripts/buildowlfile.py
    echo
    echo "created owl file"
    echo
    echo -n "Copying owl file to $DIR ... "
    cp ./docs/schemaorg.owl $DIR
    echo " copied."
    sleep 2
fi
if [ $RELS -eq 1 ]
then
    echo
    echo "Creating sitemap file"
    ./scripts/buildsitemap.py
    echo
    echo "created sitemap file"
    echo
    sleep 2
fi
echo "Done!"



