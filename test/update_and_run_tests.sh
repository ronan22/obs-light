#!/bin/bash
#
# Shell script to test OBS Light with an OBS appliance
# containing a complete MeeGo distribution
#

# Default arguments for sub-commands
APT_ARGS="$APT_ARGS --allow-unauthenticated --assume-yes"
ZYPPER_ARGS="$ZYPPER_ARGS --non-interactive"
YUM_ARGS="$YUM_ARGS -y"
OBSLIGHT_OPTIONS="quiet"

# Force user to set DRY_RUN to false
[ -z "$DRY_RUN" ] && declare -r DRY_RUN=true

# Setting DEBUG to something different from false activates bash's "-x" option
[ -n "$DEBUG" -a "$DEBUG" != false ] && set -x

# If we are doing a dry run, tell it to sub-commands
if [ $DRY_RUN != false ]
then
	APT_ARGS="$APT_ARGS --dry-run"
	OBSLIGHT_OPTIONS="$OBSLIGHT_OPTIONS noaction"
fi

# Mailing parameters
[ -z "$FROM_ADDR" ] && declare -r FROM_ADDR="florent@fridu.net"
[ -z "$TO_ADDR" ] && declare -r TO_ADDR="florent@fridu.net"
[ -z "$SMTP_SERVER" ] && declare -r SMTP_SERVER="smtp.googlemail.com:465"
[ -z "$SMTP_PASSWORD" ] && declare -r SMTP_PASSWORD=""

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

[ -z "$MAX_RETRIES" ] && declare -r -i MAX_RETRIES=5

declare DATE=`date "+%Y-%m-%d %T"`
declare ARCH=`uname -m`
declare DISTRO
declare ERRORS=""

#####################################################################
###  Utility functions  #############################################
#####################################################################

# Print a normal message, in green
function print()
{
	echo -e "\e[32;1m$*\e[0m"
}

# Print a warning message, in yellow
function print_warning()
{
	echo -e "\e[33;1m$*\e[0m"
}

# Print an error message, in red
function print_error()
{
	echo -e "\e[31;1m$*\e[0m"
}

function usage()
{
	echo "Usage:"
	echo "	$0 [DISTRO_NAME]"
	echo
	echo "DISTRO_NAME:	ubuntu, debian, opensuse, fedora"
}

# If $? != 0, print an error message and exit with status 2
function handle_error()
{
	print_error "An error occured (return code $?)"
	return 2
}

function guess_distro()
{
	for distro in "ubuntu" "opensuse" "fedora" "debian"
	do
		[ -n "`grep -i $distro /etc/*release 2>/dev/null`" ] && echo $distro && return 0
	done
	echo "unknown"
	return 1
}

function compress_file()
{
	gzip -c $1 > $1.gz
	echo $1.gz
}

function get_emailer()
{
	local DISTRO=$1
	case $DISTRO in
	"ubuntu"|"debian")
		sudo apt-get $APT_ARGS install libio-socket-ssl-perl \
			libdigest-hmac-perl libterm-readkey-perl \
			libmime-lite-perl libfile-type-perl libio-socket-inet6-perl
		;;
	"opensuse")
		sudo zypper $ZYPPER_ARGS install perl-IO-Socket-SSL \
			perl-Digest-HMAC perl-TermReadKey perl-MIME-Lite \
			perl-File-Type perl-IO-Socket-INET6
		;;
	"fedora")
		sudo yum $YUM_ARGS install perl-IO-Socket-SSL \
			perl-Digest-HMAC perl-TermReadKey \
			perl-MIME-Lite perl-File-Type perl-IO-Socket-INET6
		;;
	*)
		print_error "Unknown distribution: '$DISTRO'"
		return 1
		;;
	esac
	print "Getting mail sending script"
	wget http://www.logix.cz/michal/devel/smtp-cli/smtp-cli -O /tmp/smtp-cli
	chmod +x /tmp/smtp-cli
}

