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

pustajpozadie() {
	while true
	do
		## working dir
		cd /root/indoorpy

		## Inoteska background
		/usr/bin/python runme.py
		/bin/sleep 5
	done
}


pustaj() {
	/bin/sleep 1

	while true
	do
		## working dir
		cd /root/indoorpy

		## Inoteska Evidence python App
		/usr/bin/python pjindoor.py
#		echo "LIGLO" >> /tmp/pokus.txt
		/bin/sleep 3
	done
}


## RPi 2 - set CPU performance:
for cpucore in /sys/devices/system/cpu/cpu?;
do
[[ -f "$cpucore" ]] || echo "performance" | tee /sys/devices/system/cpu/cpu${cpucore:(-1)}/cpufreq/scaling_governor >/dev/null;
done


## start WD:
cd /root/indoorpy/share
./wdg.sh &

## start node server:
pustajNode >& /dev/null &

## start background app:
pustajpozadie >& /dev/null &

/bin/sleep 2

## start python app:
pustaj >& /dev/null &
#pustaj >& /tmp/deb.txt &

## start diag:
pustajDiag >& /dev/null &
