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
osc -A https://api.pub.meego.com co -c home:ronan:OBS_Light obslight
osc rm obslight/obslight*.tar.gz
cd $PROJECTDIR
cp src/dist/obslight*.tar.gz $TMPDIR/obslight
cp obslight.spec $TMPDIR/obslight
cp debian.changelog debian.control debian.postinst debian.rules obslight.dsc $TMPDIR/obslight
cd $TMPDIR/obslight
osc add obslight*.tar.gz
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

