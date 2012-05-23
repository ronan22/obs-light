#!/bin/sh

PROJECT=$1
RELEASE=$2

CONFDIR="obs-projects/`echo $PROJECT | sed y,:,/,`"
FULLDIR="obs-repos/$PROJECT:$RELEASE"
GITDIR="packages-git/`echo $PROJECT | sed y,:,_,`"
REPODIR="releases/$RELEASE/builds/`echo $PROJECT | cut -d ':' -f 1- --output-delimiter ':/'`"

ARCHIVENAME="`echo $PROJECT | sed y,:,_,`-$RELEASE.tar.gz"

# Create archive and save list of files
tar -cvzf $ARCHIVENAME $CONFDIR $FULLDIR $GITDIR $REPODIR

