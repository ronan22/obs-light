#!/bin/bash
ORIG=$PWD
API=$2
TOOLS=$PWD/tools
RELEASE=$1
RSYNC=$3
PROJECT="$4"
TARGET=$5
ARCHS="$6"

SANITIZEDNAME=`echo $PROJECT | sed y,:,_,`
. tools/common.sh

if [ x$1 = x -o x$2 = x -o x$3 = x ]; then
	echo Syntax: tools/createrelease.sh RELEASE OBSAPI RSYNCURL
	exit 1
fi

if [ x$RESYNC = x ]; then
	$TOOLS/dumpbuild "$API" "$PROJECT" "$PROJECT:$RELEASE" $TARGET "$ARCHS"
	DUMPBUILDRETURNCODE=$?
fi
if [ x$PRERELEASE = x ]; then

rm -f "obs-repos/$PROJECT:latest"
ln -s "$PROJECT:$RELEASE" "obs-repos/$PROJECT:latest"

fi
grab_build()
{
	local retval=0
	SYNCPATH=$1
	NAME=$2
	mkdir -p releases/$RELEASE/builds/$NAME
	cd releases/$RELEASE/builds/$NAME
	local logfile="$PWD/$SANITIZEDNAME-$RELEASE-rsync.log"
	mkdir -p packages debug
	cd packages
	echo_green "Grabbing repositories of project '$PROJECT' target '$NAME'"
	rsync -aHx --log-file="$logfile" --progress $RSYNC/$SYNCPATH/* --exclude=*.src.rpm --exclude=repocache/ --exclude=*.repo --exclude=repodata/ --exclude=src/ --include=*.rpm .
	if [ "$?" -ne "0" ]
	then
		echo_red "Problem syncing repositories of '$PROJECT' target '$NAME'"
		echo_red "Log file: $logfile"
		retval=1
	fi
	echo_green "Deleting RPM signatures"
	find -name \*.rpm | xargs -L1 rpm --delsign
	echo_green "Moving debuginfo and debugsource RPMs to separate directory"
	mv */*-debuginfo-* ../debug
	mv */*-debugsource-* ../debug
	# Apply package groups and create repository
#	createrepo -g $ORIG/obs-projects/Core/$NAME/group.xml .
#	cp $ORIG/obs-projects/Core/$NAME/patterns.xml repodata/
#	modifyrepo repodata/patterns.xml repodata/
	# TODO: get group.xml and patterns.xml from repository, not from git
	echo_green "Creating local repository"
	createrepo .
	echo_green "Creating local repository for debuginfo and debugsource RPMs"
	# No need for package groups in debug symbolsA
	cd ../debug
	createrepo .
	cd $ORIG
	return $retval
}

if [ x$RESYNC = x -a x$NO_GRAB = x ]; then
	syncpath=`echo "$PROJECT" | cut -d ":" -f 1- --output-delimiter ":/"`
	grab_build "$syncpath/$TARGET" "$syncpath/$TARGET"
	[ "$?" -ne "0" ] && exit 1
fi

[ "$DUMPBUILDRETURNCODE" -ne "0" ] && exit 1

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
