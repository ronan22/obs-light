#!/bin/bash
. ./conf_obslight.sh
$OBSLIGHT obsproject query title description server webpage repository target architecture project_alias $PROJECTALIAS
$OBSLIGHT obsproject query title description server webpage repository target architecture
$OBSLIGHT obsproject query description server webpage repository target architecture title
$OBSLIGHT obsproject query title description server 
$OBSLIGHT obsproject query server webpage repository target architecture

