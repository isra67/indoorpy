#!/bin/bash

#IFACE="ppp0"
DEST="dev.inoteska.sk"
#DEST="192.168.1.123"
PORT=2124

#if [ "$3" != "" ]
#    then
#	DEST=$3
#    fi


if [ "$2" != "" ]
    then
	PORT=$2
    fi

tunnel_task() {
	while true; do
			ssh -N  $DEST -o "RemoteForward $PORT 127.0.0.1:22" &> /dev/null
#			ssh -N $DEST &> /dev/null
		sleep 30
	done
}

tunnel_stop() {
	pkill -9 -f "ssh -N"
	pkill -9 tunnel.sh
}


case "$1" in
  start)
	tunnel_task >& /dev/null &
	;;
  stop)
	tunnel_stop
	;;
  *)
	echo "Usage: tunnel.sh [start|stop] [PORT]" >&2
	exit 3
	;;
esac

