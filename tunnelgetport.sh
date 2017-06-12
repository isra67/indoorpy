#!/bin/bash

# #################################################################################
#
# Indoor system script
#       auto start tunnel
#
# #################################################################################


FINAL_SCRIPT=/root/indoorpy/tunnel.sh
TMP_FILE=$1

service=`cat $TMP_FILE`
words=`echo $service | awk '{print NF}'`

if [ "$words" = "7" ]
    then
    if [ -n $service ]
	then
	    PORT=`echo $service | awk '{print $2}'`
	    $FINAL_SCRIPT start $PORT
	else
	    echo ERR
	fi
    else
	echo ERR $words
    fi