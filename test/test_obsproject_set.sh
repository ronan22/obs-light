#!/bin/bash
. ./conf_obslight.sh
$OBSLIGHT obsproject query title description server webpage repository target architecture project_alias $PROJECTALIAS
$OBSLIGHT obsproject set title "test title" project_alias $PROJECTALIAS
$OBSLIGHT obsproject query title project_alias $PROJECTALIAS
$OBSLIGHT obsproject set description "test description" 
$OBSLIGHT obsproject query description
$OBSLIGHT obsproject set description "_" title "_" 
$OBSLIGHT obsproject query description title

