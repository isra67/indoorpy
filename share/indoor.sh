#! /bin/bash

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

pustaj() {
	while true
	do
		## working dir
		cd /root/test_stream/indoor

		## Inoteska Evidence python App
		/usr/bin/python pjindoor.py
		sleep 3
	done
}

sleep 1

## working dir
#cd /home/pi/is-kivy-test

pustaj >& /dev/null &
