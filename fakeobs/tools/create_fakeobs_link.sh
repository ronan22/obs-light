#!/bin/sh

FAKEOBSLINKNAME="fakeobs"
source tools/common.sh

if [ "$#" -gt "0" ]
then
  OSCCONFIG=$1
else
  WEBUICONFIG="/srv/www/obs/webui/config/environments/production.rb"
  if [ ! -f "$WEBUICONFIG" ]
  then
    echo_red "OBS webui configuration file not found! Are you on an OBS appliance?"
    echo_red "Config should be at $WEBUICONFIG"
    exit 1
  fi
  HOST=`sed -rn s,"^FRONTEND_HOST\s*=\s*['\"]{1}([a-zA-Z0-9\-]*)['\"]{1}","\1",p $WEBUICONFIG`
  PORT=`sed -rn s,"^FRONTEND_PORT\s*=\s*([0-9]*)","\1",p $WEBUICONFIG`
  PROTOCOL=`sed -rn s,"^FRONTEND_PROTOCOL\s*=\s*['\"]{1}([a-zA-Z]*)['\"]{1}","\1",p $WEBUICONFIG`

  TMPOSCRC=`mktemp /tmp/localhost.oscrc-XXXX`
  sed -e s,"__PROTOCOL__","$PROTOCOL", \
	  -e s,"__PORT__","$PORT", \
	  -e s,"__HOST__","$HOST", \
	  config/localhost.oscrc > $TMPOSCRC
  OSCCONFIG=$TMPOSCRC
fi

echo_green "Listing OBS projects to see if we can connect to..."
osc -c $OSCCONFIG ls
if [ "$?" -ne "0" ]
then
  echo_red "Cannot contact OBS API running on localhost"
  exit 1
fi

echo_green "Checking if '$FAKEOBSLINKNAME' project exists..."
osc -c $OSCCONFIG meta prj $FAKEOBSLINKNAME > /dev/null
if [ "$?" -eq "0" ]
then
  echo_yellow "'$FAKEOBSLINKNAME' remote link already exists!"
else
  echo_green "  ==> The project does not exist"
  echo_green "Creating remote link project '$FAKEOBSLINKNAME'..."
  osc -c $OSCCONFIG meta  prj -F config/fakeobs_meta "$FAKEOBSLINKNAME"
  if [ "$?" -ne "0" ]
  then
    echo_red "Creation of the link failed!"
    exit 1
  else
    echo_green "Link '$FAKEOBSLINKNAME' created"
  fi
fi

[ -n "$TMPOSCRC" ] && rm -f $TMPOSCRC
