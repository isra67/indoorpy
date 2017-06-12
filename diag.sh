#! /bin/bash

# #################################################################################
#
# Indoor system script
#	internal diag: date, RPi S/N, diag
#
# #################################################################################

SERIAL=`/bin/cat /proc/cpuinfo | grep -i '^serial' | grep -Eo '[a-fA-F0-9]{16}$'`
DAT=$(/bin/date "+%Y-%m-%d %H:%M:%S")
CMMD=diag

if [ -n "$1" ]
then
    # zapis informacie do DB
    CMMD=$1
fi


## INOTESKA - Diagnostika
/usr/bin/wget -T 10 -q -O /tmp/dg "http://livebackups.inoteska.sk/indoor/service.php?t=$DAT&i=$SERIAL&d=$CMMD" &


