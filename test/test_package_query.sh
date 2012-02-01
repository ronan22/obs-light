#!/bin/bash
. ./conf_obslight.sh
$OBSLIGHT package query title description url  server_alias $ALIAS obsproject $PROJECT package $PACKAGE
$OBSLIGHT package query title description url  server_alias $ALIAS 
$OBSLIGHT package query server_alias $ALIAS obsproject $PROJECT package $PACKAGE
