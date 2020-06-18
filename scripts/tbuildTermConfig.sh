#!/bin/bash
set -e
set -u

PWD="`pwd`"
PROG="`basename $0`"
if [ `basename "$PWD"` != "schemaorg" ]
then
	echo "$PROG: Not in the schemaorg directory! Aborting"
	exit 1
fi

REALTARGET="${PWD}/sdoconfigTermsData.json"
TARGET="${REALTARGET}.tmp"
LOCVARIABLE='[[VOCABDEFLOC]]/'
Header="{
    \"@context\": {
        \"@vocab\": \"http://configfiles.schema.org/\"
    },
    \"@type\": \"DataFeed\",
    \"name\": \"schema.org\","
    
function doHead {
        printf ",\n        {
            \"@type\": \"DataDownload\",
            \"fileContent\": \"${2}\",
            \"contentLocation\": \"${LOCVARIABLE}${1}\",
            \"contentFile\": [\n" >> "$TARGET"
    
    }

function doExtension {
    dir=$1 
    ( 
    cd $dir
    count=0
    output=0
    for rdf in *.ttl
    do
        if [ "$rdf" != '*.ttl' ]
        then
            sep=",\n"
            if [ $count -eq 0 ]
            then
                doHead $dir "terms"
                sep=""
                output=1
            fi
            printf "$sep                \"$rdf\"" >> "$TARGET"
            count=$((count+1))
        fi
    done
    if [ $count -ne 0 ]
    then
        printf "\n            ]\n
        }"  >> "$TARGET"
    fi

    count=0
    for ex in *examples.txt
    do
        if [ "$ex" != '*examples.txt' ]
        then
            sep=",\n"
            if [ $count -eq 0 ]
            then
                doHead $dir "examples"
                output=1
                sep=""
            fi
            printf "$sep                \"$ex\"" >> "$TARGET"
            count=$((count+1))
        fi
    done
    if [ $count -ne 0 ]
    then
        printf "\n            ]\n
        }"   >> "$TARGET"
    fi
    )
        return 
}

function doDocs {
    echo "        {
            \"@type\": \"DataDownload\",
            \"fileContent\": \"docs\",
            \"contentLocation\": \"${LOCVARIABLE}docs\",
            \"contentFile\": [" >> "$TARGET"
    
            
    count=0
    for i in `(cd docs;find * -type f -print)`
    do 
    sep=",\n"
    if [ $count -eq 0 ]
    then
        sep=""
    fi 
    count=$((count+1))
    printf "$sep                \"$i\"" >> "$TARGET"
    
    
    done
    printf "
                ]
        }" >> "$TARGET"

}

function doElements {
    echo "    \"dataFeedElement\": [" >> "$TARGET"
    doDocs
    doExtension data
    for ext in `ls data/ext` 
    do
        doExtension "data/ext/$ext"
    done
    echo "
    ]
}" >> "$TARGET"

}

######### Build file

printf "{
    \"@context\": {
        \"@vocab\": \"http://configfiles.schema.org/\"
    },
    \"@type\": \"DataFeed\",
    \"name\": \"schema.org\"," > "$TARGET"
echo >> "$TARGET"

doElements


########Only overwite if different
if [ ! -f "$REALTARGET" ]
then
    mv $TARGET $REALTARGET
elif `cmp -s $REALTARGET $TARGET`
then
    rm -f $TARGET
else
    mv $TARGET $REALTARGET
fi
