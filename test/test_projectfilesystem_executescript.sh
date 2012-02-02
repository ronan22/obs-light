#!/bin/bash
. ./conf_obslight.sh
echo "uname -a" >/tmp/testScript.sh
$OBSLIGHT projectfilesystem executescript /tmp/testScript.sh $PROJECTALIAS
rm /tmp/testScript.sh
