#!/bin/bash

PROJECT=$1
TARGET=$2
EXTENDEDPROJECTDIR=`echo $PROJECT | sed y,:,/,`

echo "<mappings>"
cat mappings.xml | grep -v "<mappings>" | grep -v "</mappings>" | grep -v "project=\"$PROJECT\""
echo "	<mapping project=\"$PROJECT\" path=\"obs-project/$EXTENDEDPROJECTDIR\" binaries=\"obs-repos/$PROJECT:latest\" reponame=\"$TARGET\" />"
echo "</mappings>"
