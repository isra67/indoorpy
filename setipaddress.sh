#! /bin/bash

# #################################################################################
#
# Indoor system script
#	set IP address (network settings)
#
# #################################################################################

IFILE="/etc/network/interfaces"
DFILE="/etc/resolv.conf"
DNS=`cat $DFILE | grep "nameserver $7" | awk 'NR==1 {print $2}'`

# file backup
cat $IFILE > "$IFILE.backup"
cat $DFILE > "$DFILE.backup"

echo "\n" > $DFILE


# IP setting
echo "# ###################################################################" > $IFILE
echo "#   !!! Do not edit manualy !!!   ***   !!! Neupravujte rucne !!!   #" >> $IFILE
echo "# ###################################################################" >> $IFILE
echo "" >> $IFILE
echo "# This file describes the network interfaces available on your system" >> $IFILE
echo "# and how to activate them. For more information, see interfaces(5)." >> $IFILE
echo "" >> $IFILE
echo "# The loopback network interface" >> $IFILE
echo "auto lo" >> $IFILE
echo "iface lo inet loopback" >> $IFILE
echo "" >> $IFILE
echo "# The primary network interface" >> $IFILE
echo "auto eth0" >> $IFILE
echo "allow-hotplug eth0" >> $IFILE

if [ $1 = "dhcp" ]; then
  echo "iface eth0 inet dhcp" >> $IFILE
else
  echo "iface eth0 inet static" >> $IFILE
  echo "address $2" >> $IFILE
  echo "netmask $3" >> $IFILE
  echo "gateway $4" >> $IFILE

  # DNS setting
  if [ $5 = "" ]; then
    echo "nic"
  else
    echo "nameserver $5" > $DFILE
  fi
fi

/etc/init.d/networking restart
