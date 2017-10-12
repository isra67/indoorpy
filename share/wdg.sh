#!/bin/bash

PROCESS_NAME=python
TEST_FILE=/tmp/indoor_wd.dat
TIME_INTERVAL=14

old_val=1
new_val=0

wdg_task() {
    while true; do
	if [ -f $TEST_FILE ]
	    then
	    new_val=`cat $TEST_FILE`
	    if [ -z "$new_val" ]
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
#		 /usr/bin/pkill $PROCESS_NAME -9
		 echo "AUDIO ERROR $SUCCESS" > /tmp/test.xxx
		 echo "AUDIO ERROR" > $TEST_FILE
		 echo 1 > /dev/watchdog0
		 /sbin/reboot

#		 sleep 10
#		 SUCCESS=`ps aux | grep -c $PROCESS_NAME`
#		 echo "AUDIO ERROR $SUCCESS" > "$TEST_FILE.xxx"
#		 if [ "1" != "$SUCCESS" ]
#		    then
#		     echo "AUDIO ERROR reboot" >> $TEST_FILE
#		     echo 1 > /dev/watchdog0
#		     /sbin/reboot
#		 fi
	    fi
	fi
	sleep $TIME_INTERVAL
    done
}

wdg_task >& /dev/null &

