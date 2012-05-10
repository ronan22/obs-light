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
cp -f dist/obslight*.tar.gz $INITIALDIR/src/dist/
cd $INITIALDIR
echo "Compressed tar in src/dist/"
rm -rf $TMPDIR

