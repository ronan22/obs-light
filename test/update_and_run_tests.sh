#!/bin/bash
#
# Shell script to test OBS Light with an OBS appliance
# containing a complete MeeGo distribution
#

# Default arguments for sub-commands
APT_ARGS="$APT_ARGS --allow-unauthenticated --assume-yes"
ZYPPER_ARGS="$ZYPPER_ARGS --non-interactive"
YUM_ARGS="$YUM_ARGS --assumeyes"
OBSLIGHT_OPTIONS="quiet"

# Force user to set DRY_RUN to false
[ -z "$DRY_RUN" ] && declare -r DRY_RUN=true

# Setting DEBUG to something different from false activates bash's "-x" option
[ -n "$DEBUG" -a "$DEBUG" != false ] set -x

# If we are doing a dry run, tell it to sub-commands
if [ $DRY_RUN != false ]
then
	APT_ARGS="$APT_ARGS --dry-run"
	ZYPPER_ARGS="$ZYPPER_ARGS --dry-run"
	OBSLIGHT_OPTIONS="$OBSLIGHT_OPTIONS noaction"
fi

# Check if user provided us with the address of an OBS appliance
[ -z "$OBS_HOST" ] && declare -r OBS_HOST="128.224.219.10"
declare -r API_URL="http://$OBS_HOST:81/"
declare -r REPOSITORY_URL="http://$OBS_HOST:82/"
declare -r WEB_URL="http://$OBS_HOST:80/"
declare -r SERVER_ALIAS=testServer
declare -r LOGIN=obsuser
declare -r PASSWORD=opensuse

# Check if user provided us with the name of a source project, target and arch
[ -z "$SOURCE_PROJECT" ] && declare -r SOURCE_PROJECT='MeeGo:1.2.0:oss'
[ -z "$PROJECT_TARGET" ] && declare -r PROJECT_TARGET='standard'
[ -z "$PROJECT_ARCH" ] && declare -r PROJECT_ARCH='i586'
declare -r PROJECT_ALIAS='my_test_project'

# Check if user provided us with a list of packages to test
if [ -z "$PACKAGES" ]
then
	declare -r PACKAGES="tzdata fastinit vim"
fi

#####################################################################
###  Utility functions  #############################################
#####################################################################

# Print a normal message, in green
function print()
{
	echo -e "\e[32;1m$*\e[0m"
}

# Print an error message, in red
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

# If $? != 0, print an error message and exit with status 2
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
	local DISTRO=$1
	case $DISTRO in
	"ubuntu"|"debian")
		print "Updating OBS Light using apt-get..."
		sudo apt-get update || return $?
		sudo apt-get $APT_ARGS install obslight
		;;
	"opensuse")
		print "Updating OBS Light using zypper..."
		sudo zypper $ZYPPER_ARGS refresh || return $?
		sudo zypper $ZYPPER_ARGS install obslight obslight-gui
		;;
	"fedora")
		print "Updating OBS Light using yum..."
		sudo yum $YUM_ARGS makecache || return $?
		sudo yum $YUM_ARGS update obslight obslight-gui
		;;
	*)
		print_error "Unknown distribution: '$DISTRO'"
		return 1
		;;
	esac
}

# Print the list of local packages of project $PROJECT_ALIAS
function get_all_local_packages()
{
	obslight $OBSLIGHT_OPTIONS package list project_alias $PROJECT_ALIAS
}

