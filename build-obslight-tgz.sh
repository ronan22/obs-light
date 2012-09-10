#!/bin/sh

PRJ=obslight
PRJDIR=obslight
PACKAGING="$PRJDIR/packaging"

. ./build-project-tgz.sh

echo "Compressed $PRJ tar in $PRJDIR/dist"

