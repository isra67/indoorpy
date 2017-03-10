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

## RPi 2 - set CPU performance:
for cpucore in /sys/devices/system/cpu/cpu?;
do
[[ -f "$cpucore" ]] || echo "performance" | tee /sys/devices/system/cpu/cpu${cpucore:(-1)}/cpufreq/scaling_governor >/dev/null;
done

sleep 1

## Audio setting:
cd /root/indoorpy
./hid_init.sh

pustaj >& /dev/null &
