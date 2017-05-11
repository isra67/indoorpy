#!/bin/bash

PROCESS_NAME=python
TEST_FILE=/tmp/indoor_wd.dat
TIME_INTERVAL=15

old_val=1
new_val=0

wdg_task() {
    while true; do
	if [ -f $TEST_FILE ]
	    then
	    new_val=`cat $TEST_FILE`
	    if [ "$new_val" == "" ]
	    then
	     #echo empty file
	     old_val=1
	    elif [ "$new_val" != "$old_val" ]
		then
		 #echo test OK
		 old_val=$new_val
		else
		 #echo test ERR
		  > $TEST_FILE
		 old_val=1
		 pkill $PROCESS_NAME -9
	    fi
	fi
	sleep $TIME_INTERVAL
    done
}

wdg_task >& /dev/null &

