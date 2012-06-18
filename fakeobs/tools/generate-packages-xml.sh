#!/bin/bash
# To be executed from /srv/fakeobs

PROJECT=$1
SANITIZEDNAME=`echo $PROJECT | sed y,:,_,`
EXTENDEDPROJECTDIR=`echo $PROJECT | sed y,:,/,`

# Generate package list with last commit hash for each
TMPPACKAGESXML=`mktemp pkgxml-XXXX`
echo -e "<project>" >> $TMPPACKAGESXML
# We need to grep project name in case there are other projects listed in the file
for gitrepo in `cat packages-git/repos.lst | grep $SANITIZEDNAME`
do
  bash tools/generate-package $gitrepo >> $TMPPACKAGESXML
done
echo -e "</project>" >> $TMPPACKAGESXML

# Copy package list at the right place
bash tools/mergetwo $TMPPACKAGESXML > obs-projects/$EXTENDEDPROJECTDIR/packages.xml

rm -f $TMPPACKAGESXML
