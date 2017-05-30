#!/bin/bash

FINAL_SCRIPT=/root/indoorpy/tunnelgetport.sh
TMP_FILE=/tmp/service

URL="http://livebackups.inoteska.sk/indoor/service.php"
DATEY=`date +%Y-%m-%d`
DATEH=`date +%H:%M:%S`
SERIAL=`cat /proc/cpuinfo | grep Serial | awk -F \: '{print $2}'`

wget -T 30 -O $TMP_FILE -o /tmp/wgets "$URL?t=$DATEY%20$DATEH&i=$SERIAL&d=$1"
service=`cat $TMP_FILE`
if [ "$service" != "" ]
    then
	echo $service $DATEY $DATEH $SERIAL $1 >$TMP_FILE
	$FINAL_SCRIPT $TMP_FILE
    else
	echo ERR
    fi