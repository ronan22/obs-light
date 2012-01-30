#!/bin/bash
. ./conf_obslight.sh
$OBSLIGHT server test login $LOGIN password $PASSWORD api_url $API_URL
$OBSLIGHT server test server_alias $ALIAS
