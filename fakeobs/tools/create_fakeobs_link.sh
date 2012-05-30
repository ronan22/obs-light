#!/bin/sh

FAKEOBSLINKNAME="fakeobs"

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

echo "Listing OBS projects to see if we can connect to..."
osc -c $OSCCONFIG ls
if [ "$?" -ne "0" ]
then
  echo "Cannot contact OBS API running on localhost"
  exit 1
fi

echo "Checking if '$FAKEOBSLINKNAME' project exists"
osc -c $OSCCONFIG meta prj $FAKEOBSLINKNAME > /dev/null
if [ "$?" -eq "0" ]
then
  echo "'$FAKEOBSLINKNAME' remote link already exists!"
else
  echo "Creating remote link project '$FAKEOBSLINKNAME'..."
  osc -c $OSCCONFIG meta  prj -F config/fakeobs_meta "$FAKEOBSLINKNAME"
  if [ "$?" -ne "0" ]
  then
    echo "Creation of the link failed!"
    exit 1
  else
    echo "Link '$FAKEOBSLINKNAME' created"
  fi
fi

[ -n "$TMPOSCRC" ] && rm -f $TMPOSCRC

