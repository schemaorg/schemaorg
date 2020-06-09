#!/bin/bash
set -e
set -u

######### run Create Site script #######
PWD="`pwd`"
PROG="`basename $0`"

echo "Run schemaorg static site creation...."

if [ `basename $PWD` != "schemaorg" ]
then
    echo "Must be run from the 'schemaorg' directory"
    exit 1
fi
if [ ! -d staticbuild ]
then
    echo "No 'staticbuild' directory here aborting!"
    exit 1
fi
if [ ! -d staticbuild/scripts ]
then
    echo "No 'staticbuild/scripts' directory here aborting!"
    exit 1
fi

if [[ ! -f 'staticbuild/scripts/createstaticsite.sh' || ! -f 'staticbuild/scripts/prebuild.py' ]]
then
    echo "Requred scripts not in 'staticbuild/scripts' aborting!"
    exit 1
fi

echo
VER=""
while [ -z "$VER" ]
do
    read -r -p "Schema.org release version: " VER
done
echo

CONFVER=`grep schemaversion ./versions.json | sed   's|[ \t]*"schemaversion" *: *"\(.*\)".*|\1|g' `

if [ "$VER" != "$CONFVER" ]
then
    echo "WARNING!! "
    echo "         Version '$VER' is not the same as defined as schemaversion in versions.json file ($CONFVER)"
    echo "Fix before continuing!!"
    echo
    exit 1
fi

RECREATE=""
if [ ! -d data/releases/${VER} ]
then
    echo "No version '$VER' in releases directory - need to build files before continuing"
    echo "Calling release files & generated pages build script..."
    scripts/buildreleasefiles.sh $VER
    RECREATE="N"
fi

while [ -z "$RECREATE" ]
do
    echo "Have any of the following changed since last build:"
    echo "   * Vocabulary definitions or contents"
    echo "   * Examples contents"
    echo "   * Documentation pages or page templates"
    read -r -p "(Y|N): " RECREATE
    case "$RECREATE" in
        y|Y)
            echo "Calling release files & generated pages build script"
            scripts/buildreleasefiles.sh $VER
            break
            ;;
        n|N)
            echo "Continuing..."
            break
            ;;
        *)
            RECREATE=""
            ;;
    esac
done
PREV=""
if [ -f "staticbuild/preversion.txt" ]
then
    PREV=`cat staticbuild/preversion.txt`
fi

BUILDSITE="Y"

if [ "$PREV" = "$VER" ]
then
    CONT=""
    while [ -z "$CONT" ]
    do
        echo
        echo "A $VER release version already built"
        read -r -p "  is this a Site Change or just a Redeploy? (C|R): " CONT
        case "$CONT" in
            c|C)
                BUILDSITE="Y"
                break
                ;;
            r|R)
                BUILDSITE="N"
                break
                ;;
            *)
                CONT=""
                ;;
        esac
    done
fi
if [ "$BUILDSITE" = "Y" ]
then
    echo
    echo  -n "Cleaning site ..."
    rm -f "staticbuild/preversion.txt"
    if [ -d "staticbuild/docs" ]
    then
        rm -rf staticbuild/docs
        echo -n " ."
    fi
    if [ -d "staticbuild/releases" ]
    then
        rm -rf staticbuild/releases
        echo -n " ."
    fi
    if [ -d "staticbuild/terms" ]
    then
        rm -rf staticbuild/terms
        echo -n " ."
    fi
    echo
    echo "Copying non-generated docs..."
    cp -r docs staticbuild/docs
    echo
    echo "Copying release downloads..."
    cp -r data/releases staticbuild/releases
    echo "Done"
    
    echo "$VER" > "staticbuild/preversion.txt"

fi
if [ "$BUILDSITE" == "Y" ]
then
    echo
    echo "Calling build script for generated docs & terms ..."
    echo
    staticbuild/scripts/prebuild.py
fi
echo
echo "Creating version specific yaml include files from templates..."
for i in handlers handlers-Local
do
    echo "   ${i}.yaml"
    sed "s/{{ver}}/$VER/g" staticbuild/${i}-template.yaml > staticbuild/${i}.yaml
done

CONT=""
while [ -z "$CONT" ]
do
    echo
    echo "Select target site:"
    echo "  S = schema.org"
    echo "  W = webschemas.org"
    echo "  O = Other development or test site"
    echo "  L = Local on this system"
    read -r -p "    (S|W|O|L): " CONT
    case "$CONT" in
        s|S)
            YAML="schemaorg.yaml"
            PROJ="-p schemaorgae"
            break
            ;;
        w|W)
            YAML="webschemasorg.yaml"
            PROJ="-p webschemas-g"
            break
            ;;
        o|O)
            YAML="other.yaml"
            PROJ=""
            break
            ;;
        l|L)
            YAML="local.yaml"
            echo
            echo "==================="
            echo "Complete..."
            echo "  To run the static site on this system"
            echo "  Change directory to '`pwd`/staticbuild'and run the following command:"
            echo "     dev_appserver.py $YAML"
            echo
            exit 0
            break
            ;;
        *)
            CONT=""
            ;;
    esac
done
echo
echo "Calling deployment script"
echo
staticbuild/scripts/deploy2gcloud.sh -e $PROJ -y $YAML
echo
echo "Complete..."
echo
exit 0





