#!/bin/bash

uiFiles=`/bin/ls wizard_*.ui`

for uiFile in $uiFiles
do
  echo -n $uiFile "	-> "
  pyFile=`echo $uiFile | sed s/\.ui/\.py/`
  echo -n $pyFile
  pyside-uic -o $pyFile $uiFile
  [ "$?" -eq "0" ] && echo " OK" || echo " Failed"
done
