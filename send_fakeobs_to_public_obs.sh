#!/bin/bash
#
# Before running this you have to:
# - run ./update_fakeobs_version.sh <old_version> <new_version>
# - run ./build-fakeobs-tgz.sh
# - update the changelogs (fakeobs.spec, debian.changelog)
#

PRJ=obslight-fakeobs 
OBSPROJECT=devel:OBS:Light:Stable
OBSAPI=https://api.opensuse.org
PRJDIR=obslight-fakeobs/
PACKAGING="$PRJDIR"packaging/
 
. ./send_project_to_obs.sh "$@"

