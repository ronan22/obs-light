#!/bin/bash
. ./conf_obslight.sh
$OBSLIGHT obsproject add $PROJECTALIAS $PROJECT $TARGET $ARCH $ALIAS
$OBSLIGHT package add $PACKAGE project_alias $PROJECTALIAS
$OBSLIGHT rpmbuild isinit project_alias $PROJECTALIAS package $PACKAGE

