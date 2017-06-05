#! /bin/bash

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

pustajNode() {
	while true
	do
		## working dir
		cd /root/app

		## Inoteska Evidence nodejs App
		/usr/local/bin/node server.js
		sleep 3
	done
}

pustajDiag() {
	sleep 60

	while true
	do
		## working dir
		cd /root/indoorpy

		## Diag request 1x 20min
#		./diag.sh
		./tunnelservice.sh diag
		sleep 1200
	done
}

pustaj() {
	while true
	do
		## working dir
		cd /root/indoorpy

		## Inoteska Evidence python App
		/usr/bin/python pjindoor.py
#		/usr/bin/python test.py
		sleep 3
	done
}

sleep 1

## RPi 2 - set CPU performance:
for cpucore in /sys/devices/system/cpu/cpu?;
do
[[ -f "$cpucore" ]] || echo "performance" | tee /sys/devices/system/cpu/cpu${cpucore:(-1)}/cpufreq/scaling_governor >/dev/null;
done

sleep 1

## Audio setting:
cd /root/indoorpy
./hid_init.sh

## start node server
#/usr/local/bin/node /root/app/server >& /dev/null  &
pustajNode >& /dev/null &

## start python app
pustaj >& /dev/null &

## start diag
pustajDiag >& /dev/null &

## start WD
cd /root/indoorpy/share
./wdg.sh &
