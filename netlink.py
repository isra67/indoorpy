import os
import socket
import struct

from my_lib import *

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

# Create the netlink socket and bind to RTMGRP_LINK
s = socket.socket(socket.AF_NETLINK, socket.SOCK_RAW, socket.NETLINK_ROUTE)
#s.bind((os.getpid(), RTMGRP_LINK))
#s.bind((0, RTMGRP_LINK | RTMGRP_IPV4_IFADDR))
s.bind((0, -1))

while True:
    data = s.recv(65535)
    msg_len, msg_type, flags, seq, pid = struct.unpack("=LHHLL", data[:16])

    if msg_type == NLMSG_NOOP:
#        print "no-op"
        continue
    elif msg_type == NLMSG_ERROR:
#        print "error"
        break

    # We fundamentally only care about NEWLINK messages in this version.
#    if msg_type != RTM_NEWLINK:
    if not (msg_type == RTM_NEWLINK or msg_type == RTM_DELLINK or msg_type == RTM_NEWADDR or msg_type == RTM_DELADDR):
	continue

    data = data[16:]

    family, _, if_type, index, flags, change = struct.unpack("=BBHiII", data[:16])
#    print family, if_type, index, flags, change

    remaining = msg_len - 32
    data = data[16:]

    while remaining and len(data) >= 4:
        rta_len, rta_type = struct.unpack("=HH", data[:4])

        # This check comes from RTA_OK, and terminates a string of routing attributes
        if rta_len < 4: break

        rta_data = data[4:rta_len]

        increment = (rta_len + 4 - 1) & ~(4 - 1)
        data = data[increment:]
        remaining -= increment

	if not (msg_type == RTM_NEWLINK or msg_type == RTM_NEWADDR): continue

        # Hoorah, a link is up!
        if rta_type == IFLA_IFNAME:
	    t = "New link %s" % rta_data
#            print "New link %s" % rta_data
	    send_command('echo %s' % t)
	    send_command('./killme.sh')

        # Hoorah, a link have an address!
        if rta_type == IFLA_ADDRESS:
#            print "New address %s" % rta_data
	    send_command('./killme.sh')
