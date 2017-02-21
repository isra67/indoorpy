#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################


import inspect
import os
import signal
import socket
import subprocess
import sys
import time

from kivy.logger import Logger


from constants import *

###############################################################
#
# Declarations
#
# ###############################################################

#APLAYER = 'aplay'
#APARAMS = '-q -N -f cd -D plughw:0,0'
#RING_WAV = APLAYER + ' ' + APARAMS + ' ' +'share/sounds/linphone/rings/oldphone.wav &'

PHONERING_PLAYER = APLAYER + ' ' + APARAMS + RING_TONE  #'aplay -q -N -f cd -D plughw:0,0 sounds/oldphone.wav'


# ###############################################################
#
# Functions
#
# ###############################################################

def whoami():
    "returns name of function"
    return inspect.stack()[1][3]


# ##############################################################################

def playWAV(dt):
    "start play"
    Logger.debug(whoami()+': '+ PHONERING_PLAYER)
#    send_command(PHONERING_PLAYER)
    subprocess.Popen(PHONERING_PLAYER.split())


# ##############################################################################

def stopWAV():
    "stop play"
    Logger.debug(whoami()+': ')
    send_command('pkill -9 ' + APLAYER)


# ##############################################################################

def send_dbus(dst,args):
    "send DBUS command to omxplayer"

#    subprocess.Popen([DBUSCONTROL_SCRIPT, dst] + args)
#    return True

    try:
	proc = subprocess.check_output([DBUSCONTROL_SCRIPT, dst] + args) #, stderr=subprocess.STDOUT, shell=False)
	# do something with output
	Logger.debug(whoami()+': dst=%s args=[%s] out=%s' % (dst, ','.join(args), proc))
#	time.sleep(0.12)
    except subprocess.CalledProcessError, e:
	Logger.warning(whoami()+': dst=%s args=[%s] ERR=%s' % (dst, ','.join(args), e.output))
	return False

    return True


# ##############################################################################

def send_command(cmd):
    "send shell command"
    Logger.debug(whoami()+': cmd=%s' % (cmd))
    try:
        os.system(cmd)
    except:
	pass


# ###############################################################

def get_info(cmd):
    "get information from shell script"
    proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, shell=False)
    (out, err) = proc.communicate()
    Logger.debug(whoami()+': cmd=%s out=%s (err=%s)' % (cmd, out, err))
    return out


# ##############################################################################

