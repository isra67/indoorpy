#! /bin/bash

# #################################################################################
#
# Indoor system script
#	internal diag: date, RPi S/N, diag
#
# #################################################################################

SERIAL=`cat /proc/cpuinfo | grep -i '^serial' | grep -Eo '[a-fA-F0-9]{16}$'`
DAT=$(date "+%Y-%m-%d %H:%M:%S")

#echo $DAT $SERIAL
## INOTESKA - Diagnostika
wget -q -O /tmp/dg "http://livebackups.inoteska.sk/indoor/service.php?t=$DAT&i=$SERIAL&d=diag" &


