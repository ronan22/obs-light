#!/bin/sh

source tools/common.sh

PROJECT=$1
# TODO: check the following line
TARGET=`/bin/ls obs-repos/$PROJECT:latest/`
if [ "$?" -ne "0" ]
then
  echo_yellow "Project '$PROJECT' does not exist, removing it from mappings" 1>&2
  TARGET=''
fi
EXTENDEDPROJECTDIR=`echo $PROJECT | sed y,:,/,`

echo "<mappings>"
cat mappings.xml | grep -v "<mappings>" | grep -v "</mappings>" | grep -v "project=\"$PROJECT\""
if [ -n "$TARGET" ]
then
  echo "	<mapping project=\"$PROJECT\" path=\"obs-projects/$EXTENDEDPROJECTDIR\" binaries=\"obs-repos/$PROJECT:latest\" reponame=\"$TARGET\" />"
fi
echo "</mappings>"
