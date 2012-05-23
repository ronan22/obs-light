#!/bin/sh

PROJECT=$1
MANIFEST="`echo $PROJECT | sed y,:,_,`.manifest"

echo "Removing files of project $PROJECT"
cat $MANIFEST | sort -r | xargs rm -vrf

echo
echo "Updating packages-git/repos.lst..."
find packages-git/ -mindepth 2 -maxdepth 2 -type d -printf "%p\n" | sort > packages-git/repos.lst

echo "Updating packages-git/mappingscache.xml..."
python tools/makemappings.py packages-git/repos.lst packages-git/mappingscache.xml

echo "Updating 'latest' links in obs-repos..."
cd obs-repos
LATEST=`find . -maxdepth 1 -name "$PROJECT*" -printf "%f\n" | grep -v "$PROJECT:latest" | sort | tail -n 1`
if [ -z $LATEST ]
then
  rm -f "$PROJECT:latest"
else
  ln -sf $LATEST "$PROJECT:latest"
fi
cd ..

echo "Updating 'latest' links in releases..."
cd releases
rm -f latest
RELEASE=`find . -maxdepth 1 -type d -printf "%f\n" | sort | tail -n 1`
if [ -n $RELEASE ]
then
  ln -sf $RELEASE latest
fi
cd ..

echo "Updating mappings.xml..."
MAPPINGSBACKUP="mappings.xml.`date +%Y%m%d%H%M%S`"
if [ -f mappings.xml ]
then
  cp -f mappings.xml $MAPPINGSBACKUP
  cat $MAPPINGSBACKUP | grep -v "project=\"$PROJECT\"" > mappings.xml
fi

