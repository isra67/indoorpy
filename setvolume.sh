#! /bin/bash

# #################################################################################
#
# Indoor system script
#	set audio volume
#
# #################################################################################

VOLUMEID=`amixer controls | grep "PCM Playback Volume" | sed -e 's/,/\n/g' | awk 'NR==1 {print $1}' | sed 's/numid=//'`

amixer cset numid=$VOLUMEID $1%
alsactl store
