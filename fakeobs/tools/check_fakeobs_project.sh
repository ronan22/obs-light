#!/bin/bash

source tools/common.sh

function usage()
{
	cat <<EOF
Usage: $0 <command> <project_name>

Commands:
	config
		Checks the existence of a _meta and a _config file in
		$FAKEOBSPREFIX/obs-projects/<extended/project/name>/
	full
		Checks if no RPMs is missing in
		$FAKEOBSPREFIX/obs-repos/<project_name>:latest/<target>/<arch>/
	repositories
		Checks integrity of RPMs in
		$FAKEOBSPREFIX/releases/<release>/builds/<extended:/project:/name>
	all
		Check config, full and repositories
EOF
}

function check_config()
{
	if [ "$#" -lt 1 ]
	then
		echo_red "Missing argument for check_config!"
	fi
	local project="$1"
	EXTENDEDPROJECTDIR=`echo $project | sed y,:,/,`
	EXTENDEDPROJECTDIR="$FAKEOBSPREFIX/obs-projects/$EXTENDEDPROJECTDIR"
	if [ ! -d "$EXTENDEDPROJECTDIR" ]
	then
		echo_red "Directory $EXTENDEDPROJECTDIR not found, please check project name"
		return 1
	fi

	if [ ! -f "$EXTENDEDPROJECTDIR/_meta" ]
	then
		echo_red "Project meta does not exist!"
		# curl $CURLARGS "$API/source/$PROJECT/_meta" > $EXTENDEDPROJECTDIR/_meta
	elif [ ! -s "$EXTENDEDPROJECTDIR/_meta" ]
	then
		echo_red "Project meta is empty!"
	else
		echo_green "Project meta is present"
	fi

	if [ ! -f "$EXTENDEDPROJECTDIR/_config" ]
	then
		echo_red "Project config does not exist!"
		# curl $CURLARGS "$API/source/$PROJECT/_config" > $EXTENDEDPROJECTDIR/_config
	elif [ ! -s "$EXTENDEDPROJECTDIR/_config" ]
	then
		echo_yellow "Project config is empty, may be a problem for top-level projects"
	else
		echo_green "Project config is present"
	fi
}

function check_full()
{
	if [ "$#" -lt 1 ]
	then
		echo_red "Missing argument for check_full!"
	fi
	local returncode=0
	local namesrawfile="_repository?view=names"
	local project="$1"
	local repotopdir="$FAKEOBSPREFIX/obs-repos/$project:latest/"
	if [ ! -d "$repotopdir" ]
	then
		echo_red "Directory $repotopdir not found, please check project name"
		return 1
	fi
	cd $repotopdir
	for target in `ls -1`
	do
		cd "$target" || continue
		for arch in `ls -1`
		do
			cd "$arch" || continue
			if [ ! -s "$namesrawfile" ]
			then
				echo_red "The file listing the RPMs is missing from '$PWD' or is empty!"
				echo_red "Should be '$namesrawfile'"
				returncode=1
				cd ..
				continue
			fi
			local namesfile=`mktemp rpm_names.XXXX`
			print_rpm_names "$namesrawfile" | grep -v "debuginfo.rpm" | grep -v "debugsource.rpm" > "$namesfile"
			local missingfiles=`check_missing_files $namesfile`
			if [ -n "$missingfiles" ]
			then
				returncode=1
				echo_red "The following files are missing in '$PWD':"
				echo_yellow "$missingfiles"
				echo "$missingfiles" > "missing_rpms.txt"
				echo
			else
				echo_green "$project seems OK for target $target/$arch"
			fi
			rm "$namesfile"
			cd ..
		done
		cd ..
	done
	return $returncode
}

function check_repositories()
{
	if [ "$#" -lt "1" ]
	then
		echo_red "Missing argument for check_repositories!"
	fi
	local returncode=0
	local project="$1"
	if [ -z "$project" ]
	then
		echo_red "Please specify a project name!"
		exit 1
	fi
	repodirname=`echo "$project" | cut -d ":" -f 1- --output-delimiter ":/"`
	for dir in `find $FAKEOBSPREFIX/releases -type d | grep "$repodirname\$"`
	do
		cd "$dir" || continue
		local rpmcount=`find . -name "*.rpm" | wc -l`
		if [ "$rpmcount" -lt "1" ]
		then
			echo_red "No RPM found in '$dir'!"
			returncode=1
		else
			echo_green "Found $rpmcount RPMs in '$dir'"
		fi
		echo_green "Running 'rpm -q --checksig -p' on each"
		find . -name "*.rpm" | xargs -r rpm -q --checksig -p 1>/dev/null
		if [ "$?" -ne "0" ]
		then
			returncode=1
			echo_red "Integrity test failed for some packages"
		else
			echo_green "No package failed the integrity test"
		fi
		echo
		cd ..
	done
	return $returncode
}

if [ "$#" -lt 1 ]
then
	usage
	exit 1
fi

WHATTOCHECK="$1"
shift

case $WHATTOCHECK in
	config)
		check_config "$1"
		;;
	full)
		check_full "$1"
		;;
	repositories|repos)
		check_repositories "$1"
		;;
	sources)
		echo "Not implemented."
		;;
	all)
		check_config "$1"
		check_full "$1"
		check_repositories "$1"
		;;
	usage|help|--help)
		usage
		;;
	*)
		echo "Unknown command: $WHATTOCHECK"
		usage
		exit 1
		;;
esac
