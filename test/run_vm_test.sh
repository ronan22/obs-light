#!/bin/bash
#
# Run a script in a virtual machine, using Vagrant.
#

[ -n "$TOPDIR" ] || declare -r TOPDIR="$HOME/OBSLight_tests"
#if [ $# -lt "2" ]
#then
#	echo "Missing arguments !"
#	echo "usage: $0 <distro> <test_script>"
#	exit 1
#fi

declare SCRIPT
declare DISTRO


function usage()
{
	echo "Run a script in a virtual machine, using Vagrant" >&2
	echo >&2
	echo "Usage: run_vm_test.sh -d <distribution> -s <script_path> [[-a <additional_file>] ...]" >&2
	echo >&2
	echo "	distribution:		the name of a Vagrant box" >&2
	echo "	script_path:		the path to the script to run" >&2
	echo "	additional_file:	a file to copy to TESTDIR" >&2
	echo >&2
	echo "A test directory (TESTDIR) will be created in \$TOPDIR/<date>_<distro>" >&2
	echo "(TOPDIR being $HOME/OBSLight_tests by default). stdout and stderr" >&2
	echo "will be saved to \$TESTDIR/test.log." >&2
	echo >&2
	echo "All files created in /vagrant/ inside VM will be accessible" >&2
	echo "in \$TESTDIR outside VM." >&2
}

function parse_args()
{
	while getopts "d:s:a:" opt
	do
		case $opt in
			d)
				DISTRO=$OPTARG
				;;
			s)
				SCRIPT=$OPTARG
				;;
			a)
				ADDITIONAL_FILES="$ADDITIONAL_FILES $OPTARG"
				;;
			\?)
				echo "Invalid option: -$OPTARG" >&2
				exit 1
				;;
			:)
				echo "Option -$OPTARG requires an argument." >&2
				exit 1
				;;
		esac
	done
}

function make_name()
{
	local DISTRO=$1
	local DATE=`date +%Y-%m-%d_%H-%M-%S`
	echo $DATE"_"$DISTRO
}

function copy_additional_files()
{
	for f in $ADDITIONAL_FILES
	do
		cp f
	done
}

parse_args $@

if [ -z "$DISTRO" ]
then
	echo "You must specify a distribution !" >&2
	usage
	exit 1
fi

if [ -z "$SCRIPT" ]
then
	echo "You must specify a script to run !" >&2
	usage
	exit 1
fi

# Create Vagrant directory
mkdir -p $TOPDIR
declare TESTDIR="$TOPDIR/`make_name $DISTRO`"
echo "Test directory: $TESTDIR"
mkdir -p $TESTDIR

# Copy script and additional files to Vagrant directory
cp $SCRIPT $TESTDIR
for f in $ADDITIONAL_FILES
do
	cp "$f" "$TESTDIR"
done

cd $TESTDIR

# Initialize Vagrant
vagrant init $DISTRO
# Activate bridged mode
sed -i -r "s,[ \t]*#( config.vm.network :bridged), \1," Vagrantfile
# Start VM
vagrant up
# Run script
vagrant ssh -c "cd /vagrant; ./`basename $SCRIPT` 2>&1 | tee /vagrant/test.log"
# Shutdown VM
vagrant halt

echo "Test directory was: $TESTDIR"

