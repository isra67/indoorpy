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
    print whoami(), PHONERING_PLAYER
#    send_command(PHONERING_PLAYER)
    subprocess.Popen(PHONERING_PLAYER.split())


# ##############################################################################

def stopWAV():
    "stop play"
    send_command('pkill -9 ' + APLAYER)


# ##############################################################################

def send_dbus(dst,args):
    "send DBUS command to omxplayer"

#    subprocess.Popen([DBUSCONTROL_SCRIPT, dst] + args)
#    return True

    try:
	proc = subprocess.check_output([DBUSCONTROL_SCRIPT, dst] + args) #, stderr=subprocess.STDOUT, shell=False)
	# do something with output
	print whoami(), dst,args, ':', 'out:',proc

	time.sleep(0.1)
    except subprocess.CalledProcessError as e:
        print whoami(), dst,args, ':', 'ERR:',e.output
	return False

    return True


# ##############################################################################

def send_command(cmd):
    "send shell command"
    print whoami(),':', cmd
    try:
        os.system(cmd)
    except:
	pass


# ###############################################################

def get_info(cmd):
    "get information from shell script"
    proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, shell=False)
    (out, err) = proc.communicate()
    print whoami(), cmd, ':', out, err
    return out


# ##############################################################################

