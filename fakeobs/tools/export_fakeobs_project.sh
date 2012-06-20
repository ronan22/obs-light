#!/bin/sh

# Example:
#   tools/export_fakeobs_project.sh "Tizen:1.0:Base" "1.0"
# will generate an archive "Tizen_1.0_Base-1.0.tar.gz"
# which can be imported by tools/import_fakeobs_project.sh

PROJECT=$1
RELEASE=$2

source tools/common.sh

CONFDIR="obs-projects/`echo $PROJECT | sed y,:,/,`"
FULLDIR="obs-repos/$PROJECT:$RELEASE"
GITDIR="packages-git/`echo $PROJECT | sed y,:,_,`"
REPODIR="releases/$RELEASE/builds/`echo $PROJECT | cut -d ':' -f 1- --output-delimiter ':/'`"

ARCHIVENAME="`echo $PROJECT | sed y,:,_,`-$RELEASE.tar.gz"

rm -f $PROJECTINFOFILE
echo "$PROJECT" "$RELEASE" > $PROJECTINFOFILE

# Create archive
tar -cvzf $ARCHIVENAME $PROJECTINFOFILE $CONFDIR $FULLDIR $GITDIR $REPODIR
if [ "$?" -eq "0" ]
then
  rm $PROJECTINFOFILE
  echo_green "Archive $PWD/$ARCHIVENAME created"
else
  rm $PROJECTINFOFILE
  echo_red "Failed to create archive $PWD/$ARCHIVENAME"
  exit 1
fi
