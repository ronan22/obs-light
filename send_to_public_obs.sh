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

TMPDIR=`mktemp -d`
PROJECTDIR=`pwd`
cd $TMPDIR
osc -A https://build.pub.meego.com co home:ronan:OBS_Light obslight
cd $PROJECTDIR
cp src/dist/obslight*.tar.gz $TMPDIR
cp obslight.spec $TMPDIR
cp debian.changelog debian.control debian.postinst debian.rules obslight.dsc $TMPDIR
cd $TMPDIR
osc ci -m "$1"
RETVAL=$?
cd $PROJECTDIR
if [ $RETVAL -eq 0 ]; then
  rm -rf $TMPDIR
  echo "DONE"
else
  echo "FAILED"
  echo "Temp dir was $TMPDIR"
fi
