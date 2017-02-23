#!/bin/bash

# #################################################################################
#
# Indoor system script
#	set screen brightness
#
# #################################################################################

echo $1 > /sys/class/backlight/rpi_backlight/brightness