# Print the list of available packages of project $PROJECT_ALIAS
function get_all_available_packages()
{
	obslight $OBSLIGHT_OPTIONS package list available \
		project_alias $PROJECT_ALIAS
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

# Configure an OBS server $SERVER_ALIAS with $API_URL, $REPOSITORY_URL,
# $WEB_URL, $LOGIN, $PASSWORD
function configure_server()
{
	print "Configuring new '$SERVER_ALIAS' OBS server (URL: $API_URL)"
	obslight $OBSLIGHT_OPTIONS server add server_alias $SERVER_ALIAS \
		login $LOGIN password $PASSWORD \
		api_url $API_URL repository_url $REPOSITORY_URL web_url $WEB_URL
}

# Create a local project $PROJECT_ALIAS from $SOURCE_PROJECT
# on $SERVER_ALIAS, with target $PROJECT_TARGET and arch $PROJECT_ARCH
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
		add_package $package
		RETURN_CODE=$?
		if [ $RETURN_CODE -ne "0" ]
		then
			FAILED_PACKAGES="$FAILED_PACKAGES $package"
		fi
	done
	if [ -n "$FAILED_PACKAGES" ]
	then
		MESSAGE="Failed to add some packages: $FAILED_PACKAGES"
		print_error $MESSAGE
		ERRORS="$ERRORS\n$MESSAGE"
		return 0
	fi
}

# Calls add_packages with packages of $PACKAGES.
# Special value __ALL__ will add all available packages
function add_all_packages()
{
	if [ "$PACKAGES" = "__ALL__" ]
	then
		PACKAGES=`get_all_available_packages`
	fi
	print "Importing packages: $PACKAGES"
	add_packages $PACKAGES
}

# Create project filesystem of $PROJECT_ALIAS
function create_project_filesystem()
{
	print "Creating project filesystem (chroot jail)"
	obslight $OBSLIGHT_OPTIONS filesystem create $PROJECT_ALIAS
}

# Execute %prep of package $1
function prep_package()
{
	if [ $# -lt "1" ]
	then
		print_error "Missing argument: package name"
		return 1
	fi
	print "Importing '$1' source code in chroot jail and executing %prep"
	obslight $OBSLIGHT_OPTIONS rpmbuild prepare package $1 \
		project_alias $PROJECT_ALIAS
}

# Execute %prep of all packages in parameter
function prep_packages()
{
	local failed_packages=""
	for package in $@
	do
		prep_package $package
		local return_code=$?
		if [ $return_code -ne "0" ]
		then
			failed_packages="$failed_packages $package"
		fi
	done
	if [ -n "$failed_packages" ]
	then
		local message="Preparation failed for packages: $failed_packages"
		print_error $message
		ERRORS="$ERRORS\n$message"
	       	return 0
	fi
}

# Execute %prep of all local packages
function prep_all_packages()
{
	local all_packages=`get_all_local_packages`
	print "Preparing packages: $all_packages"
	prep_packages $all_packages
}

# Execute %files package $1
function construct_package()
{
	if [ $# -lt "1" ]
	then
		print_error "Missing argument: package name"
		return 1
	fi
	print "Constructing RPMs for '$1'"
	obslight $OBSLIGHT_OPTIONS rpmbuild buildpackage package $1 \
		project_alias $PROJECT_ALIAS
}

# Execute %files of all packages in argument
function construct_packages()
{
	local failed_packages=""
	for package in $@
	do
		construct_package $package
		local return_code=$?
		if [ $return_code -ne "0" ]
		then
			failed_packages="$failed_packages $package"
		fi
	done
	if [ -n "$failed_packages" ]
	then
		local message="Construction failed for packages: $failed_packages"
		print_error $message
		ERRORS="$ERRORS\n$message"
		return 0
	fi
}

function construct_all_packages()
{
	local all_packages=`get_all_local_packages`
	print "Constructing packages: $all_packages"
	construct_packages $all_packages
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

declare ERRORS=""

update $1 || handle_error

ACTIONS="reset_conf configure_server create_new_project create_project_filesystem"
ACTIONS="$ACTIONS add_all_packages prep_all_packages construct_all_packages"
for action in $ACTIONS
do
	$action || handle_error
done

if [ -z "$ERRORS" ]
then
	print "Finished without errors"
else
	print_error "Some errors occured:\n$ERRORS"
	exit 2
fi

