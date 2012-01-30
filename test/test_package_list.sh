#!/bin/bash
. ./conf_obslight.sh
$OBSLIGHT package list available project_alias $PROJECTALIAS
$OBSLIGHT package list project_alias $PROJECTALIAS
$OBSLIGHT package list available 
$OBSLIGHT package list  

