#! /bin/bash

PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin

WDG_FILE=/tmp/indoor_wd.dat

pustajNode() {
	while true
	do
		## working dir
		cd /root/app

		## Inoteska Evidence nodejs App
		/usr/local/bin/node server.js
		/bin/sleep 3
	done
}

pustajDiag() {
	/bin/sleep 60

	while true
	do
		## working dir
		cd /root/indoorpy

		## Diag request 1x 20min
		./tunnelservice.sh diag
		/bin/sleep 1200
	done
}

pustaj() {
	while true
	do
		## working dir
		cd /root/indoorpy

		## Inoteska Evidence python App
		/usr/bin/python pjindoor.py
		/bin/sleep 3
	done
}

/bin/sleep 1

## RPi 2 - set CPU performance:
for cpucore in /sys/devices/system/cpu/cpu?;
do
[[ -f "$cpucore" ]] || echo "performance" | tee /sys/devices/system/cpu/cpu${cpucore:(-1)}/cpufreq/scaling_governor >/dev/null;
done

/bin/sleep 1

## start WD
#echo 01 > $WDG_FILE
cd /root/indoorpy/share
./wdg.sh &

## Audio setting:
#cd /root/indoorpy
#./hid_init.sh

## IP monitor:
cd /root/indoorpy
/usr/bin/python netlink.py &

## start node server
pustajNode >& /dev/null &

## start python app
pustaj >& /dev/null &

## start diag
pustajDiag >& /dev/null &
