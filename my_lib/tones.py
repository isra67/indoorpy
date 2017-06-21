#!/bin/python

# ###############################################################
#
# Imports
#
# ###############################################################

from kivy.clock import Clock

import os
import subprocess
import sys
import time


from kivy.logger import Logger

from constants import *
from itools import *


###############################################################
#
# Declarations
#
# ###############################################################

PHONERING_PLAYER = APLAYER + ' ' + APARAMS + RING_TONE


# ###############################################################
#
# Functions
#
# ###############################################################

def ringingTones():
    "get list of ringing tones"

    Logger.debug('%s:' % whoami())

    tones = []
    try: dirs = os.listdir('sounds/')
    except: dirs = []

    # This would print all the files and directories
    for file in dirs:
	if 'ring_' in file:
	    tones.append(file)

    return tones


# ##############################################################################

def delCustomRingingTones():
    "delete customer's ringing tones"

    Logger.debug('%s:' % whoami())

    try: dirs = os.listdir('sounds/')
    except: dirs = []

    # This would print all the files and directories
    for file in dirs:
	if 'ring_' in file:
	    try: os.remove('sounds/' + file)
	    except: pass


# ##############################################################################

def playTone(tone):
    "start play"

#    stopWAV()

    Logger.debug('%s: %s' %(whoami(), tone))
###    send_command(PHONERING_PLAYER)
##    send_command(tone)
    subprocess.Popen(tone.split())
    #Clock.schedule_once(lambda dt: subprocess.Popen(tone.split()), .5)
#    Clock.schedule_once(lambda dt: send_command(tone))


# ##############################################################################

def playWAV(dt):
    "start play ringing task"
#    Logger.debug('%s: %s' %(whoami(), PHONERING_PLAYER))
#    subprocess.Popen(PHONERING_PLAYER.split())
    playTone(PHONERING_PLAYER)


# ##############################################################################

def stopWAV():
    "stop play"
    Logger.debug('%s: ' % whoami())
    send_command('pkill -9 ' + APLAYER)


# ##############################################################################
