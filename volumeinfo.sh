#! /bin/bash
VOLUMEID=`amixer controls | grep "PCM Playback Volume" | sed -e 's/,/\n/g' | awk 'NR==1 {print $1}' | sed 's/numid=//'`
VOLUMEVAL=`amixer cget numid=$VOLUMEID | grep ": values" | sed 's/  : values=//' | sed -e 's/,/\n/g' | awk 'NR==1 {print $1}'`
MINVAL=`amixer cget numid=$VOLUMEID | grep "access" | sed -e 's/,/\n/g' | awk 'NR==4 {print $1}' | sed 's/min=//'`
MAXVAL=`amixer cget numid=$VOLUMEID | grep "access" | sed -e 's/,/\n/g' | awk 'NR==5 {print $1}' | sed 's/max=//'`
echo $VOLUMEID $VOLUMEVAL $MINVAL $MAXVAL
