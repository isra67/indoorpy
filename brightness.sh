#!/bin/bash

# #################################################################################
#
# Indoor system script
#	set screen brightness
#
# #################################################################################

VAL=50
if [ -n "$1" ];
then
    VAL=$1
fi

echo $VAL > /sys/class/backlight/rpi_backlight/brightness

sync
