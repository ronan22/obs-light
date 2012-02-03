#!/bin/bash
. ./conf_obslight.sh
$OBSLIGHT projectfilesystem repository add $REPOURL $REPOALIAS $PROJECTALIAS
$OBSLIGHT projectfilesystem repository query  $PROJECTALIAS
$OBSLIGHT projectfilesystem repository modify $REPOALIAS newUrl $NEWREPOURL newAlias $NEWREPOALIAS project_alias $PROJECTALIAS
$OBSLIGHT projectfilesystem repository query $PROJECTALIAS
$OBSLIGHT projectfilesystem repository modify $NEWREPOALIAS newAlias $REPOALIAS project_alias $PROJECTALIAS
$OBSLIGHT projectfilesystem repository query $PROJECTALIAS
$OBSLIGHT projectfilesystem repository modify $REPOALIAS newUrl $REPOURL project_alias $PROJECTALIAS
$OBSLIGHT projectfilesystem repository query $PROJECTALIAS
$OBSLIGHT projectfilesystem repository delete $REPOALIAS $PROJECTALIAS
