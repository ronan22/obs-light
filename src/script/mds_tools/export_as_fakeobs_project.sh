#!/bin/bash

RELEASE=$1
API=$2
RSYNC=$3
PROJECT="$4"
TARGET=$5
ARCHS="$6"

echo "Creating release, getting binary RPMs..."
tools/createrelease.sh "$RELEASE" "$API" "$RSYNC" "$PROJECT" "$TARGET" "$ARCHS"

echo "Gitifying packages..."
# Build the list of OBS packages to prepare
PKGLISTFILE=`mktemp pkglist-XXXX`
curl -k "$API/source/$PROJECT" > $PKGLISTFILE

# Create local git repositories for these OBS packages
for pkg in `python tools/printnames.py $PKGLISTFILE`
do
  tools/gitify-package "$PROJECT" $pkg "$API"
done

# Move them to the right place
SANITIZEDNAME=`echo $PROJECT | sed y,:,_,`
mkdir -p packages-git/$SANITIZEDNAME
mv gitrepos/* packages-git/$SANITIZEDNAME/

# Dress the list of packages and create/update mappings cache
find packages-git/ -mindepth 2 -maxdepth 2 -type d -printf "%p\n" | sort > packages-git/repos.lst
python tools/makemappings.py packages-git/repos.lst packages-git/mappingscache.xml

echo "Generating final package list..."
# Generate package list with last commit hash for each
TMPPACKAGESXML=`mktemp pkgxml-XXXX`
echo -e "<project>" >> $TMPPACKAGESXML
# We need to grep project name in case there are other projects listed in the file
for gitrepo in `cat packages-git/repos.lst | grep $SANITIZEDNAME`
do
  bash tools/generate-package $gitrepo >> $TMPPACKAGESXML
done
echo -e "</project>" >> $TMPPACKAGESXML

# Copy package list at the right place
EXTENDEDPROJECTDIR=`echo $PROJECT | sed y,:,/,`
mkdir -p obs-projects/$EXTENDEDPROJECTDIR
bash tools/mergetwo $TMPPACKAGESXML > obs-projects/$EXTENDEDPROJECTDIR/packages.xml

echo "Getting project _meta..."
curl -k "$API/source/$PROJECT/_meta" > obs-projects/$EXTENDEDPROJECTDIR/_meta

echo "Getting project _config..."
curl -k "$API/source/$PROJECT/_config" > obs-projects/$EXTENDEDPROJECTDIR/_config

echo "Updating fakeobs project mappings..."
if [ -f mappings.xml ]
then
  cp -f mappings.xml mappings.xml.`date +%Y%m%d%H%M%S`
else
  touch mappings.xml
fi
bash tools/updatemappings.sh $PROJECT $TARGET > mappings.xml

# Remove temporary files
echo "Removing temporary files ($PKGLISTFILE $TMPPACKAGESXML)"
rm -f $PKGLISTFILE
rm -f $TMPPACKAGESXML
