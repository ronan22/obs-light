#!/bin/sh

if [ $# -ne 2 ]; then
  echo "usage: $0 <old_version> <new_version>"
  exit 1
fi

OLDVERSION=$1
NEWVERSION=$2

PRJDIR=obslight-fakeobs
PACKAGING="$PRJDIR/packaging"

SPECFILE="$PACKAGING/obslight-fakeobs.spec"
YAMLFILE="$PACKAGING/obslight-fakeobs.yaml"
DEBIANLOG="$PACKAGING/debian.changelog"
DEBIANDSC="$PACKAGING/obslight-fakeobs.dsc"
DEBIANRULES="$PACKAGING/debian.rules"

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
echo $DEBIANLOG
grep --color "obslight-fakeobs ($OLDVERSION-1)" $DEBIANLOG
sed -i s/"obslight-fakeobs ($OLDVERSION-1)"/"obslight-fakeobs ($NEWVERSION-1)"/ $DEBIANLOG
echo "---"
grep --color "obslight-fakeobs ($NEWVERSION-1)" $DEBIANLOG
echo "----------------"
echo __________________________________________________________________________
echo $DEBIANDSC
grep --color "Version: $OLDVERSION" $DEBIANDSC
sed -i s/"Version: $OLDVERSION"/"Version: $NEWVERSION"/ $DEBIANDSC
echo "---"
grep --color "Version: $NEWVERSION" $DEBIANDSC
echo -
grep --color "obslight_$OLDVERSION" $DEBIANDSC
sed -i s/"obslight-fakeobs_$OLDVERSION"/"obslight-fakeobs_$NEWVERSION"/ $DEBIANDSC
echo "---"
grep --color "obslight_$NEWVERSION" $DEBIANDSC
echo "----------------"
echo __________________________________________________________________________
echo $DEBIANRULES
grep --color "obslight-fakeobs-$OLDVERSION" $DEBIANRULES
sed -i s/"obslight-fakeobs-$OLDVERSION-"/"obslight-fakeobs-$NEWVERSION-"/ $DEBIANRULES
echo "---"
grep --color "obslight-fakeobs-$NEWVERSION" $DEBIANRULES
echo "----------------"
