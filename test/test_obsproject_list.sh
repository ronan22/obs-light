#!/bin/bash
. ./conf_obslight.sh
$OBSLIGHT obsproject list server_alias $ALIAS
$OBSLIGHT obsproject list 
$OBSLIGHT obsproject list server_alias $ALIAS raw

