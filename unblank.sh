#!/bin/bash

#cat /sys/module/kernel/parameters/consoleblank
echo 0 >/sys/class/graphics/fb0/blank
#cat /sys/module/kernel/parameters/consoleblank
