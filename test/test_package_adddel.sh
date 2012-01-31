#!/bin/bash
. ./conf_obslight.sh
$OBSLIGHT package add $PACKAGE project_alias $PROJECTALIAS
$OBSLIGHT package del $PACKAGE project_alias $PROJECTALIAS


