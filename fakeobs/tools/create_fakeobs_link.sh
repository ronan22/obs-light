#!/bin/sh

FAKEOBSLINKNAME="fakeobs"
RED="\e[31;1m"
GREEN="\e[32;1m"
YELLOW="\e[33;1m"
DEFAULT="\e[0m"

if [ "$#" -gt "0" ]
then
  OSCCONFIG=$1
else
  WEBUICONFIG="/srv/www/obs/webui/config/environments/production.rb"
  HOST=`sed -rn s,"^FRONTEND_HOST\s*=\s*['\"]{1}([a-zA-Z]*)['\"]{1}","\1",p $WEBUICONFIG`
  PORT=`sed -rn s,"^FRONTEND_PORT\s*=\s*([0-9]*)","\1",p $WEBUICONFIG`
  PROTOCOL=`sed -rn s,"^FRONTEND_PROTOCOL\s*=\s*['\"]{1}([a-zA-Z]*)['\"]{1}","\1",p $WEBUICONFIG`

  TMPOSCRC=`mktemp /tmp/localhost.oscrc-XXXX`
  sed -e s,"__PROTOCOL__","$PROTOCOL", \
	  -e s,"__PORT__","$PORT", \
	  -e s,"__HOST__","$HOST", \
	  config/localhost.oscrc > $TMPOSCRC
  OSCCONFIG=$TMPOSCRC
fi

echo -e "$GREEN" "Listing OBS projects to see if we can connect to..." "$DEFAULT"
osc -c $OSCCONFIG ls
if [ "$?" -ne "0" ]
then
  echo -e "$RED" "Cannot contact OBS API running on localhost" "$DEFAULT"
  exit 1
fi

echo -e "$GREEN" "Checking if '$FAKEOBSLINKNAME' project exists..." "$DEFAULT"
osc -c $OSCCONFIG meta prj $FAKEOBSLINKNAME > /dev/null
if [ "$?" -eq "0" ]
then
  echo -e "$YELLOW" "'$FAKEOBSLINKNAME' remote link already exists!" "$DEFAULT"
else
  echo -e "$GREEN" "  ==> The project does not exist"
  echo -e "$GREEN" "Creating remote link project '$FAKEOBSLINKNAME'..." "$DEFAULT"
  osc -c $OSCCONFIG meta  prj -F config/fakeobs_meta "$FAKEOBSLINKNAME"
  if [ "$?" -ne "0" ]
  then
    echo -e "$RED" "Creation of the link failed!" "$DEFAULT"
    exit 1
  else
    echo -e "$GREEN" "Link '$FAKEOBSLINKNAME' created" "$DEFAULT"
  fi
fi

[ -n "$TMPOSCRC" ] && rm -f $TMPOSCRC

