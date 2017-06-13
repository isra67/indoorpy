#!/bin/bash

# #################################################################################
#
# Indoor system script
#       get USB Audio devide ID, volume, min&max value
#
# #################################################################################


FINAL_SCRIPT=/root/indoorpy/tunnelgetport.sh
TMP_FILE=/tmp/service

URL="http://livebackups.inoteska.sk/indoor/service.php"
DATEY=`date +%Y-%m-%d`
DATEH=`date +%H:%M:%S`
SERIAL=`cat /proc/cpuinfo | grep Serial | awk -F \: '{print $2}'`


CMMD=diag
if [ -n "$1" ]
then
    # zapis informacie do DB
    CMMD=$1
fi


wget -T 30 -O $TMP_FILE -o /tmp/wgets "$URL?t=$DATEY%20$DATEH&i=$SERIAL&d=$CMMD"

service=`cat $TMP_FILE`
if [ -n "$service" ]
    then
	echo $service $DATEY $DATEH $SERIAL $CMMD >$TMP_FILE
	$FINAL_SCRIPT $TMP_FILE
    else
	echo ERR
    fi