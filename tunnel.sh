#!/bin/bash

# #################################################################################
#
# Indoor system script
#      build remote control access via tunnel
#
# #################################################################################


DEST="dev.inoteska.sk"
PORT=2124


if [ "$2" != "" ]
    then
	PORT=$2
    fi

tunnel_task() {
	while true; do
			ssh -N  $DEST -o "RemoteForward $PORT 127.0.0.1:22" &> /dev/null
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