function send_report_by_email()
{
	local body="$DATE\n$1"
	local version=`get_obslight_version`
	local subject="Test result: $version on $DISTRO $ARCH"
	local attachment=`compress_file ~/OBSLight/obslight.log`
	/tmp/smtp-cli --user "$FROM_ADDR" --pass "$SMTP_PASSWORD" \
		--server "$SMTP_SERVER" --ssl \
		--from "$FROM_ADDR" --to "$TO_ADDR" \
		--attach "$attachment" \
		--subject "$subject" --body-plain "`echo -e \"$body\"`"
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
		sudo apt-get $APT_ARGS install libio-socket-ssl-perl \
			libdigest-hmac-perl libterm-readkey-perl \
			libmime-lite-perl libfile-type-perl libio-socket-inet6-perl
		sudo apt-get $APT_ARGS install obslight
		;;
	"opensuse")
		print "Updating OBS Light using zypper..."
		sudo zypper $ZYPPER_ARGS refresh || return $?
		if [ $DRY_RUN != false ]
		then
			sudo zypper $ZYPPER_ARGS install --dry-run obslight obslight-gui
		else
			sudo zypper $ZYPPER_ARGS install obslight obslight-gui
		fi
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

function get_obslight_version()
{
	obslight $OBSLIGHT_OPTIONS --version
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


function repair_package()
{
	if [ $# -lt "1" ]
	then
		print "Missing argument: package name"
		return 1
	fi
	print "Repairing package '$1'"
	obslight $OBSLIGHT_OPTIONS package repair package $1 \
		project_alias $PROJECT_ALIAS
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
	local -i return_code=1
	local -i retries=0
	obslight $OBSLIGHT_OPTIONS package add package $1 \
		project_alias $PROJECT_ALIAS
	return_code=$?
	while [ $return_code -ne 0 -a $retries -lt $MAX_RETRIES ]
	do
		print_warning "  Package import failed ($return_code), "\
			"retrying... ($retries)"
		obslight $OBSLIGHT_OPTIONS package add package $1 \
			project_alias $PROJECT_ALIAS
		return_code=$?
		((retries++))
	done
	return $return_code
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

# Execute %files of package $1
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

function get_all_initialized_packages()
{
	local all_packages=`get_all_local_packages`
	local initialized_packages=""
	for package in $all_packages
	do
		local -l is_init
		is_init=`obslight $OBSLIGHT_OPTIONS rpmbuild isinit package $package \
				project_alias $PROJECT_ALIAS`
		if [ "$is_init" = "true" ]
		then
			initialized_packages="$initialized_packages $package"
		fi
	done
	echo $initialized_packages
}

function construct_all_packages()
{
	local packages_to_construct=`get_all_initialized_packages`
	if [ -z "$packages_to_construct" ]
	then
		print_error "No packages report to be initialized! There might be a problem..."
		ERRORS="$ERRORS\nNo packages report to be initialized! There might be a problem..."
		return 2
	fi
	print "Constructing packages: $packages_to_construct"
	construct_packages $packages_to_construct
}


#####################################################################
###  Main loop  #####################################################
#####################################################################

declare ACTIONS="reset_conf configure_server create_new_project create_project_filesystem"
ACTIONS="$ACTIONS add_all_packages prep_all_packages construct_all_packages"

if [ $# -lt "1" ]
then
	print "Trying to guess distribution"
	DISTRO=`guess_distro`
	[ $? -ne 0 ] && print_error "Could not guess the distribution" && usage && exit 1
	print " --> $DISTRO"
else
	DISTRO=$1
fi

get_emailer $DISTRO || print_error "Cannot retrieve email sending program!"
update $DISTRO || handle_error

for action in $ACTIONS
do
	$action || handle_error
	[ $? -eq "0" ] || break
done

if [ -z "$ERRORS" ]
then
	send_report_by_email "Finished without errors"
	print "Finished without errors"
else
	send_report_by_email "Some errors occured:\n$ERRORS"
	print_error "Some errors occured:\n$ERRORS"
	exit 2
fi

