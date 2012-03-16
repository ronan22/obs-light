#!/bin/bash

APT_ARGS="--allow-unauthenticated --assume-yes"

function print()
{
	echo -e "\e[32;1m$1\e[0m"
}

# Force user to set DRY_RUN to false
if [ -z "$DRY_RUN" ]
then
	DRY_RUN=true
	print "Doing a dry run (DRY_RUN = true)"
fi

# Setting DEBUG to something different from false activates bash's "-x" option
if [ -n "$DEBUG" -a "$DEBUG" != false ]
then
	set -x
	print "Debug mode activated (DEBUG = true)"
fi

if [ $DRY_RUN != false ]
then
	APT_ARGS="$APT_ARGS --dry-run"
fi

API_URL=http://obslightserver:81/
REPOSITORY_URL=http://obslightserver:82/
WEB_URL=http://obslightserver:80/
SERVER_ALIAS=testServer

LOGIN=obsuser
PASSWORD=opensuse

function usage()
{
	echo "Usage:"
	echo "	$0 DISTRO_NAME"
	echo
	echo "DISTRO_NAME:	ubuntu, debian, opensuse, fedora"
}

function handle_error()
{
	print "An error occured (return code $?)"
	exit 2
}

function update()
{
	DISTRO=$1
	case $DISTRO in
	"ubuntu"|"debian")
		print "Updating OBS Light using apt-get..."
		sudo apt-get update || return $?
		sudo apt-get $APT_ARGS install obslight
		;;
	"opensuse")
		print "Updating OBS Light using zypper..."
		sudo zypper --non-interactive refresh --no-gpg-checks --gpg-auto-import-keys \
			|| return $?
		sudo zypper --non-interactive install obslight obslight-gui
		;;
	"fedora")
		print "Updating OBS Light using yum..."
		sudo yum --assumeyes makecache || return $?
		sudo yum --assumeyes update obslight obslight-gui
		;;
	*)
		print "Unknown distribution: $DISTRO"
		return 1
		;;
	esac
}

function reset_conf()
{
	if [ $DRY_RUN = "false" ]
       	then
		print "Removing ~/OBSLight and ~/.oscrc"
		rm -rf ~/OBSLight || return $?
		rm ~/.oscrc
	else
		print "Keeping ~/OBSLight and ~/.oscrc (DRY_RUN = true)"
	fi
}

function configure_server()
{
	print "Configuring new '$SERVER_ALIAS' OBS server (URL: $API_URL)"
	obslight server add server_alias $SERVER_ALIAS login $LOGIN password $PASSWORD \
		api_url $API_URL repository_url $REPOSITORY_URL web_url $WEB_URL
}

if [ $# -lt "1" ]
then    
	echo "Bad number of arguments"
	usage
        exit 1
fi

update $1 || handle_error
reset_conf || handle_error
configure_server || handle_error

