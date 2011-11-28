#!/bin/sh

if [ $# -ne 2 ]; then
  echo "usage: $0 <old_version> <new_version>"
  exit 1
fi

OLDVERSION=$1
NEWVERSION=$2

grep --color "VERSION = " src/ObsLight/ObsLightManager.py
sed -i s/"VERSION = .*"/"VERSION = \"$NEWVERSION-1\""/ src/ObsLight/ObsLightManager.py
echo "---"
grep --color "VERSION = " src/ObsLight/ObsLightManager.py
echo "----------------"

grep --color "obslight ($OLDVERSION-1)" deb/debian.changelog
sed -i s/"obslight ($OLDVERSION-1)"/"obslight ($NEWVERSION-1)"/ deb/debian.changelog
echo "---"
grep --color "obslight ($NEWVERSION-1)" deb/debian.changelog
echo "----------------"

grep --color "Version: $OLDVERSION" deb/obslight.dsc
sed -i s/"Version: $OLDVERSION"/"Version: $NEWVERSION"/ deb/obslight.dsc
echo "---"
grep --color "Version: $NEWVERSION" deb/obslight.dsc
echo "----------------"

grep --color "obslight_$OLDVERSION" deb/obslight.dsc
sed -i s/"obslight_$OLDVERSION"/"obslight_$NEWVERSION"/ deb/obslight.dsc
echo "---"
grep --color "obslight_$NEWVERSION" deb/obslight.dsc
echo "----------------"

grep --color "version $OLDVERSION" rpm/obslight.spec
sed -i s/"version $OLDVERSION"/"version $NEWVERSION"/ rpm/obslight.spec
echo "---"
grep --color "version $NEWVERSION" rpm/obslight.spec
echo "----------------"

grep --color "version=\"$OLDVERSION\"" src/setup.py
sed -i s/"version=\"$OLDVERSION\""/"version=\"$NEWVERSION\""/ src/setup.py
echo "---"
grep --color "version=\"$NEWVERSION\"" src/setup.py

