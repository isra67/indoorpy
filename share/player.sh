#! /bin/bash

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

pustaj() {
	while true
	do
		## working dir
		cd /root/test_stream/indoor

		## OmxPlayer App
		/usr/bin/omxplayer --no-osd --no-keys --win '1 1 799 429' http://192.168.1.253:8080/stream/video.h264 > /dev/null
		sleep 15
	done
}

sleep 3

## working dir
#cd /home/pi/is-kivy-test

pustaj >& /dev/null &
