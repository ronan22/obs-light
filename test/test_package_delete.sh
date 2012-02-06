#!/bin/bash
. ./conf_obslight.sh
$OBSLIGHT package list project_alias $PROJECTALIAS
$OBSLIGHT package add $PACKAGE project_alias $PROJECTALIAS
$OBSLIGHT package list project_alias $PROJECTALIAS
$OBSLIGHT package delete $PACKAGE project_alias $PROJECTALIAS
$OBSLIGHT package list project_alias $PROJECTALIAS

