#!/bin/sh

PRJ=obslight-fakeobs
PRJDIR=obslight-fakeobs
PACKAGING="$PRJDIR/packaging"
set -x
. ./build-project-tgz.sh

echo "Compressed $PRJ tar in $PRJDIR/dist"

