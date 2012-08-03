#!/bin/bash

#pyside-uic come from the package "python-pyside-tools".
uiFiles=`/bin/ls ui/wizard_*.ui`

for uiFile in $uiFiles
do
  echo -n $uiFile "	-> "
  pyFile=`echo $uiFile | sed s/\.ui/\.py/`
  pyFile=`echo $pyFile | sed s/"ui\/"/"Wizard\/"/`
  echo -n $pyFile
  pyside-uic -o $pyFile $uiFile
  [ "$?" -eq "0" ] && echo " OK" || echo " Failed"
done
