#!/bin/bash

APT_ARGS="--allow-unauthenticated --assume-yes"
OBSLIGHT_OPTIONS=""

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
	OBSLIGHT_OPTIONS="noaction"
fi

API_URL=http://obslightserver:81/
REPOSITORY_URL=http://obslightserver:82/
WEB_URL=http://obslightserver:80/
SERVER_ALIAS=testServer
LOGIN=obsuser
PASSWORD=opensuse

SOURCE_PROJECT='MeeGo:1.2.0:oss'
PROJECT_ALIAS='my_test_project'
PROJECT_TARGET='standard'
PROJECT_ARCH='i586'

#####################################################################
###  Utility functions  #############################################
#####################################################################

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


#####################################################################
###  Test actions  ##################################################
#####################################################################

# Update OBS Light using appropriate command for each distro
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

# Delete OBS Light and OSC configurations
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
	obslight $OBSLIGHT_OPTIONS server add server_alias $SERVER_ALIAS \
		login $LOGIN password $PASSWORD \
		api_url $API_URL repository_url $REPOSITORY_URL web_url $WEB_URL
}

function create_new_project()
{
	print "Creating project '$PROJECT_ALIAS' from '$SOURCE_PROJECT'"
	obslight $OBSLIGHT_OPTIONS obsproject add $PROJECT_ALIAS \
		$SOURCE_PROJECT $PROJECT_TARGET $PROJECT_ARCH $SERVER_ALIAS
}

function add_package()
{
	if [ $# -lt "1" ]
	then
		return 1
	fi
	print "Importing package '$1'"
	obslight $OBSLIGHT_OPTIONS package add package $1 \
		project_alias $PROJECT_ALIAS
}

function add_packages()
{
	for package in $@
	do
		add_package $package
	done
}

function add_a_few_packages()
{
	PACKAGES="tzdata fastinit nano"
	print "Importing packages: $PACKAGES"
	add_packages $PACKAGES
}

#####################################################################
###  Main loop  #####################################################
#####################################################################

if [ $# -lt "1" ]
then    
	echo "Bad number of arguments"
	usage
        exit 1
fi

update $1 || handle_error

ACTIONS="reset_conf configure_server create_new_project add_a_few_packages"
for action in $ACTIONS
do
	$action || handle_error
done


