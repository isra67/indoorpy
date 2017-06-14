
#!/bin/python

# ###############################################################
#
# NetLink socket
#
# ###############################################################

from kivy.logger import Logger

from itools import *

import os
import socket
import struct
import time

netstatus = 1

def procNetlink():
    "listen to system NETLINK socket"
    global netstatus

    # These constants map to constants in the Linux kernel. This is a crappy
    # way to get at them, but it'll do for now.
    RTMGRP_LINK = 1
    RTMGRP_IPV4_IFADDR = 0x10

    NLMSG_NOOP = 1
    NLMSG_ERROR = 2

    RTM_NEWLINK = 16
    RTM_DELLINK = 17
    RTM_NEWADDR = 20
    RTM_DELADDR = 21

    IFLA_ADDRESS = 1
    IFLA_IFNAME = 3

    WAIT_TXT = ' wait...'
    OK_TXT = ' OK '
    NO_TXT = ' NO '
    ERR_TXT = ' ERROR '
    NONE_TXT = ' None '
    UP_TXT = ' up '
    DOWN_TXT = ' down '


    # Create the netlink socket and bind to RTMGRP_LINK,
    s = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, socket.NETLINK_ROUTE)
#    s.bind((os.getpid(), RTMGRP_LINK))
    s.bind((0, -1))

    old_msg = -1
    link_status = ''

    while True:
        time.sleep(.2)

        data = s.recv(65535)
        msg_len, msg_type, flags, seq, pid = struct.unpack("=LHHLL", data[:16])

        if msg_type == NLMSG_NOOP: continue
        if msg_type == NLMSG_ERROR: break

        if old_msg == msg_type: continue

        old_msg = msg_type

        # We fundamentally only care about NEWLINK messages in this version.
        #if msg_type != RTM_NEWLINK:
        if not msg_type in [RTM_NEWLINK, RTM_DELLINK, RTM_NEWADDR, RTM_DELADDR]: continue

        data = data[16:]

        family, _, if_type, index, flags, change = struct.unpack("=BBHiII", data[:16])

        remaining = msg_len - 32
        data = data[16:]

        while remaining and len(data) >= 4:
            rta_len, rta_type = struct.unpack("=HH", data[:4])

            # This check comes from RTA_OK, and terminates a string of routing attributes.
            if rta_len < 4: break

            rta_data = data[4:rta_len]

            increment = (rta_len + 4 - 1) & ~(4 - 1)
            data = data[increment:]
            remaining -= increment

	    Logger.debug('%s: %d %s' % (whoami(), msg_type, rta_data))
#           print('%s: %d %s' % (whoami(), msg_type, rta_data))

            ip = ''
            # Hoorah, a link is up!
            if msg_type == RTM_NEWLINK:
                ip = UP_TXT
		netstatus = 1
            elif msg_type == RTM_DELLINK:
                ip = DOWN_TXT
		netstatus = 0
            elif msg_type == RTM_NEWADDR:
                ip = OK_TXT
		netstatus = 1
            elif msg_type == RTM_DELADDR:
                ip = WAIT_TXT
		netstatus = 0

            if len(ip) == 0: continue

#           print('%s: %s' % (whoami(), ip))

            if rta_type == IFLA_IFNAME and msg_type in [RTM_NEWLINK, RTM_DELLINK]:
                if link_status != ip:
                    link_status = ip
		    Logger.info('%s: LINK IS %s' % (whoami(), ip))
                continue
            elif rta_type == IFLA_IFNAME:
		Logger.info('%s: IP ADDRESS IS %s' % (whoami(), ip))
                continue
