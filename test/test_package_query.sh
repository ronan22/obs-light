#!/bin/bash
. ./conf_obslight.sh
#$OBSLIGHT package query title description url server_alias $ALIAS obsproject $PROJECT package $PACKAGE
$OBSLIGHT package query title listFile description url server_alias $ALIAS obsproject $PROJECT package $PACKAGE
#$OBSLIGHT package query server_alias $ALIAS obsproject $PROJECT package $PACKAGE
#$OBSLIGHT package query title description  obsRev oscRev project_alias $PROJECTALIAS package $PACKAGE
#$OBSLIGHT package query project_alias $PROJECTALIAS package $PACKAGE
