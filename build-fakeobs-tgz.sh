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

FAKEOBSVERSION=`sed -rn s,"Version:\s*(.*)$","\1",p fakeobs/obslight-fakeobs.spec`
mv fakeobs obslight-fakeobs-$FAKEOBSVERSION
tar -czf obslight-fakeobs-$FAKEOBSVERSION.tar.gz obslight-fakeobs-$FAKEOBSVERSION
mkdir -p $INITIALDIR/fakeobs/dist
cp -vf obslight-fakeobs-$FAKEOBSVERSION.tar.gz $INITIALDIR/fakeobs/dist/obslight-fakeobs-$FAKEOBSVERSION.tar.gz

cd $INITIALDIR
echo "Compressed obslight tar in src/dist/"
echo "Compressed obslight-fakeobs tar in fakeobs/dist/"
rm -rf $TMPDIR

