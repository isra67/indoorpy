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

app_status = {'VIDEO':{},'LOCK':{}}	# struct to save app status


# ###############################################################
#
# Functions
#
# ###############################################################

def initNodeConnection(addr='localhost', port=8123):
    "Build socket connection"
    global appSocket, server_port, address, connErr, app_status

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
	Clock.schedule_once(lambda dt: sendNodeInfo('STRUCT:%r' % app_status), 10)
    except socket.error, e:
	connErr = True
	Logger.error('%s ERROR: %r' % (whoami(), e))
	Clock.schedule_once(lambda dt: initNodeConnection(address, server_port), RECONNECT_TIMER)


# ##############################################################################

def sendNodeInfo(msg=''):
    "Send msg to node server"
    global server_port, address, connErr

    if '[***]' in msg:
	statusInfo(msg[5:])
    else:
	if 'STRUCT:' in msg: msg = '[***]%s' % msg

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

def statusInfo(info):
    "put info to the status struct"
    global app_status

    try:
	a = info.split(':', 2)
	if len(a) > 1:
	    a[0] = a[0].strip()
	    #if a[0][0] == 'u': a[0] = a[0][1:]
	    a[1] = a[1].strip()
	    #if a[1][0] == 'u': a[1] = a[1][1:]
	    if 'LOCK' in a[0] or 'VIDEO' in a[0]:
		b = a[1].strip().split(' ', 2)
		if len(b) > 1: app_status[a[0]][b[0]] = b[1].strip()
		else: app_status[a[0]] = a[1]
	    else:
		app_status[a[0]] = a[1]
    except: pass

    Logger.trace('%s: %r' % (whoami(), app_status))


# ##############################################################################
