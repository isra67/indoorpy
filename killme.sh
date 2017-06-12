
#! /bin/bash

# #################################################################################
#
# Indoor system script
#       kill pjindoor.py app
#
# #################################################################################

pkill -9 omxplayer
ps aux | grep pjindoor | awk '{print $2}' | xargs kill -9