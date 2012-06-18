#!/bin/sh

# Example:
#   tools/import_fakeobs_project.sh Tizen_1.0_Base-1.0.tar.gz "Tizen:1.0:Base"

source tools/common.sh

# name of the archive file
ARCHIVE=$1
if [ ! -f "$ARCHIVE" ]
then
  echo_red "Error: file not found: '$ARCHIVE'"
  exit 1
fi

rm -f $PROJECTINFOFILE
echo_green "Looking for 'project_info' in $ARCHIVE..."
tar -xf $ARCHIVE $PROJECTINFOFILE
if [ -f $PROJECTINFOFILE ]
then
  PROJECT=`sed -rn -e s,"^([^ ]*) ([^ ]*)( .*)*$","\1",p $PROJECTINFOFILE`
  RELEASE=`sed -rn -e s,"^([^ ]*) ([^ ]*)( .*)*$","\2",p $PROJECTINFOFILE`
  rm -f $PROJECTINFOFILE
  echo_green "  Found '$PROJECT'"
else
  echo_green "  Not found"
  PROJECT=`basename $ARCHIVE | sed -r -e s,"(.*)-(.*)\.tar\.gz$","\1", -e y,_,:,`
  echo_green "Project name guessed from archive name: '$PROJECT'"
  echo_green "Is this OK ? y/N"
  declare -l USEROK
  read USEROK
  if [ "$USEROK" != "y" ]
  then
    exit 0
  fi
fi

project_exists $PROJECT
if [ "$?" -eq "0" ]
then
  echo_red "The project '$PROJECT' already exists."
  echo_red "Please remove it before trying to re-import it."
  exit 1
fi

# name of the manifest file
MANIFEST="`echo $PROJECT | sed y,:,_,`.manifest"

echo_green "Extracting archive of project $PROJECT, saving file list to $MANIFEST"
# extract archive and keep file list (for later removal)
set -o pipefail
tar -xvf $ARCHIVE | tee -a $MANIFEST
if [ "$?" -ne "0" ]
then
  echo_red "Failed to extract $ARCHIVE"
  exit 1
fi
set +o pipefail

echo_green "Executing post import operations..."
tools/post_import_operations.sh $PROJECT

echo_green "Project '$PROJECT' imported. It will be accessible on OBS by 'fakeobs:$PROJECT'"
