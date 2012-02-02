#!/bin/bash
. ./conf_obslight.sh
$OBSLIGHT package query title description project_alias $PROJECTALIAS package $PACKAGE
$OBSLIGHT package set title "_" description "_" project_alias $PROJECTALIAS package $PACKAGE
$OBSLIGHT package query title description project_alias $PROJECTALIAS package $PACKAGE
$OBSLIGHT package set title "_test_" description "_test_" project_alias $PROJECTALIAS package $PACKAGE
$OBSLIGHT package query title description project_alias $PROJECTALIAS package $PACKAGE
