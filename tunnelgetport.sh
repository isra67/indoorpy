#!/bin/bash

FINAL_SCRIPT=/root/indoorpy/tunnel.sh
TMP_FILE=$1

service=`cat $TMP_FILE`
words=`echo $service | awk '{print NF}'`

#echo $words

if [ "$words" == "7" ]
    then
    if [ "$service" != "" ]
	then
	    PORT=`echo $service | awk '{print $2}'`
#	echo $PORT
	    $FINAL_SCRIPT start $PORT
	else
	    echo ERR
	fi
    else
	echo ERR $words
    fi