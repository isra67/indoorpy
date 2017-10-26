#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################

from kivy.clock import Clock

import inspect
import os
import signal
import socket
import subprocess
import sys
import time

from omxcontrol import *
from threading import Thread

from kivy.logger import Logger

from constants import *


###############################################################
#
# Declarations
#
# ###############################################################

omxl = {}
ret_dbus = {}


# ###############################################################
#
# Functions
#
# ###############################################################

def whoami():
    "returns name of function"
    return inspect.stack()[1][3]


# ##############################################################################

def getdatetimestr():
    t = datetime.datetime.now()
    return t.strftime('%Y-%m-%d %H:%M:%S')


# ##############################################################################

def send_dbus(dst,args):
    "send DBUS command to omxplayer"
    ret_dbus[dst] = False
    t = Thread(target=send_dbus_worker, kwargs={'dst': dst, 'args': args})
    t.daemon = True
    t.start()
    t.join()
    return ret_dbus[dst]


# ##############################################################################

def send_dbus_worker(dst,args):
    "worker thread: send DBUS command to omxplayer"

    try:
	if omxl[dst] is None: omxl[dst] = OmxControl(user='root',name=dst)
    except:
	try:
	    omxl[dst] = OmxControl(user='root',name=dst)
	except:
	    Logger.warning('%s: dst=%s args=%r ERROR' % (whoami(), dst, args))
	    return True

    omx = omxl[dst]

    try:
	if args[0] == 'status':
	    Logger.info('%s: dst=%s status=%r' % (whoami(), dst, omx.status()))
	elif args[0] is 'setalpha':
#	    v = '1' if '0' is args[1] else '254'
#	    omx.setAlpha(v)
	    if '0' == args[1]: omx.action(OmxControl.ACTION_HIDE_VIDEO)
	    elif '255' == args[1]: omx.action(OmxControl.ACTION_UNHIDE_VIDEO)
	    else: omx.setAlpha(args[1])
	else:
	    omx.videoPos(args[1:])

	ret_dbus[dst] = True
	return True
    except OmxControlError as ex:
	Logger.warning('%s: dst=%s args=%r ERR=%s' % (whoami(), dst, args, ex.message))
	Logger.info('%s: dst=%s properties=%r' % (whoami(), dst, omx.properties()))

	# try to repeat command
	try:
	    time.sleep(1.5)
	    if args[0] is 'setalpha':
		if '0' == args[1]: omx.action(OmxControl.ACTION_HIDE_VIDEO)
		elif '255' == args[1]: omx.action(OmxControl.ACTION_UNHIDE_VIDEO)
		else: omx.setAlpha(args[1])
	    else:
		omx.videoPos(args[1:])

	    ret_dbus[dst] = True
	    return True
	except: pass

    return False


# ##############################################################################

def send_command(cmd):
    "send shell command"
    Logger.debug('%s: cmd=%s' % (whoami(), cmd))
    try:
        os.system(cmd)
    except:
	pass


# ###############################################################

def get_info(cmd):
    "get information from shell script"
    proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, shell=False)
    (out, err) = proc.communicate()
    Logger.debug('%s: cmd=%s out=%s (err=%s)' % (whoami(), cmd, out, str(err)))
    return out


# ##############################################################################

def getINet():
    "check the Internet connection"
    return True		### stop checking

    info = '0'

    try: info = get_info('./checkinet.sh')
    except: pass

    return True if '1' in info else False


# ##############################################################################

