#!/bin/bash
# Authors Dominig ar Foll (Intel OTC)
# Date 1 June 2011
# License GLPv2


if [ $# -ne 3 ]; then
    echo "HELP"
	echo "Function : Tag a project in an OBS (remote obs are managed via a linked project)"
	echo "           It will create a tage file which constains the MD5 to represent the package revision"
    echo "           The Tag file can be used as direct input for obs2obsCopy"
    echo ""
	echo "Usage:     $0 obs-alias project-name md5_file-name"
    echo "Example:   $0 http://myObs.mynetwork:81 meego.com:MeeGo:1.2:oss my_revision_tag.md5"
	echo " "
	echo "           meego.com can be a local projet which is a link to a remote OBS public api"
    echo "           Public API do NOT provide log info and in that case revision info will be empty"
    echo "           bs2obscopy will then copy the current release"
    echo "Version 2.0a   Licence GLPv2"
    echo ""
    exit
fi

NB_ARG=$#
ALIAS=$1
PRJ=$2
MD5_FILE=$3
LS=".obstaglist.tmp"
TAG=".obstagpkglog.tmp"

totalPkg=0

# ugly but works
echo $totalPkg > .totalPkg.cnt

# Check that current directory is writable
if [ ! -w "$PWD" ] ; then
    echo "Error : Directory $PWD is not writable"
    exit 1
fi

# Check is MD5-file is valid
touch $MD5_FILE
if [ ! -w "$MD5_FILE" ] ; then
      echo "Error: file $MD5_FILE is not writable"
      exit 2
fi
# Check that OBS is reacheable
echo -n "info : Checking connectivity with OBS ... "
osc -A $ALIAS ls $PRJ > $LS  2> /dev/null
if [ "$?" -ne 0 ] ; then
      echo ""
      echo "Error: OBS: $ALIAS or project: $DST_PRJ' cannot be reached"
      exit 3
else
      echo "DONE"
fi
echo "Creating a revision tag of source packages as present in $PRJ"


# Addition on comment at the begining of the MD5 file
echo "# This is a revision Tag file from an OBS project created by obstag" > $MD5_FILE
echo "# That MD5 Tag is directly usable by obs2obscopy script" >> $MD5_FILE
echo "#" >> $MD5_FILE
echo "# Created   : `date`" >> $MD5_FILE
echo "# Project name : $PRJ" >> $MD5_FILE
echo "#" >> $MD5_FILE
printf "# %38s | %6s | %20s | %s | %s |%s |%s \n" "pkgMd5" "pkgRev" "pkgDate" "pkgName" "pkgVersion" "pkgOwner" "pkgComment" >> $MD5_FILE
echo "#" >> $MD5_FILE

cat $LS | while read line
do
    let totalPkg++
    echo $totalPkg > .totalPkg.cnt
    echo -n "."
    pkgName="$line"
    osc -A $ALIAS log --csv $PRJ $pkgName  > $TAG   2>/dev/null
    read pkgTag < $TAG
    # presentation is ugly but bash imposes it (no space after the =
    pkgMd5=`echo     "$pkgTag" | cut -d "|" -f 4 `
	pkgRev=`echo     "$pkgTag" | cut -d "|" -f 1 `
    pkgDate=`echo    "$pkgTag" | cut -d "|" -f 3 `
    pkgOwner=`echo   "$pkgTag" | cut -d "|" -f 2 `
    pkgVersion=`echo "$pkgTag" | cut -d "|" -f 5 `
    pkgComment=`echo "$pkgTag" | cut -d "|" -f 6 `

    # Creation of the netry in the MD5 tag file
    printf "%40s | %6s | %20s | %s | %s |%s |%s \n" "$pkgMd5" "$pkgRev" "$pkgDate" "$pkgName" "$pkgVersion" "$pkgOwner" "$pkgComment" >> $MD5_FILE
done

# ugle but works
totalPkg=`cat .totalPkg.cnt`
rm .totalPkg.cnt
rm $TAG
rm $LS

echo ""
echo "Final reports"
echo "   Total number packages tagged     = $totalPkg"
echo "   $MD5_FILE created"
# if [ "$TotalPkg" -eq "0" ] ; then
	exit 1
else 
	exit 0
fi
