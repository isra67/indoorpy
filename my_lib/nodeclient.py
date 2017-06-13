#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################

from kivy.logger import Logger
from kivy.clock import Clock

import socket

from constants import *
from itools import *


###############################################################
#
# Declarations
#
# ###############################################################

RECONNECT_TIMER = 15

appSocket = None
address = None
server_port = None
connErr = True


# ###############################################################
#
# Functions
#
# ###############################################################

def initNodeConnection(addr='localhost', port=8123):
    "Build socket connection"
    global appSocket, server_port, address, connErr

    Logger.info('%s: %s:%d' % (whoami(), addr, port))

    address = addr
    server_port = port

    try:
	# Create a TCP/IP socket
	appSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	# Connect the socket to the port where the server is listening
	server_address = (addr, port)
	appSocket.connect(server_address)
	connErr = False
    except socket.error, e:
	connErr = True
	Logger.error('%s ERROR: %r' % (whoami(), e))
	Clock.schedule_once(lambda dt: initNodeConnection(address, server_port), RECONNECT_TIMER)


# ##############################################################################

def sendNodeInfo(msg=''):
    "Send msg to node server"
    global server_port, address, connErr

    if connErr: return
#    print('%s: %s' % (whoami(), msg))

    try:
	appSocket.sendall(msg.encode())
#	appSocket.send(msg.encode())
    except socket.error:
#	print('%s: ERROR' % (whoami()))
	connErr = True
	Clock.schedule_once(lambda dt: initNodeConnection(address, server_port), RECONNECT_TIMER)


# ##############################################################################
