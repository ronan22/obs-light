#!/bin/sh

INITIALDIR=`pwd`
TMPDIR=`mktemp -d`

rm -f src/dist/obslight*.tar.gz
echo "creating archive in $TMPDIR"
git archive -o $TMPDIR/obslight.tar HEAD
cd $TMPDIR
tar -xf obslight.tar
rm -f src/dist/obslight*.tar.gz
cd src
python setup.py sdist
cp -vf dist/obslight*.tar.gz $INITIALDIR/src/dist/
cd ..

MDSVERSION=`sed -rn s,"Version:\s*(.*)$","\1",p mds-tools/mds-tools.spec`
mv mds-tools mds-tools-$MDSVERSION
tar -czf mds-tools-$MDSVERSION.tar.gz mds-tools-$MDSVERSION
cp -vf mds-tools-$MDSVERSION.tar.gz $INITIALDIR/src/dist/mds-tools-$MDSVERSION.tar.gz

cd $INITIALDIR
echo "Compressed tar in src/dist/"
rm -rf $TMPDIR

