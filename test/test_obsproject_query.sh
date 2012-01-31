#!/bin/bash
. ./conf_obslight.sh
#$OBSLIGHT obsproject query title description server webpage repository target architecture project_alias $PROJECTALIAS
#$OBSLIGHT obsproject query title description server webpage repository target architecture
#$OBSLIGHT obsproject query description server webpage repository target architecture title
#$OBSLIGHT obsproject query title description server 
#$OBSLIGHT obsproject query server webpage repository target architecture
#$OBSLIGHT obsproject query project_alias $PROJECTALIAS
#$OBSLIGHT obsproject query 
$OBSLIGHT obsproject query title description target architecture remoteurl maintainer bugowner server_alias $ALIAS obsproject $PROJECT
$OBSLIGHT obsproject query server_alias $ALIAS obsproject $PROJECT
$OBSLIGHT obsproject query server_alias $ALIAS obsproject $REMOTEPROJECT
$OBSLIGHT obsproject query remoteurl maintainer bugowner server_alias $ALIAS obsproject $REMOTEPROJECT

