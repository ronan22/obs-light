#!/bin/bash

. tools/common.sh

PROJECT=$1

if [ -z "$PROJECT" ]
then
  echo_red "Missing project argument!"
fi

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


echo
echo_green "Updating packages-git/repos.lst..."
find packages-git/ -mindepth 2 -maxdepth 2 -type d -printf "%p\n" | sort > packages-git/repos.lst

echo_green "Updating packages-git/mappingscache.xml..."
python tools/makemappings.py packages-git/repos.lst packages-git/mappingscache.xml

echo_green "Updating 'latest' links in obs-repos..."
cd obs-repos
rm -f "$PROJECT:latest"
# Do not match "$PROJECT:latest", anything ending with ":latest" or any sub-project
LATEST=`find . -maxdepth 1 -name "$PROJECT*" -printf "%f\n" | grep -v "$PROJECT:latest" | grep -v ":latest$" | grep -v "$PROJECT:.*:.*" | sort | tail -n 1`
if [ -z $LATEST ]
then
  # rm -f "$PROJECT:latest"
  echo_green "  No more releases of '$PROJECT'"
else
  echo_green "  Pointing 'latest' link to '$LATEST'"
  ln -sTf $LATEST "$PROJECT:latest"
fi
cd ..

echo_green "Updating 'latest' links in releases..."
cd releases
rm -f latest
RELEASE=`find . -maxdepth 1 -type d -printf "%f\n" | sort | tail -n 1`
if [ -n $RELEASE ]
then
  ln -sf $RELEASE latest
fi
cd ..

echo_green "Updating fakeobs project mappings..."
MAPPINGSBACKUP="mappings.xml.`date +%Y%m%d%H%M%S`"
if [ -f mappings.xml ]
then
  cp -f mappings.xml $MAPPINGSBACKUP
  bash tools/updatemappings.sh $PROJECT > mappings_new.xml
  mv mappings_new.xml mappings.xml
fi

DISTRUBUTIONS_PATH="/srv/www/obs/api/files/distributions.xml"
echo_green "Updating OBS' 'distributions.xml' file..."
if [ -f "$DISTRUBUTIONS_PATH" ]
then
  tools/removefakeobsdistrib.py "$DISTRUBUTIONS_PATH" "$PROJECT"
else
  echo_yellow "$DISTRUBUTIONS_PATH not found. You will have to manually update"
  echo_yellow "this file on your OBS server."
  echo_yellow "See http://en.opensuse.org/openSUSE:Build_Service_private_installation#Add_Repositories_targets"
fi

clean_old_mappings

