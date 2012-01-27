#!/bin/bash
set -x
../src/obslight-wrapper.py server test login obsuser password opensuse api_url http://128.224.218.244:81
../src/obslight-wrapper.py server test server_alias RepoInd
../src/obslight-wrapper.py server test server_alias meego.com
../src/obslight-wrapper.py server test server_alias OBS_251
