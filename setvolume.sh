#! /bin/bash

# #################################################################################
#
# Indoor system script
#	set audio volume
#
# #################################################################################

VOLUMEID=`amixer controls | grep "PCM Playback Volume" | sed -e 's/,/\n/g' | awk 'NR==1 {print $1}' | sed 's/numid=//'`

VOL=50
if [ -n $1 ]; then
    VOL=$1
fi

#amixer cset numid=$VOLUMEID $1%
amixer cset numid=$VOLUMEID $VOL%
alsactl store
