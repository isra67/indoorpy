#! /bin/bash

# #################################################################################
#
# Indoor system script
#	get basic system info: date, RPi S/N, network settings
#
# #################################################################################


SERIAL=`cat /proc/cpuinfo | grep -i '^serial' | grep -Eo '[a-fA-F0-9]{16}$'`
DAT=$(date "+%Y-%m-%d")
IP_ADDR=`hostname -I`
#INET=`cat /etc/network/interfaces | grep "eth0 inet" | awk '{print $4}'`
IFC_TEMP=`ifconfig eth0 | grep "inet addr"`
NETMASK=`echo $IFC_TEMP | awk '{print $4}' | sed 's/Mask://'`
BROADCAST=`echo $IFC_TEMP | awk '{print $3}' | sed 's/Bcast://'`
#NETMASK=`ifconfig eth0 | grep "inet addr" | awk '{print $4}' | sed 's/Mask://'`
#BROADCAST=`ifconfig eth0 | grep "inet addr" | awk '{print $3}' | sed 's/Bcast://'`
NETWORK=`netstat -rn | grep eth0 | awk '{if($1!="0.0.0.0") print $1}'`
GATEWAY=`netstat -rn | grep eth0 | awk '{if($1=="0.0.0.0") print $2}'`
#NS_TEMP=`netstat -rn | grep eth0`
#GATEWAY=`echo $NS_TEMP | awk '{if($1=="0.0.0.0") print $2}'`
#NETWORK=`echo $NS_TEMP | awk '{if($1!="0.0.0.0") print $1}'`
DNS=`cat /etc/resolv.conf | grep nameserver | awk 'NR==1 {print $2}'`

INET_TMP=`cat /etc/dhcpcd.conf | grep "interface eth0"`
if [ -z $INET_TMP ]; then
  INET='dhcp'
else
  INET='static'
fi

if [ -z $IP_ADDR ]; then
    IP_ADDR=127.0.0.1
fi
if [ -z $NETMASK ]; then
    NETMASK=0.0.0.0
fi
if [ -z $BROADCAST ]; then
    BROADCAST=0.0.0.0
fi
if [ -z $GATEWAY ]; then
    GATEWAY=0.0.0.0
fi
if [ -z $NETWORK ]; then
    NETWORK=0.0.0.0
fi
if [ -z $DNS ]; then
    DNS=0.0.0.0
fi

echo $DAT $SERIAL $INET $IP_ADDR $NETMASK $BROADCAST $GATEWAY $NETWORK $DNS
