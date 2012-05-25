#!/bin/sh

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
	  -e s,"__HOST__","$HOST" \
	  config/localhost.oscrc > $TMPOSCRC
  OSCCONFIG=$TMPOSCRC
fi

osc -c $OSCCONFIG ls > /dev/null
if [ "$?" -ne "0" ]
then
  echo "Cannot contact OBS API running on localhost"
  exit 1
fi

osc -c $OSCCONFIG meta prj fakeobs > /dev/null
if [ "$?" -eq "0" ]
then
  echo "fakeobs remote link already exists"
else
  osc -c $OSCCONFIG meta  prj -F config/fakeobs_meta "fakeobs"
  if [ "$?" -ne "0" ]
  then
    echo "Creation of the link failed"
    exit 1
  else
    echo "Link created"
  fi
fi

[ -n "$TMPOSCRC" ] && rm -f $TMPOSCRC

