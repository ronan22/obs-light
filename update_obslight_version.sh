#!/bin/sh

if [ $# -ne 2 ]; then
  echo "usage: $0 <old_version> <new_version>"
  exit 1
fi

OLDVERSION=$1
NEWVERSION=$2

PRJDIR=obslight/
PACKAGING="$PRJDIR"packaging/

OBSLIGHTMANAGER="$PRJDIR"ObsLight/ObsLightManager.py
DEBIANLOG="$PACKAGING"debian.changelog
DEBIANDSC="$PACKAGING"obslight.dsc
OBSLIGHTYAML="$PACKAGING"obslight.yaml
OBSLIGHTSPEC="$PACKAGING"obslight.spec
OBSLIGHTSETUP="$PRJDIR"setup.py

set -x 

echo __________________________________________________________________________
echo $OBSLIGHTMANAGER
grep --color "VERSION = " $OBSLIGHTMANAGER
sed -i s/"VERSION = .*"/"VERSION = \"$NEWVERSION-1\""/ $OBSLIGHTMANAGER
echo "---"
grep --color "VERSION = " $OBSLIGHTMANAGER
echo "----------------"
echo __________________________________________________________________________
echo $DEBIANLOG
grep --color "obslight ($OLDVERSION-1)" $DEBIANLOG
sed -i s/"obslight ($OLDVERSION-1)"/"obslight ($NEWVERSION-1)"/ $DEBIANLOG
echo "---"
grep --color "obslight ($NEWVERSION-1)" $DEBIANLOG
echo "----------------"
echo __________________________________________________________________________
echo $DEBIANDSC
grep --color "Version: $OLDVERSION" $DEBIANDSC
sed -i s/"Version: $OLDVERSION"/"Version: $NEWVERSION"/ $DEBIANDSC
echo "---"
grep --color "Version: $NEWVERSION" $DEBIANDSC
echo -
grep --color "obslight_$OLDVERSION" $DEBIANDSC
sed -i s/"obslight_$OLDVERSION"/"obslight_$NEWVERSION"/ $DEBIANDSC
echo "---"
grep --color "obslight_$NEWVERSION" $DEBIANDSC
echo "----------------"
echo __________________________________________________________________________
echo $OBSLIGHTYAML
grep --color "Version: $OLDVERSION" $OBSLIGHTYAML
sed -i s/"Version: $OLDVERSION"/"Version: $NEWVERSION"/ $OBSLIGHTYAML
echo "---"
grep --color "Version: $NEWVERSION" $OBSLIGHTYAML
echo "----------------"
echo __________________________________________________________________________
echo $OBSLIGHTSPEC
grep --color "Version:    $OLDVERSION" $OBSLIGHTSPEC
sed -i s/"Version:    $OLDVERSION"/"Version:    $NEWVERSION"/ $OBSLIGHTSPEC
echo "---"
grep --color "Version:    $NEWVERSION" $OBSLIGHTSPEC
echo "----------------"
echo __________________________________________________________________________
echo $OBSLIGHTSETUP
grep --color "version=\"$OLDVERSION\"" $OBSLIGHTSETUP
sed -i s/"version=\"$OLDVERSION\""/"version=\"$NEWVERSION\""/ $OBSLIGHTSETUP
echo "---"
grep --color "version=\"$NEWVERSION\"" $OBSLIGHTSETUP

