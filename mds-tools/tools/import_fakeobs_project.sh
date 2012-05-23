#!/bin/sh

# original name of the project
PROJECT=$1
# name of the archive file
ARCHIVE=$2

# extract archive and keep file list (for later removal)
tar -xvf $ARCHIVE | tee $ARCHIVE.manifest

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
tools/updatemappings.sh $PROJECT > mappings.xml

