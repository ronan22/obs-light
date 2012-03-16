#!/bin/bash

function usage()
{
	echo "Usage:"
	echo "	$0 DISTRO_NAME"
	echo
	echo "DISTRO_NAME:	ubuntu, debian, opensuse, fedora"
}

function handle_error()
{
	echo "An error occured (return code $?)"
	exit 2
}

function update()
{
	DISTRO=$1
	case $DISTRO in
	"ubuntu"|"debian")
		sudo apt-get update || return $?
		sudo apt-get --allow-unauthenticated --assume-yes install obslight
		;;
	"opensuse")
		sudo zypper --non-interactive refresh --no-gpg-checks --gpg-auto-import-keys || return $?
		sudo zypper --non-interactive install obslight obslight-gui
		;;
	"fedora")
		sudo yum --assumeyes makecache || return $?
		sudo yum --assumeyes update obslight obslight-gui
		;;
	*)
		echo "Unknown distribution: $DISTRO"
		return 1
		;;
	esac
}

if [ $# -lt "1" ]
then    
	echo "Bad number of arguments"
	usage
        exit 1
fi

update $1 || handle_error

