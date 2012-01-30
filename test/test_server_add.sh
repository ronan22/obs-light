#!/bin/bash
. ./conf_obslight.sh
$OBSLIGHT server add server_alias $ALIAS login $LOGIN password $PASSWORD api_url $API_URL repository_url $REPOSITORY_URL web_url $WEB_URL
