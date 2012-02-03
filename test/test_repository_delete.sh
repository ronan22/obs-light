#!/bin/bash
. ./conf_obslight.sh
$OBSLIGHT projectfilesystem repository query $PROJECTALIAS
$OBSLIGHT projectfilesystem repository add $REPOURL $REPOALIAS $PROJECTALIAS
$OBSLIGHT projectfilesystem repository query $PROJECTALIAS
$OBSLIGHT projectfilesystem repository delete $REPOALIAS $PROJECTALIAS
$OBSLIGHT projectfilesystem repository query $PROJECTALIAS
