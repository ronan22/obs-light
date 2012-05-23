#!/bin/sh

PROJECT=$1
# TODO: check the following line
TARGET=`/bin/ls obs-repos/$PROJECT:latest/`
EXTENDEDPROJECTDIR=`echo $PROJECT | sed y,:,/,`

echo "<mappings>"
cat mappings.xml | grep -v "<mappings>" | grep -v "</mappings>" | grep -v "project=\"$PROJECT\""
echo "	<mapping project=\"$PROJECT\" path=\"obs-projects/$EXTENDEDPROJECTDIR\" binaries=\"obs-repos/$PROJECT:latest\" reponame=\"$TARGET\" />"
echo "</mappings>"