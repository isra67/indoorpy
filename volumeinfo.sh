#! /bin/bash

# #################################################################################
#
# Indoor system script
#	get USB Audio devide ID, volume, min&max value
#
# #################################################################################

VOLUMEID=`amixer controls | grep "PCM Playback Volume" | sed -e 's/,/\n/g' | awk 'NR==1 {print $1}' | sed 's/numid=//'`
VALS=`amixer cget numid=$VOLUMEID`
VOLUMEVAL=`amixer cget numid=$VOLUMEID | grep ": values" | sed 's/  : values=//' | sed -e 's/,/\n/g' | awk 'NR==1 {print $1}'`
MINVAL=`amixer cget numid=$VOLUMEID | grep "access" | sed -e 's/,/\n/g' | awk 'NR==4 {print $1}' | sed 's/min=//'`
MAXVAL=`amixer cget numid=$VOLUMEID | grep "access" | sed -e 's/,/\n/g' | awk 'NR==5 {print $1}' | sed 's/max=//'`

MICVOLUMEID=`amixer controls | grep "Mic Capture Volume" | sed -e 's/,/\n/g' | awk 'NR==1 {print $1}' | sed 's/numid=//'`
MVALS=`amixer cget numid=$MICVOLUMEID`
MICVOLUMEVAL=`amixer cget numid=$MICVOLUMEID | grep ": values" | sed 's/  : values=//' | sed -e 's/,/\n/g' | awk 'NR==1 {print $1}'`
MICMINVAL=`amixer cget numid=$MICVOLUMEID | grep "access" | sed -e 's/,/\n/g' | awk 'NR==4 {print $1}' | sed 's/min=//'`
MICMAXVAL=`amixer cget numid=$MICVOLUMEID | grep "access" | sed -e 's/,/\n/g' | awk 'NR==5 {print $1}' | sed 's/max=//'`

echo $VOLUMEID $VOLUMEVAL $MINVAL $MAXVAL $MICVOLUMEID $MICVOLUMEVAL $MICMINVAL $MICMAXVAL
