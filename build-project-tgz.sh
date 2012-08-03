#!/bin/sh

INITIALDIR=`pwd`
TMPDIR=`mktemp -d`
set -x 
PRJOBSVERSION=`sed -rn s,"Version:\s*(.*)$","\1",p "$PACKAGING""$PRJ".spec`

rm -f "$PRJDIR"dist/*.tar.gz
echo "creating archive in $TMPDIR"
git archive -o $TMPDIR/"$PRJ"-"$PRJOBSVERSION".tar HEAD "$PRJDIR"
cd "$TMPDIR"
gzip -f "$PRJ"-"$PRJOBSVERSION".tar
cp -vf "$PRJ"-"$PRJOBSVERSION".tar.gz $INITIALDIR/"$PRJDIR"/dist/
cd "$INITIALDIR"
rm -rf "$TMPDIR"

