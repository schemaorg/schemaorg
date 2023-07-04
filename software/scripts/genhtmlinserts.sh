#!/bin/sh
PWD=`pwd`
PROG="`basename $0`"
if [ `basename $PWD` != "schemaorg" ]
then
	echo "Not in the schemaorg directory! Aborting"
	exit 1
fi

for doc in `grep -l '##### Generated insert \[' docs/*.html templates/*.tpl`
do
    echo generating $doc
ed -s $doc <<EOF
/##### Generated insert \[CSEScript-start\]/+,/##### Generated insert \[CSEScript-end\]/-d
w
q
EOF

ed -s $doc <<EOF1
/##### Generated insert \[CSEScript-start\]/ r scripts/htmlinserts/CSEScript.txt
w
q
EOF1

######
ed -s $doc <<EOF2
/##### Generated insert \[DOCSHDR-start\]/+,/##### Generated insert \[DOCSHDR-end\]/-d
w
q
EOF2


ed -s $doc <<EOF3
/##### Generated insert \[DOCSHDR-start\]/ r scripts/htmlinserts/DOCSHDR.txt
w
q
EOF3

    
done