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

from kivy.logger import Logger

from constants import *


###############################################################
#
# Declarations
#
# ###############################################################

omxl = {}


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
##    return send_dbus_old(dst,args)
#    Logger.info('%s: dst=%s args=%s' % (whoami(), dst, str(args)))

    try:
	if omxl[dst] is None: omxl[dst] = OmxControl(user='root',name=dst)
    except:
	omxl[dst] = OmxControl(user='root',name=dst)

    omx = omxl[dst]

    try:
	if args[0] is 'setalpha':
#	    v = '1' if '0' is args[1] else '254'
#	    omx.setAlpha(v)
	    if '0' == args[1]: omx.action(OmxControl.ACTION_HIDE_VIDEO)
	    elif '255' == args[1]: omx.action(OmxControl.ACTION_UNHIDE_VIDEO)
	    else: omx.setAlpha(args[1])
	else:
	    omx.videoPos(args[1:])
    except OmxControlError as ex:
	Logger.warning('%s: dst=%s args=%s ERR=%s' % (whoami(), dst, str(args), ex.message))
	return False

    return True


# ##############################################################################

def send_command(cmd):
    "send shell command"
    Logger.info('%s: cmd=%s' % (whoami(), cmd))
    try:
        os.system(cmd)
    except:
	pass


# ###############################################################

def get_info(cmd):
    "get information from shell script"
    proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, shell=False)
    (out, err) = proc.communicate()
    Logger.info('%s: cmd=%s out=%s (err=%s)' % (whoami(), cmd, out, str(err)))
    return out


# ##############################################################################
