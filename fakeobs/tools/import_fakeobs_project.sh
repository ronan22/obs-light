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
tar -xvf $ARCHIVE | tee $MANIFEST

echo
echo "Updating packages-git/repos.lst..."
find packages-git/ -mindepth 2 -maxdepth 2 -type d -printf "%p\n" | sort > packages-git/repos.lst

echo "Updating packages-git/mappingscache.xml..."
python tools/makemappings.py packages-git/repos.lst packages-git/mappingscache.xml

echo "Updating 'latest' links in obs-repos..."
cd obs-repos
LATEST=`find . -maxdepth 1 -name "$PROJECT*" -printf "%f\n" | grep -v "$PROJECT:latest" | sort | tail -n 1`
ln -sf $LATEST "$PROJECT:latest"
cd ..

echo "Updating 'latest' links in releases..."
cd releases
RELEASE=`find . -maxdepth 1 -type d -printf "%f\n" | sort | tail -n 1`
ln -sf $RELEASE latest
cd ..

echo "Updating mappings.xml..."
if [ -f mappings.xml ]
then
  cp -f mappings.xml mappings.xml.`date +%Y%m%d%H%M%S`
fi
tools/updatemappings.sh $PROJECT > mappings_new.xml
mv mappings_new.xml mappings.xml

DISTRUBUTIONS_PATH="/srv/www/obs/api/files/distributions.xml"
echo "Updating OBS' 'distributions.xml' file..."
if [ -f "$DISTRUBUTIONS_PATH" ]
then
	# here we assume there is only one target
	TARGET=`/bin/ls obs-repos/$PROJECT:latest/`
	tools/addfakeobsdistrib.py "$DISTRUBUTIONS_PATH" "$PROJECT" "$TARGET"
else
	echo "$DISTRUBUTIONS_PATH not found. You will have to manually update"
	echo "this file on your OBS server."
	echo "See http://en.opensuse.org/openSUSE:Build_Service_private_installation#Add_Repositories_targets"
fi
