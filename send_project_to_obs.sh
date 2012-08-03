#!/bin/bash
#
# Before running this you have to:
# - run ./update_version.sh <old_version> <new_version>
# - run ./buildtgz.sh
# - update the changelogs (obslight.spec, debian.changelog)
#
set -x
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
osc -A "$OBSAPI" co -c "$OBSPROJECT" "$PRJ"
# Delete the old source archive
rm "$PRJ"/*
cd "$PRJ"
# Copy all project file to the temporary directory
cp -v "$PROJECTDIR"/"$PRJDIR"dist/"$PRJ"*.tar.gz $TMPDIR/"$PRJ"
cp -v "$PROJECTDIR"/"$PACKAGING"/* $TMPDIR/"$PRJ"
cd $TMPDIR/"$PRJ"
# Add all new files, remove disappeared files, and commit
osc -v ar 
osc -v ci -m "$1"
# Check the return value and delete (or not) the temporary directory
RETVAL=$?
cd $PROJECTDIR
if [ $RETVAL -eq 0 ]; then
  #rm -rf $TMPDIR
  echo "DONE"
else
  echo "FAILED"
  echo "Temp dir was $TMPDIR"
fi

