#!/bin/sh

# Example:
#   tools/import_fakeobs_project.sh Tizen_1.0_Base-1.0.tar.gz "Tizen:1.0:Base"

# name of the archive file
ARCHIVE=$1
if [ "$#" -gt "1" ]
then
  PROJECT=$2
else
  PROJECT=`basename $ARCHIVE | sed -r -e s,"(.*)-(.*)\.tar\.gz$","\1", -e y,_,:,`
fi

if [ ! -f "$ARCHIVE" ]
then
	echo "Error: file not found: '$ARCHIVE'"
	exit 1
fi

echo "Extracting archive of project $PROJECT..."
# name of the manifest file
MANIFEST="`echo $PROJECT | sed y,:,_,`.manifest"

# extract archive and keep file list (for later removal)
set -o pipefail
tar -xvf $ARCHIVE | tee -a $MANIFEST
if [ "$?" -ne "0" ]
then
	echo "Failed to extract $ARCHIVE"
	exit 1
fi
set +o pipefail

echo "Executing post import operations..."
tools/post_import_operations.sh $PROJECT

echo "Project '$PROJECT' imported. It will be accessible on OBS by 'fakeobs:$PROJECT'"
