#!/bin/sh
ORIG=$PWD
API=$2
TOOLS=$PWD/tools
RELEASE=$1
RSYNC=$3
PROJECT="$4"
TARGET=$5
ARCHS="$6"

if [ x$1 = x -o x$2 = x -o x$3 = x ]; then
	echo Syntax: tools/createrelease.sh RELEASE OBSAPI RSYNCURL
	exit 0
fi

if [ x$RESYNC = x ]; then
$TOOLS/dumpbuild "$API" "$PROJECT" "$PROJECT:$RELEASE" $TARGET "$ARCHS"
fi
if [ x$PRERELEASE = x ]; then

rm -f "obs-repos/$PROJECT:latest"
ln -s "$PROJECT:$RELEASE" "obs-repos/$PROJECT:latest"

fi
grab_build()
{
	SYNCPATH=$1
	NAME=$2
	mkdir -p releases/$RELEASE/builds/$NAME
	cd releases/$RELEASE/builds/$NAME
	mkdir -p packages debug
	cd packages
	rsync  -aHx --progress $RSYNC/$SYNCPATH/* --exclude=*.src.rpm --exclude=repocache/ --exclude=*.repo --exclude=repodata/ --exclude=src/ --include=*.rpm .
	find -name \*.rpm | xargs -L1 rpm --delsign
	mv */*-debuginfo-* ../debug
	mv */*-debugsource-* ../debug
	# Apply package groups and create repository
#	createrepo -g $ORIG/obs-projects/Core/$NAME/group.xml .
#	cp $ORIG/obs-projects/Core/$NAME/patterns.xml repodata/
#	modifyrepo repodata/patterns.xml repodata/
	# TODO: get group.xml and patterns.xml from repository, not from git
	createrepo .
	# No need for package groups in debug symbolsA
	cd ../debug
	createrepo .
	cd $ORIG
}

if [ x$RESYNC = x -a x$NO_GRAB = x ]; then
	syncpath=`echo "$PROJECT" | cut -d ":" -f 1- --output-delimiter ":/"`
	grab_build "$syncpath/$TARGET" "$syncpath/$TARGET"
fi

if [ x$NORSYNC = x1 ]; then
 exit 0
fi
if [ x$PRERELEASE = x ]; then
	echo $RELEASE > obs-repos/latest.release
	echo $RELEASE > releases/latest-release
	rm releases/latest
	ln -s $RELEASE releases/latest
fi

exit 0