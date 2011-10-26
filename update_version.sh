#!/bin/sh

if [ $# -ne 2 ]; then
  echo "usage: $0 <old_version> <new_version>"
  exit 1
fi

OLDVERSION=$1
NEWVERSION=$2

grep --color "obslight ($OLDVERSION-1)" debian.changelog
sed -i s/"obslight ($OLDVERSION-1)"/"obslight ($NEWVERSION-1)"/ debian.changelog
echo "---"
grep --color "obslight ($NEWVERSION-1)" debian.changelog
echo "----------------"
grep --color "Version: $OLDVERSION" obslight.dsc
sed -i s/"Version: $OLDVERSION"/"Version: $NEWVERSION"/ obslight.dsc
echo "---"
grep --color "Version: $NEWVERSION" obslight.dsc
echo "----------------"
grep --color "obslight_$OLDVERSION" obslight.dsc
sed -i s/"obslight_$OLDVERSION"/"obslight_$NEWVERSION"/ obslight.dsc
echo "---"
grep --color "obslight_$NEWVERSION" obslight.dsc
echo "----------------"
grep --color "version $OLDVERSION" obslight.spec
sed -i s/"version $OLDVERSION"/"version $NEWVERSION"/ obslight.spec
echo "---"
grep --color "version $NEWVERSION" obslight.spec
echo "----------------"
grep --color "version=\"$OLDVERSION\"" src/setup.py
sed -i s/"version=\"$OLDVERSION\""/"version=\"$NEWVERSION\""/ src/setup.py
echo "---"
grep --color "version=\"$NEWVERSION\"" src/setup.py
