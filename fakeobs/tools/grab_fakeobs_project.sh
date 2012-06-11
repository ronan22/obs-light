#!/bin/bash

# Example:
#   tools/grab_fakeobs_project.sh "1.0" "https://api.tizen.org/public" "rsync://download.tizen.org/live" "Tizen:1.0:Base" "standard" "i586 armv7el"

RELEASE=$1
API=$2
RSYNC=$3
PROJECT="$4"
TARGET=$5
ARCHS="$6"

source tools/common.sh

SANITIZEDNAME=`echo $PROJECT | sed y,:,_,`
EXTENDEDPROJECTDIR=`echo $PROJECT | sed y,:,/,`
mkdir -p packages-git/$SANITIZEDNAME
mkdir -p obs-projects/$EXTENDEDPROJECTDIR

SKIPPEDPACKAGES=""

echo_green "Creating release, getting binary RPMs..."
tools/createrelease.sh "$RELEASE" "$API" "$RSYNC" "$PROJECT" "$TARGET" "$ARCHS"

echo_green "Gitifying packages..."
# Build the list of OBS packages to prepare
PKGLISTFILE=`mktemp pkglist-XXXX`
curl $CURLARGS "$API/source/$PROJECT" > $PKGLISTFILE

# Create local git repositories for these OBS packages
for pkg in `python tools/printnames.py $PKGLISTFILE`
do
  tools/gitify-package "$PROJECT" $pkg "$API"
  if [ "$?" -ne "0" ]
  then
    SKIPPEDPACKAGES="$SKIPPEDPACKAGES $pkg"
  fi
done

# Move git repositories to the right place
mv gitrepos/* packages-git/$SANITIZEDNAME/

echo_green "Getting project _meta..."
curl $CURLARGS "$API/source/$PROJECT/_meta" > obs-projects/$EXTENDEDPROJECTDIR/_meta

echo_green "Getting project _config..."
curl $CURLARGS "$API/source/$PROJECT/_config" > obs-projects/$EXTENDEDPROJECTDIR/_config

echo_green "Executing post import operations..."
tools/post_import_operations.sh $PROJECT

echo_green "Generating final package list of project $PROJECT..."
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
bash tools/mergetwo $TMPPACKAGESXML > obs-projects/$EXTENDEDPROJECTDIR/packages.xml

# Remove temporary files
echo_green "Removing temporary files ($PKGLISTFILE $TMPPACKAGESXML)"
rm -f $PKGLISTFILE
rm -f $TMPPACKAGESXML

echo_green "Project '$PROJECT' grabbed. It will be accessible on OBS by 'fakeobs:$PROJECT'"
if [ -n "$SKIPPEDPACKAGES" ]
then
  echo_red "The following packages have been skipped because of errors:"
  echo_red "$SKIPPEDPACKAGES"
fi
