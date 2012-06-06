#!/bin/bash

# Example:
#   tools/grab_fakeobs_project.sh "1.0" "https://api.tizen.org/public" "rsync://download.tizen.org/live" "Tizen:1.0:Base" "standard" "i586 armv7el"

RELEASE=$1
API=$2
RSYNC=$3
PROJECT="$4"
TARGET=$5
ARCHS="$6"

SKIPPEDPACKAGES=""

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
  if [ "$?" -ne "0" ]
  then
    SKIPPEDPACKAGES="$SKIPPEDPACKAGES $pkg"
  fi
done

# Move them to the right place
SANITIZEDNAME=`echo $PROJECT | sed y,:,_,`
mkdir -p packages-git/$SANITIZEDNAME
mv gitrepos/* packages-git/$SANITIZEDNAME/

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

echo "Executing post import operations..."
tools/post_import_operations.sh $PROJECT

# Remove temporary files
echo "Removing temporary files ($PKGLISTFILE $TMPPACKAGESXML)"
rm -f $PKGLISTFILE
rm -f $TMPPACKAGESXML

echo "Project '$PROJECT' grabbed. It will be accessible on OBS by 'fakeobs:$PROJECT'"
if [ -n "$SKIPPEDPACKAGES" ]
then
  echo -e "\e[33;1m"
  echo "The following packages have been skipped because of errors:"
  echo "$SKIPPEDPACKAGES"
  echo -e "\e[0m"
fi
