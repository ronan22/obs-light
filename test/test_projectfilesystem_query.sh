#!/bin/bash
. ./conf_obslight.sh
$OBSLIGHT projectfilesystem query path query project_alias $PROJECTALIAS
$OBSLIGHT projectfilesystem query project_alias $PROJECTALIAS
