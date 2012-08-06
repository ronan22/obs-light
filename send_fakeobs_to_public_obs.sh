#!/bin/bash
#
# Before running this you have to:
# - run ./update_fakeobs_version.sh <old_version> <new_version>
# - run ./build-fakeobs-tgz.sh
# - update the changelogs (fakeobs.spec, debian.changelog)
#

PRJ=obslight-fakeobs 
OBSPROJECT=Project:OBS_Light
OBSAPI=https://api.pub.meego.com
PRJDIR=obslight-fakeobs/
PACKAGING="$PRJDIR"packaging/
 
. ./send_project_to_obs.sh "$@"

