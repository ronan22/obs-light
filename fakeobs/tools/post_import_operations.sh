#!/bin/sh

PROJECT=$1

echo "Updating fakeobs project mappings..."
if [ -f mappings.xml ]
then
  cp -f mappings.xml mappings.xml.`date +%Y%m%d%H%M%S`
else
  touch mappings.xml
fi
bash tools/updatemappings.sh $PROJECT > mappings_new.xml
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
