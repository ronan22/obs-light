#!/bin/bash
. ./conf_obslight.sh
AFILE=test_export
$OBSLIGHT obsproject list
$OBSLIGHT obsproject add $PROJECTALIAS $PROJECT $TARGET $ARCH $ALIAS
$OBSLIGHT obsproject list
$OBSLIGHT obsproject export $AFILE $PROJECTALIAS
$OBSLIGHT obsproject del $PROJECTALIAS
$OBSLIGHT obsproject list
if  [ -e $AFILE ] ;then echo "------------------file OK"  ;else echo "------------------file KO" ; fi
$OBSLIGHT obsproject import $AFILE
$OBSLIGHT obsproject list
$OBSLIGHT obsproject del $PROJECTALIAS
rm $AFILE

