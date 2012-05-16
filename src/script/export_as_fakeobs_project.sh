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
curl "$API/source/$PROJECT" > $PKGLISTFILE

# Create local git repositories for these OBS packages
for pkg in `python tools/printnames.py $PKGLISTFILE`
do
  tools/gitify-package "$PROJECT" $pkg "$API"
done

# Move them to the right place
SANITIZEDNAME=`echo $PROJECT | sed s,:,_,`
mkdir -p packages-git/$SANITIZEDNAME
mv gitrepos/* packages-git/$SANITIZEDNAME/

# Dress the list of packages and create mappings cache
find packages-git/$SANITIZEDNAME -mindepth 1 -maxdepth 1 -type d -printf "%p\n" | sort > packages-git/repos.lst
python tools/makemappings.py packages-git/repos.lst packages-git/mappingscache.xml

echo "Generating final package list..."
# Generate package list with last commit hash for each
TMPPACKAGESXML=`mktemp pkgxml-XXXX`
echo -e "<project>\n" >> $TMPPACKAGESXML
for gitrepo in `cat packages-git/repos.lst`
do
  bash tools/generate-package $gitrepo >> $TMPPACKAGESXML
done
echo -e "</project>" >> $TMPPACKAGESXML

# Copy package list at the right place
EXTENDEDPROJECTDIR=`echo $PROJECT | sed s,:,/,`
mkdir -p obs-projects/$EXTENDEDPROJECTDIR
bash tools/mergetwo $TMPPACKAGESXML > obs-projects/$EXTENDEDPROJECTDIR/packages.xml

echo "Getting project _meta..."
curl "$API/source/$PROJECT/_meta" > obs-projects/$EXTENDEDPROJECTDIR/_meta

# TODO: Get correct meta
# TODO: Get project config (_config)
# TODO: Update mappings.xml

# Remove temporary files
echo "Removing temporary files ($PKGLISTFILE $TMPPACKAGESXML)"
rm -f $PKGLISTFILE
rm -f $TMPPACKAGESXML
