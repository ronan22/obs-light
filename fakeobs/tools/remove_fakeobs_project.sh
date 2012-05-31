#!/bin/sh

PROJECT=$1
MANIFEST="`echo $PROJECT | sed y,:,_,`.manifest"

if [ -f "$MANIFEST" ]
then
  echo "Removing files of project $PROJECT as listed in '$MANIFEST'..."
  cat $MANIFEST | sort -r | xargs rm -frv
else
  echo "Manifest file '$MANIFEST' not found, some files may not be removed..."
  RELEASES=`/bin/ls -1 obs-repos/ | sed -n -r s,"$PROJECT:([^:]*)$","\1",p`
  for RELEASE in $RELEASES
  do
    CONFDIR="obs-projects/`echo $PROJECT | sed y,:,/,`"
    FULLDIR="obs-repos/$PROJECT:$RELEASE"
    GITDIR="packages-git/`echo $PROJECT | sed y,:,_,`"
    REPODIR="releases/$RELEASE/builds/`echo $PROJECT | cut -d ':' -f 1- --output-delimiter ':/'`"
    rm -frv $CONFDIR
    rm -frv $FULLDIR
    rm -frv $GITDIR
    rm -frv $REPODIR
  done
fi

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

DISTRUBUTIONS_PATH="/srv/www/obs/api/files/distributions.xml"
echo "Updating OBS' 'distributions.xml' file..."
if [ -f "$DISTRUBUTIONS_PATH" ]
then
	tools/removefakeobsdistrib.py "$DISTRUBUTIONS_PATH" "$PROJECT"
else
	echo "$DISTRUBUTIONS_PATH not found. You will have to manually update"
	echo "this file on your OBS server."
	echo "See http://en.opensuse.org/openSUSE:Build_Service_private_installation#Add_Repositories_targets"
fi
