
#! /bin/bash

# #################################################################################
#
# Indoor system script
#       kill app
#
# #################################################################################

if [ -n "$1" ]; then
    ps aux | grep $1 | awk 'NR==1 {print $2}' | xargs kill -9
fi