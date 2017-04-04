#! /bin/bash

# #################################################################################
#
# Indoor system script
#	set audio volume
#
# #################################################################################

VOLUMEID=`amixer controls | grep "Mic Capture Volume" | sed -e 's/,/\n/g' | awk 'NR==1 {print $1}' | sed 's/numid=//'`
AGCID=`amixer controls | grep "Auto Gain Control" | sed -e 's/,/\n/g' | awk 'NR==1 {print $1}' | sed 's/numid=//'`

amixer cset numid=$VOLUMEID $1%
amixer cset numid=$AGCID 0
alsactl store
