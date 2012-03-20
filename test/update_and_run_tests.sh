#!/bin/bash

APT_ARGS="--allow-unauthenticated --assume-yes"
OBSLIGHT_OPTIONS=""

# Force user to set DRY_RUN to false
if [ -z "$DRY_RUN" ]
then
	DRY_RUN=true
fi

# Setting DEBUG to something different from false activates bash's "-x" option
if [ -n "$DEBUG" -a "$DEBUG" != false ]
then
	set -x
fi

if [ $DRY_RUN != false ]
then
	APT_ARGS="$APT_ARGS --dry-run"
	OBSLIGHT_OPTIONS="noaction"
fi

OBS_HOST="128.224.219.10"
API_URL="http://$OBS_HOST:81/"
REPOSITORY_URL="http://$OBS_HOST:82/"
WEB_URL="http://$OBS_HOST:80/"
SERVER_ALIAS=testServer
LOGIN=obsuser
PASSWORD=opensuse

SOURCE_PROJECT='MeeGo:1.2.0:oss'
PROJECT_ALIAS='my_test_project'
PROJECT_TARGET='standard'
PROJECT_ARCH='i586'

A_FEW_PACKAGES="tzdata fastinit nano"

#####################################################################
###  Utility functions  #############################################
#####################################################################

function print()
{
	echo -e "\e[32;1m$*\e[0m"
}

function print_error()
{
	echo -e "\e[31;1m$*\e[0m"
}

function usage()
{
	echo "Usage:"
	echo "	$0 DISTRO_NAME"
	echo
	echo "DISTRO_NAME:	ubuntu, debian, opensuse, fedora"
}

function handle_error()
{
	print_error "An error occured (return code $?)"
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
		print_error "Unknown distribution: $DISTRO"
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
		sudo rm -rf ~/OBSLight || return $?
		rm -f ~/.oscrc
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

# Calls 'obslight package add <package>' with its first parameter as package
function add_package()
{
	if [ $# -lt "1" ]
	then
		print "Missing argument: package name"
		return 1
	fi
	print "Importing package '$1'"
	obslight $OBSLIGHT_OPTIONS package add package $1 \
		project_alias $PROJECT_ALIAS
}

# Calls add_packages with each of its parameters
function add_packages()
{
	for package in $@
	do
		add_package $package || return $?
	done
}

function add_a_few_packages()
{
	print "Importing packages: $A_FEW_PACKAGES"
	add_packages $A_FEW_PACKAGES
}

function create_project_filesystem()
{
	print "Creating project filesystem (chroot jail)"
	obslight $OBSLIGHT_OPTIONS filesystem create $PROJECT_ALIAS
}

function prep_package()
{
	if [ $# -lt "1" ]
	then
		print_error "Missing argument: package name"
		return 1
	fi
	print "Importing '$0' source code in project filesystem and executing %prep"
	obslight $OBSLIGHT_OPTIONS rpmbuild prepare package $1 \
		project_alias $PROJECT_ALIAS
}

function prep_packages()
{
	for package in $@
	do
		prep_package $package || return $?
	done
}

function prep_a_few_packages()
{
	print "Preparing packages: $A_FEW_PACKAGES"
	prep_packages $A_FEW_PACKAGES
}

#####################################################################
###  Main loop  #####################################################
#####################################################################

if [ $# -lt "1" ]
then    
	print_error "Bad number of arguments"
	usage
        exit 1
fi

update $1 || handle_error

ACTIONS="reset_conf configure_server create_new_project add_a_few_packages"
ACTIONS="$ACTIONS create_project_filesystem prep_a_few_packages"
for action in $ACTIONS
do
	$action || handle_error
done

print "Finished without errors"
