#!/bin/sh

PRJ=fakeobs
PRJDIR=fakeobs/
PACKAGING="$PRJDIR"packaging/

. ./build-project-tgz.sh

echo "Compressed $PRJ tar in "$PRJDIR"dist/"

