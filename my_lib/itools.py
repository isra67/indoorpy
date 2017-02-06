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

#CMD_KILL = 'kill -9 '

#CONFIG_FILE = 'indoor.ini'

#SCREEN_SAVER = 0
#BACK_LIGHT = False
#BRIGHTNESS = 100
#WATCHES = 'analog'

#DBUSCONTROL_SCRIPT = './dbuscntrl.sh'
#BACK_LIGHT_SCRIPT = './backlight.sh'
#UNBLANK_SCRIPT = './unblank.sh'
#BRIGHTNESS_SCRIPT = './brightness.sh'
#SYSTEMINFO_SCRIPT = './sysinfo.sh'

#APLAYER = 'aplay'
#APARAMS = '-q -N -f cd -D plughw:0,0'
#RING_WAV = APLAYER + ' ' + APARAMS + ' ' +'share/sounds/linphone/rings/oldphone.wav &'

#TRANSPARENCY_VIDEO_CMD = ['setalpha']

#DBUS_PLAYERNAME = 'org.mpris.MediaPlayer2.omxplayer'


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
    send_command(RING_WAV)


# ##############################################################################

def stopWAV():
    "stop play"
    send_command('pkill -9 ' + APLAYER)


# ##############################################################################

def send_dbus(dst,args):
    "send DBUS command to omxplayer"

    try:
	proc = subprocess.check_output([DBUSCONTROL_SCRIPT, dst] + args, stderr=subprocess.STDOUT)
	# do something with output
	print whoami(), dst,args, ':', 'out:',proc

	time.sleep(0.05)
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
    proc = subprocess.Popen(cmd.split(), stdout=subprocess.PIPE, shell=True)
    (out, err) = proc.communicate()
    print whoami(), cmd, ':', out, err
    return out


# ##############################################################################

