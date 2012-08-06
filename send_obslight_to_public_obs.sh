#!/bin/bash
#
# Before running this you have to:
# - run ./update_obslight_version.sh <old_version> <new_version>
# - run ./build-obslight-tgz.sh
# - update the changelogs (obslight.spec, debian.changelog)
#

PRJ=obslight
OBSPROJECT=Project:OBS_Light
OBSAPI=https://api.pub.meego.com
PRJDIR=obslight/
PACKAGING="$PRJDIR"packaging/
 
. ./send_project_to_obs.sh "$@"

