#!/bin/bash

# #################################################################################
#
# Indoor system script
#	switch on|off screen backlight
#
# #################################################################################

if [ -n "$1" ]; then
    echo $1 > /sys/class/backlight/rpi_backlight/bl_power
fi