#!/bin/bash
. ./conf_obslight.sh
$OBSLIGHT projectfilesystem query path status project_alias $PROJECTALIAS
$OBSLIGHT projectfilesystem query project_alias $PROJECTALIAS
$OBSLIGHT projectfilesystem query  status project_alias $PROJECTALIAS
$OBSLIGHT projectfilesystem query path  project_alias $PROJECTALIAS
