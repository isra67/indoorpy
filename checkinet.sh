#! /bin/bash

# #################################################################################
#
# Indoor system script
#       test the Internet access
#
# #################################################################################

TFILE=/tmp/inet.txt
wget --spider -T 5 http://dochadzka.inoteska.sk 2> $TFILE
R=`cat $TFILE | grep "request sent" | grep 200`

if [ -n "$R" ]; then
  echo "1"
else
  echo "0"
fi
