#!/bin/bash
. ./conf_obslight.sh
$OBSLIGHT obsproject add $PROJECTALIAS $PROJECT $TARGET $ARCH $ALIAS
$OBSLIGHT projectfilesystem create $PROJECTALIAS
$OBSLIGHT package add $PACKAGE project_alias $PROJECTALIAS
$OBSLIGHT rpmbuild prepare project_alias $PROJECTALIAS package $PACKAGE
$OBSLIGHT obsproject del $PROJECTALIAS
