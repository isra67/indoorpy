#! /bin/bash

# #################################################################################
#
# Indoor system script
#	set IP address (network settings)
#
# #################################################################################

CFG_FILE="/etc/dhcpcd.conf"
IFACE="eth0"
SERVICE="dhcpcd"

# file backup
cat $CFG_FILE > "../tmp/DHCPCD.backup"

# vymazem staticke nastavenie
sed --in-place "/^interface\ $IFACE/d; /^static/d" $CFG_FILE

# ak je staticke nastavebnie, tak to pridam
if [ $1 = "static" ]; then
	NETMASK_BITS=`netmask $2/$3 | cut -f2 -d/`
	echo "interface $IFACE" >> $CFG_FILE
	echo "static ip_address=$2/$NETMASK_BITS" >> $CFG_FILE
	if [ -n $4 ]; then
		echo "static routers=$4" >> $CFG_FILE
	fi
	if [ -n $5 ]; then
		echo "static domain_name_servers=$5" >> $CFG_FILE
	fi
fi

ifconfig $IFACE 0.0.0.0
systemctl restart $SERVICE.service

sync &
