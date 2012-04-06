#!/bin/bash
#
# Run a script in a virtual machine, using Vagrant.
#
# Usage: run_vm_test.sh <script_path> <vagrant_box>
#   script_path: the path to the script you want to run
#   vagrant_box: the name of a preconfigured vagrant box
#
# A test directory (TESTDIR) will be created in $TOPDIR/<date>_<distro>
# (TOPDIR being $HOME/OBSLight_tests by default). stdout and stderr
# will be saved to $TESTDIR/test.log.
# 
# All files created in /vagrant/ inside VM will be accessible
# in $TESTDIR outside VM.
#

[ -n "$TOPDIR" ] || declare -r TOPDIR="$HOME/OBSLight_tests"
if [ $# -lt "2" ]
then
	echo "Missing arguments !"
	echo "usage: $0 <test_script> <distro>"
	exit 1
fi

declare SCRIPT=$1
declare DISTRO=$2

function make_name()
{
	local DISTRO=$1
	local DATE=`date +%Y-%m-%d_%H-%M-%S`
	echo $DATE"_"$DISTRO
}

mkdir -p $TOPDIR
declare TESTDIR="$TOPDIR/`make_name $DISTRO`"
echo "Test directory: $TESTDIR"
mkdir -p $TESTDIR
cp $SCRIPT $TESTDIR
cd $TESTDIR

# Initialize Vagrant
vagrant init $DISTRO
# Activate bridged mode
sed -i -r "s,[ \t]*#( config.vm.network :bridged), \1," Vagrantfile
# Start VM
vagrant up
# Run script
vagrant ssh -c "bash /vagrant/`basename $SCRIPT` 2>&1 | tee /vagrant/test.log"
# Shutdown VM
vagrant halt

