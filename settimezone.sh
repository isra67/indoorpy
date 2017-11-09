#! /bin/bash

# #################################################################################
#
# Indoor system script
#	set time zone
#
# #################################################################################


TZ="Europe/Brussels"
if [ -n "$1" ]; then
    TZ=$1
fi

rm /etc/localtime
ln -s /usr/share/zoneinfo/$TZ /etc/localtime
rm /etc/timezone
echo $TZ | tee /etc/timezone

sync
