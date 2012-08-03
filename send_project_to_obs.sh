#!/bin/bash
#
# Before running this you have to:
# - run ./update_version.sh <old_version> <new_version>
# - run ./buildtgz.sh
# - update the changelogs (obslight.spec, debian.changelog)
#

if [ $# -ne 1 ]; then
  echo "usage: $0 \"commit message\""
  exit 1
fi

# Create a temporary directory and go into it
TMPDIR=`mktemp -d`
PROJECTDIR=`pwd`
cd $TMPDIR
echo TMPDIR $TMPDIR
# Checkout the project
osc -A https://api.pub.meego.com co -c Project:OBS_Light:Testing obslight
# Delete the old source archive
rm obslight/obslight*.tar.gz
cd $PROJECTDIR
# Copy all project file to the temporary directory
cp -v src/dist/obslight*.tar.gz $TMPDIR/obslight
cp -v src/rpm/obslight.spec src/rpm/obslight.yaml src/rpm/obslight.changes src/rpm/Makefile $TMPDIR/obslight
cp -v src/deb/debian.changelog src/deb/debian.control src/deb/debian.postinst src/deb/debian.prerm src/deb/debian.rules src/deb/obslight.dsc $TMPDIR/obslight
cd $TMPDIR/obslight
# Add all new files, remove disappeared files, and commit
osc -v ar 
osc -v ci -m "$1"
# Check the return value and delete (or not) the temporary directory
RETVAL=$?
cd $PROJECTDIR
if [ $RETVAL -eq 0 ]; then
  rm -rf $TMPDIR
  echo "DONE"
else
  echo "FAILED"
  echo "Temp dir was $TMPDIR"
fi

