#!/bin/bash

# #################################################################################
#
# Indoor system script
#	switch on|off screen backlight
#
# #################################################################################

echo $1 > /sys/class/backlight/rpi_backlight/bl_power