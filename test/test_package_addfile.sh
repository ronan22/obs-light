#!/bin/bash
. ./conf_obslight.sh
$OBSLIGHT obsproject add $PROJECTALIAS $PROJECT $TARGET $ARCH $ALIAS
$OBSLIGHT package add $PACKAGE project_alias $PROJECTALIAS
$OBSLIGHT package query listFile project_alias $PROJECTALIAS package $PACKAGE
AFILE=test_export
touch $AFILE
$OBSLIGHT package  addfile $AFILE project_alias $PROJECTALIAS package $PACKAGE
$OBSLIGHT package  query listFile project_alias $PROJECTALIAS package $PACKAGE
$OBSLIGHT package  deletefile $AFILE project_alias $PROJECTALIAS package $PACKAGE
$OBSLIGHT package  query listFile project_alias $PROJECTALIAS package $PACKAGE
$OBSLIGHT obsproject del $PROJECTALIAS
rm $AFILE
