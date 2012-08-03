#!/bin/sh

if [ $# -ne 2 ]; then
  echo "usage: $0 <old_version> <new_version>"
  exit 1
fi

OLDVERSION=$1
NEWVERSION=$2

PRJDIR=obslight/
PACKAGING="$PRJDIR"packaging/

SPECFILE="$PACKAGING"obslight-fakeobs.spec
YAMLFILE="$PACKAGING"obslight-fakeobs.yaml

echo __________________________________________________________________________
echo $YAMLFILE
grep --color "Version: $OLDVERSION" $YAMLFILE
sed -i s/"Version: $OLDVERSION"/"Version: $NEWVERSION"/ $YAMLFILE
echo "---"
grep --color "Version: $NEWVERSION" $YAMLFILE
echo "----------------"
echo __________________________________________________________________________
echo $SPECFILE
grep --color "Version:    $OLDVERSION" $SPECFILE
sed -i s/"Version:    $OLDVERSION"/"Version:    $NEWVERSION"/ $SPECFILE
echo "---"
grep --color "Version:    $NEWVERSION" $SPECFILE
echo "----------------"
echo __________________________________________________________________________

