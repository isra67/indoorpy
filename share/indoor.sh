#! /bin/bash

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

pustaj() {
	while true
	do
		## working dir
		cd /root/indoorpy

		## Inoteska Evidence python App
		/usr/bin/python pjindoor.py
		sleep 3
	done
}

sleep 1

clear > /dev/tty1
setterm -cursor off > /dev/tty1

## working dir
cd /root/indoorpy
./hid_init.sh

pustaj >& /dev/null &
