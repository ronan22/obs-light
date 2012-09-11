#!/bin/sh

INITIALDIR=`pwd`
TMPDIR=`mktemp -d`
set -x 
PRJOBSVERSION=`sed -rn s,"Version:\s*(.*)$","\1",p "$PACKAGING/$PRJ.spec"`

rm -f "$PRJ/dist"/*.tar.gz
echo "creating archive in $TMPDIR"
git archive -o "$TMPDIR/$PRJ-$PRJOBSVERSION.tar" HEAD "$PRJDIR"
cd "$TMPDIR"
tar -xf "$PRJ-$PRJOBSVERSION.tar"
mv "$PRJDIR" "$PRJ-$PRJOBSVERSION"
tar -czf "$PRJ-$PRJOBSVERSION.tar.gz" "$PRJ-$PRJOBSVERSION"
#gzip -f "$PRJ"-"$PRJOBSVERSION".tar
cp -vf "$PRJ-$PRJOBSVERSION".tar.gz "$INITIALDIR/$PRJDIR/dist/"
cd "$INITIALDIR"
rm -rf "$TMPDIR"

