#!/bin/bash
cd
wget https://meego.gitorious.org/meego-developer-tools/obs-light/blobs/raw/master/test/update_and_run_tests.sh -O update_and_run_tests.sh
export DRY_RUN=false
exec update_and_run_tests.sh

