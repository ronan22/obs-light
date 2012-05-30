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
tar -xvf $ARCHIVE | tee $MANIFEST
if [ "$?" -ne "0" ]
then
	echo "Failed to extract $ARCHIVE"
	exit 1
fi

echo
echo "Updating packages-git/repos.lst..."
find packages-git/ -mindepth 2 -maxdepth 2 -type d -printf "%p\n" | sort > packages-git/repos.lst

echo "Updating packages-git/mappingscache.xml (may be long)..."
python tools/makemappings.py packages-git/repos.lst packages-git/mappingscache.xml
if [ "$?" -ne "0" ]
then
  echo -e "\e[33;1m"
  echo " Updating mappingscache failed!"
  echo " This may append if the project contains big files and there is not enough free memory."
  echo " Please cd to '/srv/fakeobs' and run"
  echo "   python tools/makemappings.py packages-git/repos.lst packages-git/mappingscache.xml"
  echo -e "\e[0m"
fi

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

ONOBSAPPLIANCE=`grep -q "Intel OTC" /var/config_obs && echo 1 || echo 0`
if [ $ONOBSAPPLIANCE -eq 1 ]
then
  echo "This machine seems to be an OBS appliance"
  echo "  trying to automatically create a link to the fakeobs..."
  tools/create_fakeobs_link.sh
fi

DISTRUBUTIONSPATH="/srv/www/obs/api/files/distributions.xml"
echo "Updating OBS' 'distributions.xml' file..."
if [ -f "$DISTRUBUTIONSPATH" ]
then
  cp -f config/fakeobs.png /srv/www/obs/webui/public/images/distributions/
  # here we assume there is only one target
  TARGET=`/bin/ls obs-repos/$PROJECT:latest/`
  tools/addfakeobsdistrib.py "$DISTRUBUTIONSPATH" "$PROJECT" "$TARGET"
else
  echo "$DISTRUBUTIONSPATH not found."
  echo "You will have to manually update this file on your OBS server."
  echo "See http://en.opensuse.org/openSUSE:Build_Service_private_installation#Add_Repositories_targets"
fi

echo "Project '$PROJECT' imported. It will be accessible on OBS by 'fakeobs:$PROJECT'"
